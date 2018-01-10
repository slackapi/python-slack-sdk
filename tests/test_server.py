import json
import pytest
import requests
import responses
from slackclient.user import User
from slackclient.server import Server, SlackLoginError
from slackclient.channel import Channel
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


@pytest.fixture
def rtm_start_fixture():
    file_login_data = open('tests/data/rtm.start.json', 'r').read()
    json_login_data = json.loads(file_login_data)
    return json_login_data


def test_server(server):
    assert type(server) == Server


def test_server_is_hashable(server):
    server_map = {server: server.token}
    assert server_map[server] == 'xoxp-1234123412341234-12341234-1234'
    assert (server_map[server] == 'foo') is False


def test_response_headers(server):
    # Testing for rate limit retry headers
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/auth.test",
            status=429,
            json={"ok": True},
            headers={'Retry-After': "1"}
        )

        res = json.loads(server.api_call("auth.test"))

        for call in rsps.calls:
            assert call.request.url in [
                "https://slack.com/api/auth.test"
            ]
            assert call.response.status_code == 429
        assert res["headers"]['Retry-After'] == "1"


def test_server_parse_channel_data(server, rtm_start_fixture):
    server.parse_channel_data(rtm_start_fixture["channels"])
    assert type(server.channels.find('general')) == Channel


def test_server_parse_user_data(server, rtm_start_fixture):
    server.parse_user_data(rtm_start_fixture["users"])
    # Find user by Name
    userbyname = server.users.find('fakeuser')
    assert type(userbyname) == User
    assert userbyname == "fakeuser"
    assert userbyname != "someotheruser"
    # Find user by ID
    userbyid = server.users.find('U10CX1234')
    assert type(userbyid) == User
    assert userbyid == "fakeuser"
    assert userbyid.email == 'fakeuser@example.com'
    # Don't find invalid user
    userbyid = server.users.find('invaliduser')
    assert type(userbyid) != User


def test_server_cant_connect(server):
    with pytest.raises(SlackLoginError):
        reply = server.ping()


@pytest.mark.xfail
def test_server_ping(server, monkeypatch):
    monkeypatch.setattr("websocket.create_connection", lambda: True)
    reply = server.ping()
