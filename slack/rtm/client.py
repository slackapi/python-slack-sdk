"""A Python module for iteracting with Slack's RTM API."""

# Standard Imports
import os
import logging
import random
import json
import collections
import functools
import inspect
import signal

# ThirdParty Imports
import asyncio
import websockets
import websockets.exceptions as socket_err

# Internal Imports
from slack.web.client import WebClient
import slack.errors as client_err


class RTMClient(object):
    """An RTMClient allows apps to communicate with the Slack Platform's RTM API.

    The event-driven architecture of this client allows you to simply
    link callbacks to their corresponding events. When an event occurs
    this client executes your callback while passing along any
    information it receives.

    Attributes:
        token (str): A string specifying an xoxp or xoxb token.
        connect_method (str): An string specifying if the client
            will connect with `rtm.connect` or `rtm.start`.
            Default is `rtm.connect`.
        auto_reconnect (bool): When true the client will automatically
            reconnect when (not manually) disconnected. Default is True.
        ping_interval (int): automatically send "ping" command every
            specified period of seconds. If set to 0, do not send automatically.
            Default is 30.
        ping_timeout (int): The amount of seconds the ping should timeout.
            If the pong message is not received. Default is 30.
        ssl (SSLContext): The SSLContext object to be used.
        proxies (dict): If you need to use a proxy, you can pass a dict
            of proxy configs. e.g. {'https': "https://user:pass@127.0.0.1:8080"}
            Default is None.
        loop (AbstractEventLoop): An event loop provided by asyncio.
            If None is specified we attempt to use the current loop
            with `get_event_loop`. Default is None.

    Methods:
        ping: Sends a ping message over the websocket to Slack.
        typing: Sends a typing indicator to the specified channel.
        on: Stores and links callbacks to websocket and Slack events.
        start: Starts an RTM Session with Slack.
        stop: Closes the websocket connection and ensures it won't reconnect.

    Example:
    ```python
    import slack

    @slack.RTMClient.run_on(event='message')
    def say_hello(**payload):
        data = payload['data']
        web_client = payload['web_client']
        rtm_client = payload['rtm_client']
        if 'Hello' in data['text']:
            channel_id = data['channel']
            thread_ts = data['ts']
            user = data['user']

            web_client.chat_postMessage(
                channel=channel_id,
                text=f"Hi <@{user}>!",
                thread_ts=thread_ts
            )

    slack_token = os.environ["SLACK_API_TOKEN"]
    rtm_client = slack.RTMClient(slack_token)
    rtm_client.start()
    ```

    Note:
        The initial state returned when establishing an RTM connection will
        be available as the data in payload for the 'open' event. This data is not and
        will not be stored on the RTM Client.

        Any attributes or methods prefixed with _underscores are
        intended to be "private" internal use only. They may be changed or
        removed at anytime.
    """

    _callbacks = collections.defaultdict(list)

    def __init__(
        self,
        token=None,
        base_url=WebClient.BASE_URL,
        connect_method=None,
        auto_reconnect=True,
        ping_interval=30,
        ping_timeout=30,
        ssl=None,
        proxies=None,
        loop=None,
    ):
        self.token = token
        self.base_url = base_url
        self.connect_method = connect_method
        self.auto_reconnect = auto_reconnect
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.ssl = ssl
        self.proxies = proxies
        self._web_client = WebClient(
            token=self.token, base_url=self.base_url, proxies=self.proxies
        )
        self._websocket = None
        self._logger = logging.getLogger(__name__)
        self._last_message_id = 0
        self._connection_attempts = 0
        self._stopped = False
        self._event_loop = loop or asyncio.get_event_loop()

    @staticmethod
    def run_on(event):
        """A decorator to store and link a callback to an event."""

        def decorator(callback):
            @functools.wraps(callback)
            def decorator_wrapper():
                RTMClient.on(event, callback)

            return decorator_wrapper()

        return decorator

    @classmethod
    def on(cls, event, callback):
        """Stores and links the callback(s) to the event.

        Args:
            event (str): A string that specifies a Slack or websocket event.
                e.g. 'channel_joined' or 'open'
            callback (obj): Any object or a list of objects that can be called.
                e.g. <function say_hello at 0x101234567> or
                [<function say_hello at 0x10123>,<function say_bye at 0x10456>]

        Raises:
            SlackClientError: The specified callback is not callable.
            SlackClientError: The callback must accept keyword arguments (**kwargs).
        """
        if isinstance(callback, list):
            for cb in callback:
                cls._validate_callback(cb)
            previous_callbacks = cls._callbacks[event]
            cls._callbacks[event] = list(set(previous_callbacks + callback))
        else:
            cls._validate_callback(callback)
            cls._callbacks[event].append(callback)

    def start(self):
        """Starts an RTM Session with Slack.

        Makes an authenticated call to Slack's RTM API to retrieve
        a websocket URL and then connects to the message server.
        As events stream-in we run any associated callbacks stored
        on the client.

        If 'auto_reconnect' is specified we
        retrieve a new url and reconnect any time the connection
        is lost unintentionally or an exception is thrown.

        Raises:
            SlackApiError: Unable to retreive RTM URL from Slack.
        """
        try:
            # TODO: Add Windows support for graceful shutdowns.
            if os.name != "nt":
                signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
                for s in signals:
                    self._event_loop.add_signal_handler(s, self.stop)
            self._event_loop.run_until_complete(self._connect_and_read())
        finally:
            self._dispatch_event(event="close")

    def stop(self):
        """Closes the websocket connection and ensures it won't reconnect."""
        self._logger.debug("The Slack RTMClient is shutting down.")
        self._stopped = True
        self._close_websocket()

    def send_over_websocket(self, payload):
        """Sends a message to Slack over the WebSocket connection.

        Note:
            The RTM API only supports posting simple messages formatted using
            our default message formatting mode. It does not support
            attachments or other message formatting modes. For this reason
            we recommend users send messages via the Web API methods.
            e.g. web_client.chat_postMessage()

        Args:
            payload (dict): The message to send over the wesocket.
            e.g.
            {
                "id": 1,
                "type": "typing",
                "channel": "C024BE91L"
            }

        Raises:
            SlackClientError: Websocket connection is closed.
        """
        if self._websocket is None or self._event_loop is None:
            raise client_err.SlackClientError("Websocket connection is closed.")
        asyncio.ensure_future(
            self._websocket.send(json.dumps(payload)), loop=self._event_loop
        )

    def ping(self):
        """Sends a ping message over the websocket to Slack.

        Not all web browsers support the WebSocket ping spec,
        so the RTM protocol also supports ping/pong messages.

        Raises:
            SlackClientError: Websocket connection is closed.
        """
        payload = {"id": self._next_msg_id(), "type": "ping"}
        self.send_over_websocket(payload=payload)

    def typing(self, channel):
        """Sends a typing indicator to the specified channel.

        This indicates that this app is currently
        writing a message to send to a channel.

        Args:
            channel (str): The channel id. e.g. 'C024BE91L'

        Raises:
            SlackClientError: Websocket connection is closed.
        """
        payload = {"id": self._next_msg_id(), "type": "typing", "channel": channel}
        self.send_over_websocket(payload=payload)

    @staticmethod
    def _validate_callback(callback):
        """Checks if the specified callback is callable and accepts a kwargs param.

        Args:
            callback (obj): Any object or a list of objects that can be called.
                e.g. <function say_hello at 0x101234567>

        Raises:
            SlackClientError: The specified callback is not callable.
            SlackClientError: The callback must accept keyword arguments (**kwargs).
        """

        cb_name = callback.__name__ if hasattr(callback, "__name__") else callback
        if not callable(callback):
            msg = "The specified callback '{}' is not callable.".format(cb_name)
            raise client_err.SlackClientError(msg)
        callback_params = inspect.signature(callback).parameters.values()
        if not any(
            param for param in callback_params if param.kind == param.VAR_KEYWORD
        ):
            msg = "The callback '{}' must accept keyword arguments (**kwargs).".format(
                cb_name
            )
            raise client_err.SlackClientError(msg)

    def _next_msg_id(self):
        """Retrieves the next message id.

        When sending messages to Slack every event should
        have a unique (for that connection) positive integer ID.

        Returns:
            An integer representing the message id. e.g. 98
        """
        self._last_message_id += 1
        return self._last_message_id

    async def _connect_and_read(self):
        """Retreives and connects to Slack's RTM API.

        Makes an authenticated call to Slack's RTM API to retrieve
        a websocket URL. Then connects to the message server and
        reads event messages as they come in.

        If 'auto_reconnect' is specified we
        retrieve a new url and reconnect any time the connection
        is lost unintentionally or an exception is thrown.

        Raises:
            SlackApiError: Unable to retreive RTM URL from Slack.
            websockets.exceptions: Errors thrown by the 'websockets' library.
        """
        while not self._stopped:
            try:
                self._connection_attempts += 1
                url, data = self._retreive_websocket_info()
                async with websockets.connect(
                    url,
                    ping_interval=self.ping_interval,
                    ping_timeout=self.ping_timeout,
                    loop=self._event_loop,
                    ssl=self.ssl,
                ) as websocket:
                    self._logger.debug("The Websocket connection has been opened.")
                    self._websocket = websocket
                    self._dispatch_event(event="open", data=data)
                    await self._read_messages()
            except (
                client_err.SlackApiError,
                socket_err.InvalidState,
                socket_err.InvalidHandshake,
            ) as exception:
                self._logger.debug(str(exception))
                self._dispatch_event(event="error", data=exception)
                if self.auto_reconnect and not self._stopped:
                    await self._wait_exponentially(exception)
                    continue
                self._logger.exception(
                    "The Websocket encountered an error. Closing the connection..."
                )
                self._close_websocket()
                raise

    async def _read_messages(self):
        """Process messages received on the WebSocket connection.

        Iteration terminates when the client is stopped or it disconnects.
        """
        while not self._stopped:
            async for message in self._websocket:
                payload = json.loads(message)
                self._logger.debug(f"The Websocket received a new message. {payload}")
                event = payload.pop("type", "Unknown")
                self._dispatch_event(event, data=payload)

    def _dispatch_event(self, event, data=None):
        """Dispatches the event and executes any associated callbacks.

        Note: To prevent the app from crashing due to callback errors. We
        catch all exceptions and send all data to the logger.

        Args:
            event (str): The type of event. e.g. 'bot_added'
            data (dict): The data Slack sent. e.g.
            {
                "type": "bot_added",
                "bot": {
                    "id": "B024BE7LH",
                    "app_id": "A4H1JB4AZ",
                    "name": "hugbot"
                }
            }
        """
        self._logger.debug(
            "Running %s callbacks for event: '%s'", len(self._callbacks[event]), event
        )
        for callback in self._callbacks[event]:
            try:
                if self._stopped and event not in ["close", "error"]:
                    # Don't run callbacks if client was stopped unless they're close/error callbacks.
                    break
                callback(rtm_client=self, web_client=self._web_client, data=data)
            except Exception as err:
                name = callback.__name__
                module = callback.__module__
                msg = f"When calling '{module}#{name}()' the following error was raised: {err}"
                raise client_err.CallbackError(msg) from err

    def _retreive_websocket_info(self):
        """Retreives the WebSocket info from Slack.

        Returns:
            A tuple of websocket information.
            e.g.
            (
                "wss://...",
                {
                    "self": {"id": "U4X318ZMZ","name": "robotoverlord"},
                    "team": {
                        "domain": "slackdemo",
                        "id": "T2U81E2FP",
                        "name": "SlackDemo"
                    }
                }
            )

        Raises:
            SlackApiError: Unable to retreive RTM URL from Slack.
        """
        self._logger.debug("Retrieving websocket info.")
        if self.connect_method in ["rtm.start", "rtm_start"]:
            resp = self._web_client.rtm_start()
        else:
            resp = self._web_client.rtm_connect()
        url = resp.get("url")
        if url is None:
            msg = "Unable to retreive RTM URL from Slack."
            raise client_err.SlackApiError(message=msg, response=resp)
        return url, resp.data

    async def _wait_exponentially(self, exception, max_wait_time=300):
        """Wait exponentially longer for each connection attempt.

        Calculate the number of seconds to wait and then add
        a random number of milliseconds to avoid coincendental
        synchronized client retries. Wait up to the maximium amount
        of wait time specified via 'max_wait_time'. However,
        if Slack returned how long to wait use that.
        """
        wait_time = min(
            (2 ** self._connection_attempts) + random.random(), max_wait_time
        )
        try:
            wait_time = exception.response["headers"]["Retry-After"]
        except (KeyError, AttributeError):
            pass
        self._logger.debug("Waiting %s seconds before reconnecting.", wait_time)
        await asyncio.sleep(float(wait_time))

    def _close_websocket(self):
        """Closes the websocket connection."""
        close_method = getattr(self._websocket, "close", None)
        if callable(close_method):
            asyncio.ensure_future(close_method(), loop=self._event_loop)
        self._websocket = None
