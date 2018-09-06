import json
import platform
import requests
import six
import sys
import time

from slackclient.exceptions import SlackClientError
from .version import __version__


class SlackRequest(object):
    def __init__(
            self,
            client=None,
            proxies=None,
            domain="slack.com",
            access_token=None,
            refresh_token=None,
            client_id=None,
            client_secret=None,
            refresh_callback=None
    ):
        # TODO: add pydoc comments

        # HTTP configs
        self.custom_user_agent = None
        self.proxies = proxies
        self.domain = domain

        # Construct the user-agent header with the package info, Python version and OS version.
        self.default_user_agent = {
            # __name__ returns all classes, we only want the client
            "client": "{0}/{1}".format(__name__.split('.')[0], __version__),
            "python": "Python/{v.major}.{v.minor}.{v.micro}".format(v=sys.version_info),
            "system": "{0}/{1}".format(platform.system(), platform.release())
        }

        # Slack application configs
        self.client = client
        self.access_token = access_token
        self.access_token_expires_at = None
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_callback = refresh_callback

    def get_user_agent(self):
        # Check for custom user-agent and append if found
        if self.custom_user_agent:
            custom_ua_list = ["/".join(client_info) for client_info in self.custom_user_agent]
            custom_ua_string = " ".join(custom_ua_list)
            self.default_user_agent['custom'] = custom_ua_string

        # Concatenate and format the user-agent string to be passed into request headers
        ua_string = []
        for key, val in self.default_user_agent.items():
            ua_string.append(val)

        user_agent_string = " ".join(ua_string)
        return user_agent_string

    def append_user_agent(self, name, version):
        if self.custom_user_agent:
            self.custom_user_agent.append([name.replace("/", ":"), version.replace("/", ":")])
        else:
            self.custom_user_agent = [[name, version]]

    def make_http_request(self, token=None, api_method="?", post_data=None, timeout=None):
        """
        Perform a POST request to the Slack Web API
        Args:
            token (str): your authentication token
            request (str): the method to call from the Slack API. For example: 'channels.list'
            timeout (float): stop waiting for a response after a given number of seconds
            post_data (dict): key/value arguments to pass for the request. For example:
                {'channel': 'CABC12345'}
        """

        # Override token header if `token` is passed in post_data
        if post_data is not None and "token" in post_data:
            token = post_data['token']

        # Pull `file` out so it isn't JSON encoded like normal fields.
        # Only do this for requests that are UPLOADING files; downloading files
        # use the 'file' argument to point to a File ID.
        post_data = post_data or {}

        # Move singular file objects into `files`
        upload_requests = ['files.upload']

        # Move file content into requests' `files` param
        files = None
        if api_method in upload_requests:
            files = {'file': post_data.pop('file')} if 'file' in post_data else None

        # Check for plural fields and convert them to comma-separated strings if needed
        for field in {'channels', 'users', 'types'} & set(post_data.keys()):
            if isinstance(post_data[field], list):
                post_data[field] = ",".join(post_data[field])

        # Convert any params which are list-like to JSON strings
        # Example: `attachments` is a dict, and needs to be passed as JSON
        for k, v in six.iteritems(post_data):
            if isinstance(v, (list, dict)):
                post_data[k] = json.dumps(v)

        request_args = {
            'api_method': api_method,
            'post_data': post_data,
        }
        return self.__post_http_request(token, request_args, files, timeout)

    def __post_http_request(self, token, request_args, files=None, timeout=None):
        # Check the access token's expiration timestamp before submitting
        # the API request and refresh if expired
        if(self.refresh_token and self.access_token_expires_at):
            current_ts = int(time.time()) * 1000
            if(current_ts > self.access_token_expires_at):
                self.access_token_expires_at = None
                self.refresh_access_token()

        # This allows us to override the default token (self.access_token) for refresh requests
        if(self.access_token and token is None):
            token = self.access_token

        # Set user-agent and auth headers
        headers = {
            'user-agent': self.get_user_agent(),
            'Authorization': 'Bearer {}'.format(token)
        }

        # Submit the request
        res = requests.post(
            'https://{0}/api/{1}'.format(self.domain, request_args['api_method']),
            headers=headers,
            data=request_args['post_data'],
            files=files,
            timeout=timeout,
            proxies=self.proxies
        )
        response_json = res.json()
        # if the API request returns an invalid_auth error, refresh the token and try again
        if (res.status_code is 200 and response_json['ok'] is False):
            if self.access_token is None and 'refresh_token' not in request_args['post_data']:
                # If the API returns 'ok' false, attempt to refresh the client's access token
                self.refresh_access_token()
                # If token refresh was successful, retry the original API request
                return self.__post_http_request(
                    self.access_token,
                    request_args
                )
        return res

    def refresh_access_token(self):
        """
        Refresh the client's OAUth access tokens
        https://api.slack.com/docs/rotating-and-refreshing-credentials
        """
        request_args = {
            'api_method': 'oauth.access',
            'post_data': {
                'token': self.refresh_token,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
        }

        response = self.__post_http_request(
            self.refresh_token, request_args)
        response_json = json.loads(response.text)

        # If Slack returned an updated access token, update the client, otherwise
        # raise SlackClientError exception with the error returned from the API
        if (response_json['ok']):
            # Update the client's access token and expiration timestamp
            self.client.update_client_tokens(
                response_json['team_id'],
                response_json['access_token'],
                response_json['expires_in']
            )
            # Call the developer's token update callback
            update_args = {
                'team_id': response_json['team_id'],
                'access_token': response_json['access_token'],
                'expires_in': response_json['expires_in']
            }
            self.refresh_callback(update_args)
            return response_json
        else:
            raise SlackClientError(response_json['error'])
