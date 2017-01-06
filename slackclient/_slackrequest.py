import json

import requests
import six

import sys
import platform
from .version import __version__

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

        user_agent = [] # Construct the user-agent header with the package info, Python version and OS version.

        client_name = __name__.split('.')[0] # __name__ returns 'slackclient._slackrequest', we only want 'slackclient'
        client_version = __version__ # Version is returned from version.py

        user_agent.append("%s/%s" % (client_name, client_version))
        user_agent.append("python/%s.%s.%s" % (sys.version_info[0], sys.version_info[1], sys.version_info[2]))
        user_agent.append("%s/%s" % (platform.system(), platform.release()))

        headers = {'user-agent': ' '.join(map(str, user_agent))}

        # Pull file out so it isn't JSON encoded like normal fields.
        # Only do this for requests that are UPLOADING files; downloading files
        # use the 'file' argument to point to a File ID.
        post_data = post_data or {}
        upload_requests = ['files.upload']
        files = None
        if request in upload_requests:
            files = {'file': post_data.pop('file')} if 'file' in post_data else None

        for k, v in six.iteritems(post_data):
            if not isinstance(v, six.string_types):
                post_data[k] = json.dumps(v)

        url = 'https://{0}/api/{1}'.format(domain, request)
        post_data['token'] = token

        return requests.post(url, headers=headers, data=post_data, files=files)
