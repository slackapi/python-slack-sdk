import pytest
from slackclient._channel import Channel
from slackclient._server import Server
from slackclient._client import SlackClient


@pytest.fixture
def server(monkeypatch):
    my_server = Server('xoxp-1234123412341234-12341234-1234', False)
    return my_server


@pytest.fixture
def slackclient(client_server):
    my_slackclient = SlackClient('xoxp-1234123412341234-12341234-1234')
    return my_slackclient


@pytest.fixture
def channel(channel_server):
    my_channel = Channel(channel_server, "somechannel", "C12341234", ["user"])
    return my_channel

