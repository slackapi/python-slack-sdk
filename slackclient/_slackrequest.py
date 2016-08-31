import json

import requests
import six


class SlackRequest(object):

    @staticmethod
    def do(token, request="?", post_data=None, domain="slack.com"):
        '''
        Perform a POST request to the Slack Web API

        Args:
            token (str): your authentication token
            request (str): the method to call from the Slack API. For example: 'channels.list'
            post_data (dict): key/value arguments to pass for the request. For example:
                {'channel': 'CABC12345'}
            domain (str): if for some reason you want to send your request to something other
                than slack.com
        '''
        post_data = post_data or {}

        # Pull file out so it isn't JSON encoded like normal fields.
        # Only do this for requests that are UPLOADING files; downloading files
        # use the 'file' argument to point to a File ID.
        upload_requests = ['files.upload']
        files = None
        if request in upload_requests:
            files = {'file': post_data.pop('file')} if 'file' in post_data else None

        for k, v in six.iteritems(post_data):
            if not isinstance(v, six.string_types):
                post_data[k] = json.dumps(v)

        url = 'https://{0}/api/{1}'.format(domain, request)
        post_data['token'] = token

        return requests.post(url, data=post_data, files=files)
