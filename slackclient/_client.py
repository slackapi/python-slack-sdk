#!/usr/bin/python

import json

from _server import Server

class SlackClient(object):
    def __init__(self, token):
        self.token = token
        self.server = None
    def connect(self):
        try:
            self.server = Server(self.token)
            return True
        except:
            return False
    def read(self):
        if self.server:
            json_data = self.server.websocket_safe_read()
            data = []
            if json_data != '':
                for d in json_data.split('\n'):
                    data.append(json.loads(d))
            return data
        else:
            raise SlackNotConnected

class SlackNotConnected(Exception):
    pass
