import time
import urllib
import urllib2

class SlackRequest(object):
    def __init__(self):
        pass

    def do(self, token, request="?", post_data={}, domain="slack.com"):
        post_data["token"] = token
        post_data = urllib.urlencode(post_data)
        url = 'https://{}/api/{}'.format(domain, request)
        return urllib2.urlopen(url, post_data)

