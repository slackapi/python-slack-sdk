"""A Python module for iteracting with Slack's Web API."""

# Standard Imports
from urllib.parse import urljoin
import platform
import sys
import logging
import asyncio
import inspect

# ThirdParty Imports
import aiohttp

# Internal Imports
from slack.web.slack_response import SlackResponse
import slack.version as ver
import slack.errors as err


class BaseClient:
    BASE_URL = "https://www.slack.com/api/"

    def __init__(
        self,
        token,
        base_url=BASE_URL,
        timeout=30,
        loop=None,
        ssl=None,
        proxy=None,
        run_async=False,
        session=None,
    ):
        self.token = token
        self.base_url = base_url
        self.timeout = timeout
        self.ssl = ssl
        self.proxy = proxy
        self.run_async = run_async
        self.session = session
        self._logger = logging.getLogger(__name__)
        self._event_loop = loop

    def _set_event_loop(self):
        if self.run_async:
            self._event_loop = asyncio.get_event_loop()
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._event_loop = loop

    def api_call(
        self,
        api_method: str,
        *,
        http_verb: str = "POST",
        files: dict = None,
        data: dict = None,
        params: dict = None,
        json: dict = None,
    ):
        """Create a request and execute the API call to Slack.

        Args:
            api_method (str): The target Slack API method.
                e.g. 'chat.postMessage'
            http_verb (str): HTTP Verb. e.g. 'POST'
            files (dict): Files to multipart upload.
                e.g. {imageORfile: file_objectORfile_path}
            data: The body to attach to the request. If a dictionary is
                provided, form-encoding will take place.
                e.g. {'key1': 'value1', 'key2': 'value2'}
            params (dict): The URL parameters to append to the URL.
                e.g. {'key1': 'value1', 'key2': 'value2'}
            json (dict): JSON for the body to attach to the request
                (if files or data is not specified).
                e.g. {'key1': 'value1', 'key2': 'value2'}

        Returns:
            (SlackResponse)
                The server's response to an HTTP request. Data
                from the response can be accessed like a dict.
                If the response included 'next_cursor' it can
                be iterated on to execute subsequent requests.

        Raises:
            SlackApiError: The following Slack API call failed:
                'chat.postMessage'.
            SlackRequestError: Json data can only be submitted as
                POST requests.
        """
        if json is not None and http_verb != "POST":
            msg = "Json data can only be submitted as POST requests. GET requests should use the 'params' argument."
            raise err.SlackRequestError(msg)

        api_url = self._get_url(api_method)
        headers = {
            "User-Agent": self._get_user_agent(),
            "Authorization": "Bearer {}".format(self.token),
        }
        if files is not None:
            form_data = aiohttp.FormData()
            for k, v in files.items():
                if isinstance(v, str):
                    form_data.add_field(k, open(v, "rb"))
                else:
                    form_data.add_field(k, v)

            if data is not None:
                for k, v in data.items():
                    form_data.add_field(k, str(v))

            data = form_data

        req_args = {
            "headers": headers,
            "data": data,
            "params": params,
            "json": json,
            "ssl": self.ssl,
            "proxy": self.proxy,
        }

        if self._event_loop is None:
            self._set_event_loop()

        future = asyncio.ensure_future(
            self._send(http_verb=http_verb, api_url=api_url, req_args=req_args),
            loop=self._event_loop,
        )

        if self.run_async:
            return future

        return self._event_loop.run_until_complete(future)

    def _validate_xoxp_token(self):
        """Ensures that an xoxp token is used when the specified method is called.

        Raises:
            BotUserAccessError: If the API method is called with a Bot User OAuth Access Token.
        """

        if self.token.startswith("xoxb"):
            method_name = inspect.stack()[1][3]
            msg = "The method '{}' cannot be called with a Bot Token.".format(
                method_name
            )
            raise err.BotUserAccessError(msg)

    def _get_url(self, api_method):
        """Joins the base Slack URL and an API method to form an absolute URL.

        Args:
            api_method (str): The Slack Web API method. e.g. 'chat.postMessage'

        Returns:
            The absolute API URL.
                e.g. 'https://www.slack.com/api/chat.postMessage'
        """
        return urljoin(self.base_url, api_method)

    async def _send(self, http_verb, api_url, req_args):
        """Sends the request out for transmission.

        Args:
            http_verb (str): The HTTP verb. e.g. 'GET' or 'POST'.
            api_url (str): The Slack API url. e.g. 'https://slack.com/api/chat.postMessage'
            req_args (dict): The request arguments to be attached to the request.
            e.g.
            {
                json: {
                    'attachments': [{"pretext": "pre-hello", "text": "text-world"}],
                    'channel': '#random'
                }
            }
        Returns:
            The response parsed into a SlackResponse object.
        """
        res = await self._request(
            http_verb=http_verb, api_url=api_url, req_args=req_args
        )
        data = {
            "client": self,
            "http_verb": http_verb,
            "api_url": api_url,
            "req_args": req_args,
        }
        return SlackResponse(**{**data, **res}).validate()

    async def _request(self, *, http_verb, api_url, req_args):
        """Submit the HTTP request with the running session or a new session.
        Returns:
            A dictionary of the response data.
        """
        if self.session and not self.session.closed:
            async with self.session.request(http_verb, api_url, **req_args) as res:
                self._logger.debug("Ran the request with existing session.")
                return {
                    "data": await res.json(),
                    "headers": res.headers,
                    "status_code": res.status,
                }
        async with aiohttp.ClientSession(
            loop=self._event_loop, timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            async with session.request(http_verb, api_url, **req_args) as res:
                self._logger.debug("Ran the request with a new session.")
                return {
                    "data": await res.json(),
                    "headers": res.headers,
                    "status_code": res.status,
                }

    @staticmethod
    def _get_user_agent():
        """Construct the user-agent header with the package info,
        Python version and OS version.

        Returns:
            The user agent string.
            e.g. 'Python/3.6.7 slack/2.0.0 Darwin/17.7.0'
        """
        # __name__ returns all classes, we only want the client
        client = "{0}/{1}".format(__name__.split(".")[0], ver.__version__)
        python_version = "Python/{v.major}.{v.minor}.{v.micro}".format(
            v=sys.version_info
        )
        system_info = "{0}/{1}".format(platform.system(), platform.release())
        user_agent_string = " ".join([python_version, client, system_info])
        return user_agent_string
