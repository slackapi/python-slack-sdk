import json

import pytest
from requests.exceptions import ProxyError
import responses

from slackclient.channel import Channel
from slackclient.client import SlackClient
from slackclient.server import SlackConnectionError


@pytest.fixture
def channel_created_fixture():
    file_channel_created_data = open('tests/data/channel.created.json', 'r').read()
    json_channel_created_data = json.loads(file_channel_created_data)
    return json_channel_created_data


@pytest.fixture
def im_created_fixture():
    file_channel_created_data = open('tests/data/im.created.json', 'r').read()
    json_channel_created_data = json.loads(file_channel_created_data)
    return json_channel_created_data


def test_proxy():
    proxies = {'http': 'some-bad-proxy', 'https': 'some-bad-proxy'}
    client = SlackClient('xoxp-1234123412341234-12341234-1234', proxies=proxies)
    server = client.server

    assert server.proxies == proxies

    with pytest.raises(ProxyError):
        server.rtm_connect()

    with pytest.raises(SlackConnectionError):
        server.connect_slack_websocket('wss://mpmulti-xw58.slack-msgs.com/websocket/bad-token')

    api_requester = server.api_requester
    assert api_requester.proxies == proxies
    with pytest.raises(ProxyError):
        api_requester.do('xoxp-1234123412341234-12341234-1234', request='channels.list')


def test_SlackClient(slackclient):
    assert type(slackclient) == SlackClient


def test_SlackClient_process_changes(slackclient, channel_created_fixture, im_created_fixture):
    slackclient.process_changes(channel_created_fixture)
    assert type(slackclient.server.channels.find('fun')) == Channel
    slackclient.process_changes(im_created_fixture)
    assert type(slackclient.server.channels.find('U123BL234')) == Channel


def test_api_not_ok(slackclient):
    # Testing for rate limit retry headers
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/im.open",
            status=200,
            json={
                "ok": False,
            },
            headers={}
        )

        slackclient.api_call(
            "im.open",
            user="UXXXX"
        )

        for call in rsps.calls:
            assert call.response.status_code == 200
            assert call.request.url in [
                "https://slack.com/api/im.open"
            ]


def test_im_open(slackclient):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://slack.com/api/im.open",
            status=200,
            json={
                "ok": True,
                "channel": {"id":"CXXXXXX"}
            },
            headers={}
        )

        slackclient.api_call(
            "im.open",
            user="UXXXX"
        )

        for call in rsps.calls:
            assert call.response.status_code == 200
            assert call.request.url in [
                "https://slack.com/api/im.open"
            ]


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
                    "members": ("U0G9QF9C6", "U1QNSQB9U")
                }
            }
        )

        slackclient.api_call(
            "channels.join",
            channel="CXXXX"
        )

        for call in rsps.calls:
            assert call.response.status_code == 200
            assert call.request.url in [
                "https://slack.com/api/channels.join"
            ]
            response_json = call.response.json()
            assert response_json["ok"] is True
