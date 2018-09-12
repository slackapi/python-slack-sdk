from slackclient.channel import Channel


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
    assert 'C12345678' in str(channel)
    assert 'C12345678' in "%r" % channel
    assert (channel == 'foo') is False


def test_channel_is_hashable(channel):
    channel = Channel(
        'test-server',
        'test-channel',
        'C12345678',
    )
    channel_map = {channel: channel.id}
    assert channel_map[channel] == 'C12345678'
    assert (channel_map[channel] == 'foo') is False


def test_channel_send_message(channel, mocker, monkeypatch):
    mock_server = mocker.Mock()
    monkeypatch.setattr(channel, 'server', mock_server)
    channel.send_message('hi')
    mock_server.rtm_send_message.assert_called_with(channel.id, 'hi', None, False)


def test_channel_send_message_to_thread(channel, mocker, monkeypatch):
    mock_server = mocker.Mock()
    monkeypatch.setattr(channel, 'server', mock_server)
    channel.send_message('hi', thread='123456.789')
    mock_server.rtm_send_message.assert_called_with(channel.id, 'hi', '123456.789', False)

    channel.send_message('hi', thread='123456.789', reply_broadcast=True)
    mock_server.rtm_send_message.assert_called_with(channel.id, 'hi', '123456.789', True)
