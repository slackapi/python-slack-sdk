from _server import *
from _channel import *
from websocket import create_connection

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        bla = Server(sys.argv[1])

def connect(token):
    return Server(token)

def ping_pong():
    Server.ping()
