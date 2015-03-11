from slackclient._channel import Channel
import pytest

def test_Channel(channel):
    assert type(channel) == Channel

@pytest.mark.xfail
def test_Channel_send_message(channel):
    channel.send_message('hi')
