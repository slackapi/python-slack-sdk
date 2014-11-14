#!/usr/bin/python

import json
from _server import Server

def connect(token):
    return Server(token)

def process_pong(server, message_json):
    pass

def process_message(server, message_json):
    channel = server.channels.find(message_json["channel"])
    text = message_json["text"]
    try:
        if text.startswith(server.username):
            print(text)
            channel.send_message("repeated! %s" % text)
        else:
            print "ignored text: %s" % text
    except:
        print Server

def input(server, data):
    message_json = json.loads(data)
    if "type" in message_json:
        function_name = message_json["type"]
    try:
        proc[function_name](server, message_json)
    except:
        pass

proc = {k[8:]: v for k, v in globals().items() if k.startswith("process_")}
reply_queue = []

if __name__ == "__main__":
    import sys
    import time
    if len(sys.argv) > 1:
        s = connect(sys.argv[1])
        while True:
            data = s.websocket_safe_read()
            if data != '':
                for d in data.split('\n'):
                    input(s, d)
            if len(reply_queue) > 0:
                s.reply_queue
            time.sleep(.1)


