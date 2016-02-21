from future.moves.urllib.parse import urlencode
from future.moves.urllib.request import urlopen


class SlackRequest(object):
    def __init__(self):
        pass

    def do(self, token, request="?", post_data=None, domain="slack.com"):
        if post_data is None:
            post_data = {}
        post_data["token"] = token
        post_data = urlencode(post_data)
        url = 'https://{}/api/{}'.format(domain, request)
        return urlopen(url, post_data.encode('utf-8'))

