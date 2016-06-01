import json
import requests


class SlackRequest(object):

    @staticmethod
    def do(token, request="?", post_data=None, domain="slack.com"):
        post_data = post_data or {}

        for k, v in post_data.items():
            if not isinstance(v, (str, unicode)):
                post_data[k] = json.dumps(v)

        url = 'https://{0}/api/{1}'.format(domain, request)
        post_data['token'] = token

        return requests.post(url, data=post_data)
