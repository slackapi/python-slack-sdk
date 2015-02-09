import time
try:
    from urllib2 import urlopen
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen
    from urllib.parse import urlencode
    

class SlackRequest(object):
    def __init__(self):
        pass

    def do(self, token, request="?", post_data={}, domain="slack.com"):
        post_data["token"] = token
        post_data = urlencode(post_data)
        url = 'https://{}/api/{}'.format(domain, request)
        return urlopen(url, post_data)

