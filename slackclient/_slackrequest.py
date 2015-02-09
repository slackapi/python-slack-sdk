import time
import urllib
import urllib2

from _config import config

class SlackRequest(object):
    def __init__(self):
        pass

    def do(self, token, request="?", post_data={}, domain=None):
        if domain is None:
            domain = config.DOMAIN
        post_data["token"] = token
        post_data = urllib.urlencode(post_data)
        url = 'https://{}/api/{}'.format(domain, request)
        return urllib2.urlopen(url, post_data)

