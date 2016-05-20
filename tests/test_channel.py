from slackclient._channel import Channel
import pytest

def mock_channel():
    ''' Returns a Channel object for testing. '''

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

@pytest.mark.xfail
def test_channel_send_message(channel):
    channel.send_message('hi')
