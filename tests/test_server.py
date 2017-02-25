from slackclient._user import User
from slackclient._server import Server, SlackLoginError
from slackclient._channel import Channel
import json
import pytest


@pytest.fixture
def login_fixture():
    file_login_data = open('tests/data/rtm.start.json', 'r').read()
    json_login_data = json.loads(file_login_data)
    return json_login_data


def test_Server(server):
    assert type(server) == Server


def test_Server_is_hashable(server):
    server_map = {server: server.token}
    assert server_map[server] == 'xoxp-1234123412341234-12341234-1234'
    assert (server_map[server] == 'foo') is False


def test_Server_parse_channel_data(server, login_fixture):
    server.parse_channel_data(login_fixture["channels"])
    assert type(server.channels.find('general')) == Channel


def test_Server_parse_user_data(server, login_fixture):
    server.parse_user_data(login_fixture["users"])
    # Find user by Name
    userbyname = server.users.find('fakeuser')
    assert type(userbyname) == User
    assert userbyname == "fakeuser"
    assert userbyname != "someotheruser"
    # Find user by ID
    userbyid = server.users.find('U10CX1234')
    assert type(userbyid) == User
    assert userbyid == "fakeuser"
    # Don't find invalid user
    userbyid = server.users.find('invaliduser')
    assert type(userbyid) != User


def test_Server_cantconnect(server):
    with pytest.raises(SlackLoginError):
        reply = server.ping()


@pytest.mark.xfail
def test_Server_ping(server, monkeypatch):
    # monkeypatch.setattr("", lambda: True)
    monkeypatch.setattr("websocket.create_connection", lambda: True)
    reply = server.ping()

def test_Server_ping_args(server, mocker, monkeypatch):
    # Mock out send_to_websocket since it will just cause errors.
    sendmock = mocker.Mock()
    sendmock.return_value = None
    monkeypatch.setattr(server, 'send_to_websocket', sendmock)
    # No id.
    reply = server.ping()
    assert reply == (None, None)
    args, kwargs = sendmock.call_args
    assert args == ({"type": "ping"},)
    # Provide an id in the pingid argument.
    sendmock.reset_mock()
    reply = server.ping(1234)
    assert reply == (1234, None)
    args, kwargs = sendmock.call_args
    assert args == ({"type": "ping", "id": 1234},)
    # Provide and id in kwargs and in pingid. pingid has priority.
    sendmock.reset_mock()
    reply = server.ping(1234, id=42)
    assert reply == (1234, None)
    args, kwargs = sendmock.call_args
    assert args == ({"type": "ping", "id":1234},)
    # Provide an id in kwargs only.
    sendmock.reset_mock()
    reply = server.ping(id=42)
    assert reply == (42, None)
    args, kwargs = sendmock.call_args
    assert args == ({"type": "ping", "id":42},)
    # Provide extra arguments.
    sendmock.reset_mock()
    reply = server.ping(1234, timestamp=1000, user="USOMEUSER")
    assert reply == (1234, None)
    args, kwargs = sendmock.call_args
    assert args == ({"type": "ping", "id": 1234, "timestamp":1000, "user": "USOMEUSER"},)
