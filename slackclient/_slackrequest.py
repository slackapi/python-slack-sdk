import json

import requests
import six


class SlackRequest(object):

    @staticmethod
    def do(token, request="?", post_data=None, domain="slack.com"):
        post_data = post_data or {}

        for k, v in six.iteritems(post_data):
            if not isinstance(v, six.string_types):
                post_data[k] = json.dumps(v)

        url = 'https://{0}/api/{1}'.format(domain, request)
        post_data['token'] = token
        files = {'file': post_data.pop('file')} if 'file' in post_data else None

        return requests.post(url, data=post_data, files=files)
