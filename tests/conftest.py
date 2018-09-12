import pytest
import requests
from slackclient.channel import Channel
from slackclient.server import Server
from slackclient.client import SlackClient


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
    my_server = Server(token='xoxp-1234123412341234-12341234-1234', connect=False)
    return my_server


@pytest.fixture
def slackclient():
    my_slackclient = SlackClient('xoxp-1234123412341234-12341234-1234')
    return my_slackclient


@pytest.fixture
def channel(server):
    my_channel = Channel(server, "somechannel", "C12341234", ["user"])
    return my_channel

