import time
from urllib.request import urlopen
from urllib.parse import urlparse

class SlackRequest(object):
    def __init__(self):
        pass

    def do(self, token, request="?", post_data={}, domain="slack.com"):
        post_data["token"] = token
        post_data = urllib.parse.urlencode(post_data)
        url = 'https://{}/api/{}'.format(domain, request)
        return urllib.request.urlopen(url, post_data)

