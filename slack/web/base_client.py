"""A Python module for iteracting with Slack's Web API."""

# Standard Imports
from urllib.parse import urljoin
import platform
import sys
import logging
import asyncio
import functools

# ThirdParty Imports
import aiohttp

# Internal Imports
from slack.web.slack_response import SlackResponse
import slack.version as ver
import slack.errors as err


def xoxp_token_only(api_method):
    """Ensures that an xoxp token is used when the specified method is called.

    Args:
        api_method (func): The api method that only works with xoxp tokens.
    Raises:
        BotUserAccessError: If the API method is called with a Bot User OAuth Access Token.
    """

    # NOTE: Intellisense docstrings do not follow functools.wraps() semantics.
    # https://github.com/Microsoft/vscode-python/issues/2596
    @functools.wraps(api_method)
    def xoxp_token_only_decorator(*args, **kwargs):
        client = args[0]
        # The first argument is 'slack.web.client.WebClient' aka 'self'.
        if client.token.startswith("xoxb"):
            method_name = api_method.__name__
            msg = "The API method '{}' cannot be called with a Bot Token.".format(
                method_name
            )
            raise err.BotUserAccessError(msg)
        return api_method(*args, **kwargs)

    return xoxp_token_only_decorator


class BaseClient:
    BASE_URL = "https://www.slack.com/api/"

    def __init__(
        self,
        token,
        base_url=BASE_URL,
        timeout=30,
        loop=None,
        ssl=None,
        proxy=None,
        run_async=False,
        use_session=True,
    ):
        self.token = token
        self.base_url = base_url
        self.timeout = timeout
        self.ssl = ssl
        self.proxy = proxy
        self.run_async = run_async
        self.use_session = use_session
        self._logger = logging.getLogger(__name__)
        self._event_loop = loop
        self._session = None

    def __del__(self):
        """Ensures the session is closed when object is destroyed."""
        if self._session and not self._session.closed:
            asyncio.get_event_loop().run_until_complete(self._session.close())

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
                e.g. {imageORfile: file_objectORfile_path}
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
            msg = "Json data can only be submitted as POST requests. GET requests should use the 'params' argument."
            raise err.SlackRequestError(msg)

        api_url = self._get_url(api_method)
        headers = {
            "User-Agent": self._get_user_agent(),
            "Authorization": "Bearer {}".format(self.token),
        }
        if files is not None:
            form_data = aiohttp.FormData()
            for k, v in files.items():
                if isinstance(v, str):
                    form_data.add_field(k, open(v, "rb"))
                else:
                    form_data.add_field(k, v)

            if data is not None:
                for k, v in data.items():
                    form_data.add_field(k, str(v))

            data = form_data

        req_args = {
            "headers": headers,
            "data": data,
            "params": params,
            "json": json,
            "ssl": self.ssl,
            "proxy": self.proxy,
        }

        if self.run_async:
            return asyncio.ensure_future(
                self._send(http_verb=http_verb, api_url=api_url, req_args=req_args),
                loop=self._event_loop,
            )

        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)
        return self._event_loop.run_until_complete(
            self._send(http_verb=http_verb, api_url=api_url, req_args=req_args)
        )

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

    async def _get_session(self):
        if self.use_session:
            if not self._session or self._session.closed:
                self._session = aiohttp.ClientSession()
            return self._session
        return aiohttp.ClientSession()

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
        session = await self._get_session()
        res = await session.request(http_verb, api_url, **req_args)
        data = {
            "client": self,
            "http_verb": http_verb,
            "api_url": api_url,
            "req_args": req_args,
            "data": await res.json(),
            "headers": res.headers,
            "status_code": res.status,
        }
        return SlackResponse(**data).validate()

    @staticmethod
    def _get_user_agent():
        """Construct the user-agent header with the package info,
        Python version and OS version.

        Returns:
            The user agent string.
            e.g. 'Python/3.6.7 slack/2.0.0 Darwin/17.7.0'
        """
        # __name__ returns all classes, we only want the client
        client = "{0}/{1}".format(__name__.split(".")[0], ver.__version__)
        python_version = "Python/{v.major}.{v.minor}.{v.micro}".format(
            v=sys.version_info
        )
        system_info = "{0}/{1}".format(platform.system(), platform.release())
        user_agent_string = " ".join([python_version, client, system_info])
        return user_agent_string
