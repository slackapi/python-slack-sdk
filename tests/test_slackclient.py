import json

import pytest
from requests.exceptions import ProxyError

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

