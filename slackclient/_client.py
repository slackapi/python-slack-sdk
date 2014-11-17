#!/usr/bin/python

from _server import Server

class SlackClient(object):
    def __init__(self, token):
        self.token = token
        self.server = None
    def connect(self):
        self.server = Server(self.token)
