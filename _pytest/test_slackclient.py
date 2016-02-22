from slackclient._client import SlackClient
from slackclient._channel import Channel
import json
import pytest


@pytest.fixture
def channel_created_fixture():
    file_channel_created_data = open('_pytest/data/channel.created.json', 'r').read()
    json_channel_created_data = json.loads(file_channel_created_data)
    return json_channel_created_data


@pytest.fixture
def im_created_fixture():
    file_channel_created_data = open('_pytest/data/im.created.json', 'r').read()
    json_channel_created_data = json.loads(file_channel_created_data)
    return json_channel_created_data


def test_SlackClient(slackclient):
    assert type(slackclient) == SlackClient


def test_SlackClient_process_changes(slackclient, channel_created_fixture, im_created_fixture):
    slackclient.process_changes(channel_created_fixture)
    assert type(slackclient.server.channels.find('fun')) == Channel
    slackclient.process_changes(im_created_fixture)
    assert type(slackclient.server.channels.find('U123BL234')) == Channel

