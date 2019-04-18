"""A Python module for iteracting with Slack's Web API."""

# Standard Imports
from urllib.parse import urljoin
import platform
import sys
import logging
import json as jsonlib
import asyncio

# ThirdParty Imports
import aiohttp

# Internal Imports
from slack.web.slack_response import SlackResponse
import slack.version as v
import slack.errors as e


class BaseClient:
    BASE_URL = "https://www.slack.com/api/"

    def __init__(
        self,
        token=None,
        base_url=BASE_URL,
        proxies=None,
        timeout=30,
        loop=None,
        ssl=None,
        run_async=False,
        use_session=True,
    ):
        self.token = token
        self.base_url = base_url
        self.proxies = proxies or {}
        self.timeout = timeout
        self.ssl = ssl
        self.run_async = run_async
        self._logger = logging.getLogger(__name__)
        self._event_loop = loop or asyncio.get_event_loop()
        self._session = None
        if use_session:
            self._event_loop.run_until_complete(self._set_session())

    def __del__(self):
        """Ensures the session is closed when object is destroyed."""
        if self._session is not None and self._event_loop is not None:
            # FYI: self._event_loop is already closed at this point.
            asyncio.get_event_loop().run_until_complete(self._session.close())

    async def _set_session(self):
        self._session = aiohttp.ClientSession()

    def api_call(
        self,
        api_method,
        http_verb="POST",
        files=None,
        data=None,
        params=None,
        json=None,
    ):
        """Create a request and execute the API call to Slack.

        Args:
            api_method (str): The target Slack API method.
                e.g. 'chat.postMessage'
            http_verb (str): HTTP Verb. e.g. 'POST'
            files (dict): Files to multipart upload.
                e.g. {filename: fileobject}
            data: The body to attach to the request. If a dictionary is
                provided, form-encoding will take place.
                e.g. {'key1': 'value1', 'key2': 'value2'}
            params (dict): The URL parameters to append to the URL.
                e.g. {'key1': 'value1', 'key2': 'value2'}
            json (dict): JSON for the body to attach to the request
                (if files or data is not specified).
                e.g. {'key1': 'value1', 'key2': 'value2'}

        Returns:
            (SlackResponse)
                The server's response to an HTTP request. Data
                from the response can be accessed like a dict.
                If the response included 'next_cursor' it can
                be iterated on to execute subsequent requests.

        Raises:
            SlackApiError: The following Slack API call failed:
                'chat.postMessage'.
            SlackRequestError: Json data can only be submitted as
                POST requests.
        """
        if json is not None and http_verb != "POST":
            msg = "Json data can only be submitted as POST requests."
            raise e.SlackRequestError(msg)

        api_url = self._get_url(api_method)
        has_json = json is not None
        has_files = files is not None
        headers = self._get_headers(has_json, has_files)
        encoded_data = self._encode_data(data)

        req_args = {
            "headers": headers,
            # "files": files,
            "data": encoded_data,
            "params": params,
            "json": json,
            "ssl": self.ssl,
        }

        self._logger.debug(
            "Sending a '%s' request to '%s' with the following data: %s",
            http_verb,
            api_url,
            req_args,
        )

        req_future = asyncio.ensure_future(
            self._send(http_verb=http_verb, api_url=api_url, req_args=req_args),
            loop=self._event_loop,
        )

        res_future = asyncio.ensure_future(
            self._get_response(http_verb, api_url, req_args, req_future),
            loop=self._event_loop,
        )

        if self.run_async or self._event_loop.is_running():
            return res_future

        return self._event_loop.run_until_complete(res_future)

    async def _get_response(self, http_verb, api_url, req_args, request_future):
        response = await request_future
        data = {
            "client": self,
            "http_verb": http_verb,
            "api_url": api_url,
            "req_args": req_args,
            "data": response.get("data", {}),
            "headers": response.get("headers", {}),
            "status_code": response.get("status_code", None),
        }
        return SlackResponse(**data).validate()

    def _get_url(self, api_method):
        """Joins the base Slack URL and an API method to form an absolute URL.

        Args:
            api_method (str): The Slack Web API method. e.g. 'chat.postMessage'

        Returns:
            The absolute API URL.
                e.g. 'https://www.slack.com/api/chat.postMessage'
        """
        return urljoin(self.base_url, api_method)

    def _get_headers(self, has_json, has_files):
        """Contructs the headers need for a request.

        Args:
            has_json (bool): Whether or not the request has json.
            has_files (bool): Whether or not the request has files.

        Returns:
            The headers dictionary.
                e.g. {
                    'Content-Type': 'application/json;charset=utf-8',
                    'Authorization': 'Bearer xoxb-1234-1243',
                    'user-agent': 'Python/3.6 slack/2.0.0 Darwin/17.7.0'
                }
        """
        headers = {
            "user-agent": self._get_user_agent(),
            "Authorization": "Bearer {}".format(self.token),
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        if has_json:
            headers.update({"Content-Type": "application/json;charset=utf-8"})

        # if has_files:
        #     # These are set automatically by the requests library.
        #     headers.pop("Content-Type", None)

        # TODO: Open an issue with the requests library.
        # The json argument already sets the Content-Type to 'application/json'.
        # But because we also need send the charset we have to explicitly define everything.
        # We should ask them if it makes sense for the requests library to handle this.
        return headers

    async def _send(self, http_verb, api_url, req_args):
        """Sends the request out for transmission.

        Args:
            http_verb (str): The HTTP verb. e.g. 'GET' or 'POST'.
            api_url (str): The Slack API url. e.g. 'https://slack.com/api/chat.postMessage'
            req_args (dict): The request arguments to be attached to the request.
            e.g.
            {
                json: {
                    'attachments': [{"pretext": "pre-hello", "text": "text-world"}],
                    'channel': '#random'
                }
            }
        """
        async with self._session or aiohttp.ClientSession() as session:
            async with session.request(http_verb, api_url, **req_args) as res:
                response = {}
                response["data"] = await res.json()
                response["headers"] = res.headers
                response["status_code"] = res.status

                return response

    @staticmethod
    def _encode_data(data):
        """Serializes any 'list' or 'dict' values found in 'data'
        into a JSON-encoded string.

        Why do this? Some Slack methods feature arguments that accept an
        associative JSON array. Encoding this data ensures Slack receives it
        in the expected format.

        Note:
            This method is only required for those not using the json
            argument in api_call.

        Args:
            data (dict): The body to be attached to the request.
            e.g.
            {
                'attachments': [{"pretext": "pre-hello", "text": "text-world"}],
                'channel': '#random'
            }
        Returns:
            data (dict): The same body but the attachments array encoded into a string.
            e.g.
            {
                'attachments': '[{"pretext": "pre-hello", "text": "text-world"}]',
                'channel': '#random'
            }
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    data[key] = jsonlib.dumps(value)
        return data

    @staticmethod
    def _get_user_agent():
        """Construct the user-agent header with the package info,
        Python version and OS version.

        Returns:
            The user agent string.
            e.g. 'Python/3.6.7 slack/2.0.0 Darwin/17.7.0'
        """
        # __name__ returns all classes, we only want the client
        client = "{0}/{1}".format(__name__.split(".")[0], v.__version__)
        python_version = "Python/{v.major}.{v.minor}.{v.micro}".format(
            v=sys.version_info
        )
        system_info = "{0}/{1}".format(platform.system(), platform.release())
        user_agent_string = " ".join([python_version, client, system_info])
        return user_agent_string
