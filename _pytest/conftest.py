import pytest
from slackclient._channel import Channel
from slackclient._server import Server

@pytest.fixture
def server(monkeypatch):
    myserver = Server('xoxp-1234123412341234-12341234-1234', False)
    return myserver

@pytest.fixture
def channel(server):
    mychannel = Channel(server, "somechannel", "C12341234", ["user"])
    return mychannel
