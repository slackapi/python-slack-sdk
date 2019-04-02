import json
import pytest
import responses
import time
import urllib3

from mock import patch

from slackclient.user import User
from slackclient.server import Server, SlackConnectionError
from slackclient.channel import Channel

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@pytest.fixture
def rtm_start_fixture():
    file_login_data = open('tests/data/rtm.start.json', 'r').read()
    json_login_data = json.loads(file_login_data)
    return json_login_data


def test_server():
    server = Server(token="valid_token", connect=False)
    assert type(server) == Server

    # The server eqs to a string, either the token or workspace domain
    assert server.token == "valid_token"


def test_server_connect(rtm_start_fixture):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/rtm.start",
            status=200,
            json=rtm_start_fixture
        )

        Server(token="token", connect=True)

        for call in rsps.calls:
            assert call.request.url in [
                "https://slack.com/api/rtm.start"
            ]


def test_api_call_for_empty_slack_responses(server):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/chat.postMessage",
            status=429,
            headers={"Retry-After": "1"},
        )

        response_received = server.api_call("token", "chat.postMessage")
        chat_postMessage_response = rsps.calls[0].response

        assert chat_postMessage_response.text == ""
        expected_response = {
            "headers": {"Content-Type": "text/plain", "Retry-After": "1"}
        }
        assert json.loads(response_received) == expected_response


def test_server_is_hashable(server):
    server_map = {server: server.token}
    assert server_map[server] == 'xoxp-1234123412341234-12341234-1234'
    assert (server_map[server] == 'foo') is False


@patch('time.sleep', return_value=None)
def test_rate_limiting(patched_time_sleep, server):
    # Testing for rate limit retry headers
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/rtm.start",
            status=429,
            json={"ok": False},
            headers={'Retry-After': "1"}
        )

        with pytest.raises(SlackConnectionError) as e:
            server.rtm_connect()
            for call in rsps.calls:
                assert call.response.status_code == 429
            assert e.message == "RTM connection attempt was rate limited 10 times."


def test_custom_agent(server):
    server.append_user_agent("test agent", 1.0)
    assert server.api_requester.custom_user_agent[0] == ['test agent', 1.0]


def test_server_parse_channel_data(server, rtm_start_fixture):
    server.parse_channel_data(rtm_start_fixture["channels"])
    assert type(server.channels.find('general')) == Channel


def test_server_parse_user_data(server, rtm_start_fixture):
    server.parse_user_data(rtm_start_fixture["users"])
    # Find user by Name
    user_by_name = server.users.find('fakeuser')
    assert type(user_by_name) == User
    assert user_by_name == "fakeuser"
    assert user_by_name != "someotheruser"
    # Find user by ID
    user_by_id = server.users.find('U10CX1234')
    assert type(user_by_id) == User
    assert user_by_id == "fakeuser"
    assert user_by_id.email == 'fakeuser@example.com'
    # Don't find invalid user
    user_by_id = server.users.find('invaliduser')
    assert user_by_id is None


def test_server_cant_connect(server):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/rtm.start",
            status=403,
            json={"ok": False}
        )

        with pytest.raises(SlackConnectionError) as e:
            server.rtm_connect()


def test_reconnect_flag(server, rtm_start_fixture):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/rtm.start",
            status=200,
            json=rtm_start_fixture
        )

        server.rtm_connect(auto_reconnect=True)
        assert server.auto_reconnect is True

        for call in rsps.calls:
            assert call.request.url in [
                "https://slack.com/api/rtm.start"
            ]


def test_rtm_reconnect(server, rtm_start_fixture):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/rtm.connect",
            status=200,
            json=rtm_start_fixture
        )

        server.rtm_connect(auto_reconnect=True, reconnect=True, use_rtm_start=False)

        for call in rsps.calls:
            assert call.request.url in [
                "https://slack.com/api/rtm.connect"
            ]


@patch('time.sleep', return_value=None)
def test_rtm_max_reconnect_timeout(patched_time_sleep, server, rtm_start_fixture):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/rtm.connect",
            status=200,
            json=rtm_start_fixture
        )

        server.reconnect_count = 4
        server.last_connected_at = time.time()
        server.rtm_connect(auto_reconnect=True, reconnect=True, use_rtm_start=False)

        assert server.reconnect_count == 5


def test_rtm_reconnect_timeout_recently_connected(server, rtm_start_fixture):
    # If reconnected recently, server must wait to reconnect and increment the counter
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/rtm.connect",
            status=200,
            json=rtm_start_fixture
        )

        server.reconnect_count = 0
        server.last_connected_at = time.time()
        server.rtm_connect(auto_reconnect=True, reconnect=True, use_rtm_start=False)

        assert server.reconnect_count == 1
        for call in rsps.calls:
            assert call.request.url in [
                "https://slack.com/api/rtm.connect"
            ]


def test_rtm_reconnect_timeout_not_recently_connected(server, rtm_start_fixture):
    # If reconnecting after 3 minutes since last reconnect, reset counter and connect without wait
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/rtm.connect",
            status=200,
            json=rtm_start_fixture
        )

        server.reconnect_count = 1
        server.last_connected_at = time.time() - 180
        server.rtm_connect(auto_reconnect=True, reconnect=True, use_rtm_start=False)

        assert server.reconnect_count == 0
        for call in rsps.calls:
            assert call.request.url in [
                "https://slack.com/api/rtm.connect"
            ]


def test_max_rtm_reconnects(server, monkeypatch):
    monkeypatch.setattr("time.sleep", None)
    with pytest.raises(SlackConnectionError) as e:
        server.reconnect_count = 5
        server.rtm_connect(auto_reconnect=True, reconnect=True, use_rtm_start=False)
        assert e.message == "RTM connection failed, reached max reconnects."


@pytest.mark.xfail
def test_server_ping(server, monkeypatch):
    monkeypatch.setattr("websocket.create_connection", lambda: True)
    reply = server.ping()
