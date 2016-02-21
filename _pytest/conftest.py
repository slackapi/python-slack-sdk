import pytest
import requests
from slackclient._channel import Channel
from slackclient._server import Server
from slackclient._client import SlackClient


# This is so that tests work on Travis for python 2.6, it's really hacky, but expedient
def get_unverified_post():
    requests_post = requests.post

    def unverified_post(*args, **kwargs):
        # don't throw SSL errors plz
        kwargs['verify'] = False
        return requests_post(*args, **kwargs)

    return unverified_post

requests.post = get_unverified_post()


@pytest.fixture
def server(monkeypatch):
    myserver = Server('xoxp-1234123412341234-12341234-1234', False)
    return myserver

@pytest.fixture
def slackclient(server):
    myslackclient = SlackClient('xoxp-1234123412341234-12341234-1234')
    return myslackclient

@pytest.fixture
def channel(server):
    mychannel = Channel(server, "somechannel", "C12341234", ["user"])
    return mychannel

