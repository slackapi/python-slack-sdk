import pytest
from slackclient._channel import Channel
from slackclient._server import Server
from slackclient._client import SlackClient


@pytest.fixture
def server(monkeypatch):
    myserver = Server('xoxp-1234123412341234-12341234-1234', False)
    return myserver


@pytest.fixture
def slackclient(client_server):
    myslackclient = SlackClient('xoxp-1234123412341234-12341234-1234')
    return myslackclient


@pytest.fixture
def channel(channel_server):
    mychannel = Channel(channel_server, "somechannel", "C12341234", ["user"])
    return mychannel

