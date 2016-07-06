from slackclient._channel import Channel
import pytest


def test_channel(channel):
    assert type(channel) == Channel

def test_channel_eq(channel):
    channel = Channel(
        'test-server',
        'test-channel',
        'C12345678',
    )
    assert channel == 'test-channel'
    assert channel == '#test-channel'
    assert channel == 'C12345678'
    assert (channel == 'foo') is False

def test_channel_hash(channel):
    channel = Channel(
        'test-server',
        'test-channel',
        'C12345678',
    )
    channel_map = {channel: channel.id}
    assert channel_map[channel] == 'C12345678'
    assert (channel_map[channel] == 'foo') is False

@pytest.mark.xfail
def test_channel_send_message(channel):
    channel.send_message('hi')
