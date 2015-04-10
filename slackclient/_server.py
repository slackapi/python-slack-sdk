from slackclient._slackrequest import SlackRequest
from slackclient._channel import Channel
from slackclient._user import User
from slackclient._util import SearchList

from websocket import create_connection
import json


class Server(object):
    def __init__(self, token, connect=True):
        self.token = token
        self.username = None
        self.domain = None
        self.login_data = None
        self.websocket = None
        self.users = SearchList()
        self.channels = SearchList()
        self.connected = False
        self.pingcounter = 0
        self.api_requester = SlackRequest()

        if connect:
            self.rtm_connect()

    def __eq__(self, compare_str):
        if compare_str == self.domain or compare_str == self.token:
            return True
        else:
            return False

    def __str__(self):
        data = ""
        for key in list(self.__dict__.keys()):
            data += "{} : {}\n".format(key, str(self.__dict__[key])[:40])
        return data

    def __repr__(self):
        return self.__str__()

    def rtm_connect(self, reconnect=False):
        reply = self.api_requester.do(self.token, "rtm.start")
        if reply.code != 200:
            raise SlackConnectionError
        else:
            login_data = json.loads(reply.read().decode('utf-8'))
            if login_data["ok"]:
                self.ws_url = login_data['url']
                if not reconnect:
                    self.parse_slack_login_data(login_data)
                self.connect_slack_websocket(self.ws_url)
            else:
                raise SlackLoginError

    def parse_slack_login_data(self, login_data):
        self.login_data = login_data
        self.domain = self.login_data["team"]["domain"]
        self.username = self.login_data["self"]["name"]
        self.parse_channel_data(login_data["channels"])
        self.parse_channel_data(login_data["groups"])
        self.parse_channel_data(login_data["ims"])
        self.parse_user_data(login_data["users"])

    def connect_slack_websocket(self, ws_url):
        try:
            self.websocket = create_connection(ws_url)
            self.websocket.sock.setblocking(0)
        except:
            raise SlackConnectionError

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
            self.attach_user(user["name"], user["id"], user["real_name"], user["tz"])

    def send_to_websocket(self, data):
        """Send (data) directly to the websocket."""
        try:
            data = json.dumps(data)
            self.websocket.send(data)
        except:
            self.rtm_connect(reconnect=True)

    def ping(self):
        return self.send_to_websocket({"type": "ping"})

    def websocket_safe_read(self):
        """ Returns data if available, otherwise ''. Newlines indicate multiple
            messages
        """

        data = ""
        while True:
            try:
                data += "{}\n".format(self.websocket.recv())
            except:
                return data.rstrip()

    def attach_user(self, name, id, real_name, tz):
        self.users.append(User(self, name, id, real_name, tz))

    def attach_channel(self, name, id, members=[]):
        self.channels.append(Channel(self, name, id, members))

    def join_channel(self, name):
        print(self.api_requester.do(self.token,
                                    "channels.join?name={}".format(name)).read())

    def api_call(self, method, **kwargs):
        reply = self.api_requester.do(self.token, method, kwargs)
        return reply.read()


class SlackConnectionError(Exception):
    pass


class SlackLoginError(Exception):
    pass
