from _slackrequest import SlackRequest

from websocket import create_connection
import json

class Server(object):
    def __init__(self, token):
        self.token = token
        self.nick = None
        self.name = None
        self.domain = None
        self.login_data = None
        self.websocket = None
        self.users = []
        self.channels = []
        self.connected = False
        self.pingcounter = 0
        self.api_requester = SlackRequest()

        self.connect_to_slack()
    def __eq__(self, compare_str):
        if compare_str == self.domain or compare_str == self.token:
            return True
        else:
            return False
    def __str__(self):
        data = ""
        for key in self.__dict__.keys():
            data += "%s : %s\n" % (key, str(self.__dict__[key])[:40])
        return data
    def __repr__(self):
        return self.__str__()

    def connect_to_slack(self):
        reply = self.api_requester.do(self.token, "rtm.start")
        if reply.code != 200:
            raise SlackLoginError
        else:
            login_data = json.loads(reply.read())
            self.parse_slack_login_data(login_data)
    def parse_slack_login_data(self, login_data):
        self.login_data = login_data
        self.domain = self.login_data["team"]["domain"]
        self.name = self.login_data["self"]["name"]
        try:
            self.websocket = create_connection(self.login_data['url'])
            self.websocket.sock.setblocking(0)
        except:
            raise SlackLoginError

    def send_to_websocket(self, data):
        data = json.dumps(data)
        self.websocket.send(data)

    def ping(self):
        return self.send_to_websocket({"type": "ping"})

    def websocket_safe_read(self):
        data = ""
        while True:
            try:
                data += "%s\n" % self.websocket.recv()
            except:
                return data.rstrip()

class SlackLoginError(Exception):
    pass
