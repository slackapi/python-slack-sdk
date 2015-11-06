import time
from future.moves.urllib.parse import urlparse, urlencode
from future.moves.urllib.request import urlopen, Request
from future.moves.urllib.error import HTTPError


class SlackRequest(object):
    def __init__(self):
        pass

    def do(self, token, request="?", post_data={}, domain="slack.com"):
        post_data["token"] = token
        post_data = urlencode(post_data)
        url = 'https://{}/api/{}'.format(domain, request)
        return urlopen(url, post_data.encode('utf-8'))

