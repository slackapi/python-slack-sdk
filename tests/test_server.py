from slackclient._user import User
from slackclient._server import Server, SlackLoginError
from slackclient._channel import Channel
import json
import pytest
from unittest.mock import patch


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
    assert type(server.users.find('fakeuser')) == User


def test_Server_cantconnect(server):
    with pytest.raises(SlackLoginError):
        reply = server.ping()


@pytest.mark.xfail
def test_Server_ping(server, monkeypatch):
    # monkeypatch.setattr("", lambda: True)
    monkeypatch.setattr("websocket.create_connection", lambda: True)
    reply = server.ping()


def test_Server_proxy_success(server, monkeypatch):
    url = 'url'
    host = 'localhost'
    port = '8080'
    monkeypatch.setenv('HTTP_PROXY_HOST', host)
    monkeypatch.setenv('HTTP_PROXY_PORT', port)

    @patch('websocket.create_connection')
    def test_connect_slack_websocket_proxy(mocked_create_connection):
        server.connect_slack_websocket(url)
        mocked_create_connection.assert_called_once_with(url, host, port)


def test_Server_proxy_host_not_set(server, monkeypatch):
    url = 'url'
    monkeypatch.setenv('HTTP_PROXY_PORT', '8080')

    @patch('websocket.create_connection')
    def test_connect_slack_websocket_proxy(mocked_create_connection):
        server.connect_slack_websocket(url)
        mocked_create_connection.assert_called_once_with(url)


def test_Server_proxy_port_not_set(server, monkeypatch):
    url = 'url'
    monkeypatch.setenv('HTTP_PROXY_HOST', 'localhost')

    @patch('websocket.create_connection')
    def test_connect_slack_websocket_proxy(mocked_create_connection):
        server.connect_slack_websocket(url)
        mocked_create_connection.assert_called_once_with(url)

