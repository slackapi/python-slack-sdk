import json
import pytest
from requests.exceptions import ProxyError
import responses
from slackclient.exceptions import TokenRefreshError
from slackclient.channel import Channel
from slackclient.client import SlackClient
from slackclient.server import SlackConnectionError


@pytest.fixture
def channel_created_fixture():
    file_channel_created_data = open("tests/data/channel.created.json", "r").read()
    json_channel_created_data = json.loads(file_channel_created_data)
    return json_channel_created_data


@pytest.fixture
def im_created_fixture():
    file_channel_created_data = open("tests/data/im.created.json", "r").read()
    json_channel_created_data = json.loads(file_channel_created_data)
    return json_channel_created_data


def test_proxy():
    proxies = {"http": "some-bad-proxy", "https": "some-bad-proxy"}
    client = SlackClient("xoxp-1234123412341234-12341234-1234", proxies=proxies)
    server = client.server

    assert server.proxies == proxies

    with pytest.raises(ProxyError):
        server.rtm_connect()

    with pytest.raises(SlackConnectionError):
        server.connect_slack_websocket(
            "wss://mpmulti-xw58.slack-msgs.com/websocket/bad-token"
        )

    api_requester = server.api_requester
    assert api_requester.proxies == proxies
    with pytest.raises(ProxyError):
        api_requester.do("xoxp-1234123412341234-12341234-1234", request="channels.list")


def test_SlackClient(slackclient):
    assert type(slackclient) == SlackClient


def test_custom_user_agent(slackclient):
    slackclient.append_user_agent("customua", "1.0.0")
    assert "customua" in slackclient.server.api_requester.get_user_agent()


def test_SlackClient_process_changes(
    slackclient, channel_created_fixture, im_created_fixture
):
    slackclient.process_changes(channel_created_fixture)
    assert type(slackclient.server.channels.find("fun")) == Channel
    slackclient.process_changes(im_created_fixture)
    assert type(slackclient.server.channels.find("U123BL234")) == Channel


def test_api_not_ok(slackclient):
    # Testing for rate limit retry headers
    client = SlackClient("xoxp-1234123412341234-12341234-1234")

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/im.open",
            status=200,
            json={"ok": False, "error": "invalid_auth"},
            headers={},
        )

        client.api_call("im.open", user="UXXXX")

        for call in rsps.calls:
            assert call.response.status_code == 200
            assert call.request.url in ["https://slack.com/api/im.open"]


def test_im_open(slackclient):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/im.open",
            status=200,
            json={"ok": True, "channel": {"id": "CXXXXXX"}},
            headers={},
        )

        slackclient.api_call("im.open", user="UXXXX")

        for call in rsps.calls:
            assert call.response.status_code == 200
            assert call.request.url in ["https://slack.com/api/im.open"]


def test_channel_join(slackclient):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/channels.join",
            status=200,
            json={
                "ok": True,
                "channel": {
                    "id": "CXXXX",
                    "name": "test",
                    "members": ("U0G9QF9C6", "U1QNSQB9U"),
                },
            },
        )

        slackclient.api_call("channels.join", channel="CXXXX")

        for call in rsps.calls:
            assert call.response.status_code == 200
            assert call.request.url in ["https://slack.com/api/channels.join"]
            response_json = call.response.json()
            assert response_json["ok"] is True


def test_noncallable_refresh_callback():
    with pytest.raises(TokenRefreshError):
        SlackClient(
            client_id="12345",
            client_secret="12345",
            refresh_token="refresh_token",
            token_update_callback="THIS IS A STRING, NOT A CALLABLE METHOD",
        )


def test_no_RTM_with_workspace_tokens():
    def token_update_callback(update_data):
        return update_data

    with pytest.raises(TokenRefreshError):
        sc = SlackClient(
            client_id="12345",
            client_secret="12345",
            refresh_token="refresh_token",
            token_update_callback=token_update_callback,
        )

        sc.rtm_connect()


def test_token_refresh_on_initial_api_request():
    # Client should fetch and append an access token on the first API request

    # When the token is refreshed, the client will call this callback
    access_token = "xoxa-2-abcdef"
    client_args = {}

    def token_update_callback(update_data):
        client_args[update_data["team_id"]] = update_data

    sc = SlackClient(
        client_id="12345",
        client_secret="12345",
        refresh_token="refresh_token",
        token_update_callback=token_update_callback,
    )

    # The client starts out with an empty token
    assert sc.token is None

    # Mock both the main API request and the token refresh request
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/auth.test",
            status=200,
            json={"ok": True},
        )

        rsps.add(
            responses.POST,
            "https://slack.com/api/oauth.access",
            status=200,
            json={
                "ok": True,
                "access_token": access_token,
                "token_type": "app",
                "expires_in": 3600,
                "team_id": "T2U81E2FP",
                "enterprise_id": "T2U81ELK",
            },
        )

        # Calling the API for the first time will trigger a token refresh
        sc.api_call("auth.test")

        # Store the calls in order
        calls = {}
        for index, call in enumerate(rsps.calls):
            calls[index] = {"url": call.request.url}

        # After the initial call, the refresh method will update the client's token,
        # then the callback will update client_args
        assert sc.token == access_token
        assert client_args["T2U81E2FP"]["access_token"] == access_token

        # Verify that the client first tried to call the API, refreshed the token, then retried
        assert calls[0]["url"] == "https://slack.com/api/oauth.access"
        assert calls[1]["url"] == "https://slack.com/api/auth.test"


def test_token_refresh_failed():
    # Client should raise TokenRefreshError is token refresh returns error
    def token_update_callback(update_data):
        return update_data

    sc = SlackClient(
        client_id="12345",
        client_secret="12345",
        refresh_token="refresh_token",
        token_update_callback=token_update_callback,
    )

    with pytest.raises(TokenRefreshError):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "https://slack.com/api/channels.list",
                status=200,
                json={"ok": False, "error": "invalid_auth"},
            )

            rsps.add(
                responses.POST,
                "https://slack.com/api/oauth.access",
                status=200,
                json={"ok": False, "error": "invalid_auth"},
            )

            sc.api_call("channels.list")


def test_token_refresh_on_expired_token():
    # Client should fetch and append an access token on the first API request

    # When the token is refreshed, the client will call this callback
    client_args = {}

    def token_update_callback(update_data):
        client_args[update_data["team_id"]] = update_data

    sc = SlackClient(
        client_id="12345",
        client_secret="12345",
        refresh_token="refresh_token",
        token_update_callback=token_update_callback,
    )

    # Set the token TTL to some time in the past
    sc.access_token_expires_at = 0

    # Mock both the main API request and the token refresh request
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/auth.test",
            status=200,
            json={"ok": True},
        )

        rsps.add(
            responses.POST,
            "https://slack.com/api/oauth.access",
            status=200,
            json={
                "ok": True,
                "access_token": "xoxa-2-abcdef",
                "token_type": "app",
                "expires_in": 3600,
                "team_id": "T2U81E2FP",
                "enterprise_id": "T2U81ELK",
            },
        )

        # Calling the API for the first time will trigger a token refresh
        sc.api_call("auth.test")

        # Store the calls in order
        calls = {}
        for index, call in enumerate(rsps.calls):
            calls[index] = {"url": call.request.url}

        # Verify that the client first fetches the token, then submits the request
        assert calls[0]["url"] == "https://slack.com/api/oauth.access"
        assert calls[1]["url"] == "https://slack.com/api/auth.test"
