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
    mock_server.send_to_websocket.assert_called_with({
        'text': 'hi',
        'channel': channel.id,
        'type': 'message',
    })


def test_channel_send_message_to_thread(channel, mocker, monkeypatch):
    mock_server = mocker.Mock()
    monkeypatch.setattr(channel, 'server', mock_server)
    channel.send_message('hi', thread='123456.789')
    mock_server.send_to_websocket.assert_called_with({
        'text': 'hi',
        'channel': channel.id,
        'type': 'message',
        'thread_ts': '123456.789',
    })
    channel.send_message('hi', thread='123456.789', reply_broadcast=True)
    mock_server.send_to_websocket.assert_called_with({
        'text': 'hi',
        'channel': channel.id,
        'type': 'message',
        'thread_ts': '123456.789',
        'reply_broadcast': True,
    })
