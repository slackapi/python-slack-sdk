from slackclient._channel import Channel

def test_channel(channel):
    assert type(channel) == Channel
