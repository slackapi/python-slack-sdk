import time

try:
    # Try for Python3
    from urllib.parse import urlencode 
    from urllib.request import urlopen 
except:
    # Looks like Python2
    from urllib import urlencode 
    from urllib2 import urlopen 


from _config import config

class SlackRequest(object):
    def __init__(self):
        pass

    def do(self, token, request="?", post_data={}, domain=None):
        if domain is None:
            domain = config.DOMAIN
        post_data["token"] = token
        post_data = urlencode(post_data)
        url = 'https://{}/api/{}'.format(domain, request)
        return urlopen(url, post_data.encode('utf-8'))

