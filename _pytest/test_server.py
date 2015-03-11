from slackclient._user import User
from slackclient._server import Server, SlackLoginError
from slackclient._channel import Channel
import json
import pytest

@pytest.fixture
def login_data():
    login_data = open('_pytest/data/rtm.start.json','r').read()
    login_data = json.loads(login_data)
    return login_data

def test_Server(server):
    assert type(server) == Server


def test_Server_parse_channel_data(server, login_data):
    server.parse_channel_data(login_data["channels"])
    assert type(server.channels.find('general')) == Channel

def test_Server_parse_user_data(server, login_data):
    server.parse_user_data(login_data["users"])
    assert type(server.users.find('fakeuser')) == User

def test_Server_cantconnect(server):
    with pytest.raises(SlackLoginError):
        reply = server.ping()

@pytest.mark.xfail
def test_Server_ping(server, monkeypatch):
    #monkeypatch.setattr("", lambda: True)
    monkeypatch.setattr("websocket.create_connection", lambda: True)
    reply = server.ping()
