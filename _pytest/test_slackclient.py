from slackclient._client import SlackClient
from slackclient._channel import Channel
import json
import pytest

@pytest.fixture
def channel_created():
    channel_created = open('_pytest/data/channel.created.json', 'r').read()
    channel_created = json.loads(channel_created)
    return channel_created

@pytest.fixture
def im_created():
    channel_created = open('_pytest/data/im.created.json', 'r').read()
    channel_created = json.loads(channel_created)
    return channel_created

def test_SlackClient(slackclient):
    assert type(slackclient) == SlackClient

def test_SlackClient_process_changes(slackclient, channel_created, im_created):
    slackclient.process_changes(channel_created)
    assert type(slackclient.server.channels.find('fun')) == Channel
    slackclient.process_changes(im_created)
    assert type(slackclient.server.channels.find('U123BL234')) == Channel

