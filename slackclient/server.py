from .slackrequest import SlackRequest
from requests.packages.urllib3.util.url import parse_url
from .channel import Channel
from .user import User
from .util import SearchList, SearchDict
from .exceptions import SlackClientError
from ssl import SSLError

from websocket import create_connection
import json


class Server(object):
    '''
    The Server object owns the websocket connection and all attached channel information.


    '''
    def __init__(self, token, connect=True, proxies=None):
        self.token = token
        self.username = None
        self.domain = None
        self.login_data = None
        self.websocket = None
        self.users = SearchDict()
        self.channels = SearchList()
        self.connected = False
        self.ws_url = None
        self.proxies = proxies
        self.api_requester = SlackRequest(proxies=proxies)

        if connect:
            self.rtm_connect()

    def __eq__(self, compare_str):
        if compare_str == self.domain or compare_str == self.token:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.token)

    def __str__(self):
        '''
        Example Output::

        username : None
        domain : None
        websocket : None
        users : []
        login_data : None
        api_requester : <slackclient.slackrequest.SlackRequest
        channels : []
        token : xoxb-asdlfkyadsofii7asdf734lkasdjfllakjba7zbu
        connected : False
        ws_url : None
        '''
        data = ""
        for key in list(self.__dict__.keys()):
            data += "{} : {}\n".format(key, str(self.__dict__[key])[:40])
        return data

    def __repr__(self):
        return self.__str__()

    def append_user_agent(self, name, version):
        self.api_requester.append_user_agent(name, version)

    def rtm_connect(self, reconnect=False, timeout=None, use_rtm_start=True, **kwargs):
        # rtm.start returns user and channel info, rtm.connect does not.
        connect_method = "rtm.start" if use_rtm_start else "rtm.connect"
        reply = self.api_requester.do(self.token, connect_method, timeout=timeout, post_data=kwargs)

        if reply.status_code != 200:
            raise SlackConnectionError(reply=reply)
        else:
            login_data = reply.json()
            if login_data["ok"]:
                self.ws_url = login_data['url']
                self.connect_slack_websocket(self.ws_url)
                if not reconnect:
                    self.parse_slack_login_data(login_data, use_rtm_start)
            else:
                raise SlackLoginError(reply=reply)

    def parse_slack_login_data(self, login_data, use_rtm_start):
        self.login_data = login_data
        self.domain = self.login_data["team"]["domain"]
        self.username = self.login_data["self"]["name"]

        # if the connection was made via rtm.start, update the server's state
        if use_rtm_start:
            self.parse_channel_data(login_data["channels"])
            self.parse_channel_data(login_data["groups"])
            self.parse_user_data(login_data["users"])
            self.parse_channel_data(login_data["ims"])

    def connect_slack_websocket(self, ws_url):
        """Uses http proxy if available"""
        if self.proxies and 'http' in self.proxies:
            parts = parse_url(self.proxies['http'])
            proxy_host, proxy_port = parts.host, parts.port
            auth = parts.auth
            proxy_auth = auth and auth.split(':')
        else:
            proxy_auth, proxy_port, proxy_host = None, None, None

        try:
            self.websocket = create_connection(ws_url,
                                               http_proxy_host=proxy_host,
                                               http_proxy_port=proxy_port,
                                               http_proxy_auth=proxy_auth)
            self.websocket.sock.setblocking(0)
        except Exception as e:
            raise SlackConnectionError(message=str(e))

    def parse_channel_data(self, channel_data):
        for channel in channel_data:
            if "name" not in channel:
                channel["name"] = channel["id"]
            if "members" not in channel:
                channel["members"] = []
            self.attach_channel(channel["name"],
                                channel["id"],
                                channel["members"])

    def parse_user_data(self, user_data):
        for user in user_data:
            if "tz" not in user:
                user["tz"] = "unknown"
            if "real_name" not in user:
                user["real_name"] = user["name"]
            if "email" not in user["profile"]:
                user["profile"]["email"] = ""
            self.attach_user(user["name"],
                             user["id"],
                             user["real_name"],
                             user["tz"],
                             user["profile"]["email"])

    def send_to_websocket(self, data):
        """
        Send a JSON message directly to the websocket. See
        `RTM documentation <https://api.slack.com/rtm` for allowed types.

        :Args:
            data (dict) the key/values to send the websocket.

        """
        try:
            data = json.dumps(data)
            self.websocket.send(data)
        except Exception:
            self.rtm_connect(reconnect=True)

    def rtm_send_message(self, channel, message, thread=None, reply_broadcast=None):
        '''
        Sends a message to a given channel.

        :Args:
            channel (str) - the string identifier for a channel or channel name (e.g. 'C1234ABC',
            'bot-test' or '#bot-test')
            message (message) - the string you'd like to send to the channel
            thread (str or None) - the parent message ID, if sending to a
                thread
            reply_broadcast (bool) - if messaging a thread, whether to
                also send the message back to the channel

        :Returns:
            None

        '''
        message_json = {"type": "message", "channel": channel, "text": message}
        if thread is not None:
            message_json["thread_ts"] = thread
            if reply_broadcast:
                message_json['reply_broadcast'] = True

        self.send_to_websocket(message_json)

    def ping(self):
        return self.send_to_websocket({"type": "ping"})

    def websocket_safe_read(self):
        """ Returns data if available, otherwise ''. Newlines indicate multiple
            messages
        """

        data = ""
        while True:
            try:
                data += "{0}\n".format(self.websocket.recv())
            except SSLError as e:
                if e.errno == 2:
                    # errno 2 occurs when trying to read or write data, but more
                    # data needs to be received on the underlying TCP transport
                    # before the request can be fulfilled.
                    #
                    # Python 2.7.9+ and Python 3.3+ give this its own exception,
                    # SSLWantReadError
                    return ''
                raise
            return data.rstrip()

    def attach_user(self, name, user_id, real_name, tz, email):
        self.users.update({user_id: User(self, name, user_id, real_name, tz, email)})

    def attach_channel(self, name, channel_id, members=None):
        if members is None:
            members = []
        if self.channels.find(channel_id) is None:
            self.channels.append(Channel(self, name, channel_id, members))

    def join_channel(self, name, timeout=None):
        '''
        Join a channel by name.

        Note: this action is not allowed by bots, they must be invited to channels.
        '''
        return self.api_requester.do(
            self.token,
            "channels.join?name={}".format(name),
            timeout=timeout
        ).text

    def api_call(self, method, timeout=None, **kwargs):
        '''
        Call the Slack Web API as documented here: https://api.slack.com/web

        :Args:
            method (str): The API Method to call. See here for a list: https://api.slack.com/methods
        :Kwargs:
            (optional) timeout: stop waiting for a response after a given number of seconds
            (optional) kwargs: any arguments passed here will be bundled and sent to the api
            requester as post_data
                and will be passed along to the API.

        Example::

            sc.server.api_call(
                "channels.setPurpose",
                channel="CABC12345",
                purpose="Writing some code!"
            )

        Returns:
            str -- returns the text of the HTTP response.

            Examples::

                u'{"ok":true,"purpose":"Testing bots"}'
                or
                u'{"ok":false,"error":"channel_not_found"}'

            See here for more information on responses: https://api.slack.com/web
        '''
        return self.api_requester.do(self.token, method, kwargs, timeout=timeout).text

# TODO: Move the error types defined below into the .exceptions namespace. This would be a semver
# major change because any clients already referencing these types in order to catch them
# specifically would need to deal with the symbol names changing.


class SlackConnectionError(SlackClientError):
    def __init__(self, message='', reply=None):
        super(SlackConnectionError, self).__init__(message)
        self.reply = reply


class SlackLoginError(SlackClientError):
    def __init__(self, message='', reply=None):
        super(SlackLoginError, self).__init__(message)
        self.reply = reply
