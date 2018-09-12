from slackclient.slackrequest import SlackRequest
from slackclient.version import __version__
import os


def test_http_headers(mocker):
    requests = mocker.patch('slackclient.slackrequest.requests')
    request = SlackRequest()

    request.do('xoxb-123', 'chat.postMessage', {'text': 'test', 'channel': '#general'})
    args, kwargs = requests.post.call_args

    assert kwargs['headers']['user-agent'] is not None


def test_custom_user_agent(mocker):
    requests = mocker.patch('slackclient.slackrequest.requests')
    request = SlackRequest()

    request.append_user_agent("fooagent1", "0.1")
    request.append_user_agent("baragent/2", "0.2")

    request.do('xoxb-123', 'chat.postMessage', {'text': 'test', 'channel': '#general'})
    args, kwargs = requests.post.call_args

    # Verify user-agent includes both default and custom agent info
    assert "slackclient/{}".format(__version__) in kwargs['headers']['user-agent']
    assert "fooagent1/0.1" in kwargs['headers']['user-agent']

    # verify escaping of slashes in custom agent name
    assert "baragent:2/0.2" in kwargs['headers']['user-agent']


def test_auth_header(mocker):
    requests = mocker.patch('slackclient.slackrequest.requests')
    request = SlackRequest()

    request.do('xoxb-123', 'chat.postMessage', {'text': 'test', 'channel': '#general'})
    args, kwargs = requests.post.call_args

    assert "Bearer xoxb-123" in kwargs['headers']['Authorization']


def test_token_override(mocker):
    requests = mocker.patch('slackclient.slackrequest.requests')
    request = SlackRequest()

    request.do('xoxb-123', 'chat.postMessage',
               {
                   'token': "newtoken",
                   'text': 'test',
                   'channel': '#general'
                })
    args, kwargs = requests.post.call_args

    assert "Bearer newtoken" in kwargs['headers']['Authorization']


def test_plural_field(mocker):
    requests = mocker.patch('slackclient.slackrequest.requests')
    request = SlackRequest()

    request.do('xoxb-123', 'conversations.open', {'users': ['U123', 'U234', 'U345']})
    args, kwargs = requests.post.call_args

    assert kwargs['data'] == {'users': 'U123,U234,U345'}

    request.do('xoxb-123', 'conversations.open', {'users': "U123,U234,U345"})
    args2, kwargs2 = requests.post.call_args

    assert kwargs2['data'] == {'users': 'U123,U234,U345'}


def test_post_file(mocker):
    requests = mocker.patch('slackclient.slackrequest.requests')
    request = SlackRequest()

    request.do('xoxb-123',
               'files.upload',
               {'file': open(os.path.join('.', 'tests', 'data', 'slack_logo.png'), 'rb'),
                'filename': 'slack_logo.png'})
    args, kwargs = requests.post.call_args

    assert requests.post.call_count == 1
    assert 'https://slack.com/api/files.upload' == args[0]
    assert {'filename': 'slack_logo.png'} == kwargs['data']
    assert kwargs['files'] is not None


def test_get_file(mocker):
    requests = mocker.patch('slackclient.slackrequest.requests')
    request = SlackRequest()

    request.do('xoxb-123', 'files.info', {'file': 'myFavoriteFileID'})
    args, kwargs = requests.post.call_args

    assert requests.post.call_count == 1
    assert 'https://slack.com/api/files.info' == args[0]
    assert {'file': "myFavoriteFileID"} == kwargs['data']
    assert kwargs['files'] is None


def test_post_attachements(mocker):
    requests = mocker.patch('slackclient.slackrequest.requests')
    request = SlackRequest()

    request.do('xoxb-123',
               'chat.postMessage',
               {'attachments': [{'title': 'hello'}]})
    args, kwargs = requests.post.call_args

    assert requests.post.call_count == 1
    assert 'https://slack.com/api/chat.postMessage' == args[0]
    assert isinstance(kwargs["data"]["attachments"], str)
