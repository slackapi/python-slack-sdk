from slackclient._slackrequest import SlackRequest
import json


def test_post_attachements(mocker):
    requests = mocker.patch('slackclient._slackrequest.requests')

    SlackRequest.do('xoxb-123',
                    'chat.postMessage',
                    {'attachments': [{'title': 'hello'}]})

    assert requests.post.call_count == 1
    args, kwargs = requests.post.call_args
    assert 'https://slack.com/api/chat.postMessage' == args[0]
    assert {'attachments': json.dumps([{'title': 'hello'}]),
            'token': 'xoxb-123'} == kwargs['data']
    assert None == kwargs['files']
