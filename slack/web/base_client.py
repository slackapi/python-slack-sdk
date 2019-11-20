"""A Python module for interacting with Slack's Web API."""

# Standard Imports
from urllib.parse import urljoin
import platform
import sys
import logging
import asyncio
from typing import Optional, Union
import hashlib
import hmac

# ThirdParty Imports
import aiohttp
from aiohttp import FormData, BasicAuth

# Internal Imports
from slack.web.slack_response import SlackResponse
import slack.version as ver
import slack.errors as err


class BaseClient:
    BASE_URL = "https://www.slack.com/api/"

    def __init__(
        self,
        token=None,
        base_url=BASE_URL,
        timeout=30,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        ssl=None,
        proxy=None,
        run_async=False,
        session=None,
        headers: Optional[dict] = None,
    ):
        self.token = token
        self.base_url = base_url
        self.timeout = timeout
        self.ssl = ssl
        self.proxy = proxy
        self.run_async = run_async
        self.session = session
        self.headers = headers or {}
        self._logger = logging.getLogger(__name__)
        self._event_loop = loop

    def _get_event_loop(self):
        """Retrieves the event loop or creates a new one."""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def _get_headers(self, has_json, has_files, request_specific_headers):
        """Contructs the headers need for a request.
        Args:
            has_json (bool): Whether or not the request has json.
            has_files (bool): Whether or not the request has files.
            request_specific_headers (dict): Additional headers specified by the user for a specific request.

        Returns:
            The headers dictionary.
                e.g. {
                    'Content-Type': 'application/json;charset=utf-8',
                    'Authorization': 'Bearer xoxb-1234-1243',
                    'User-Agent': 'Python/3.6.8 slack/2.1.0 Darwin/17.7.0'
                }
        """
        final_headers = {
            "User-Agent": self._get_user_agent(),
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }

        if self.token:
            final_headers.update({"Authorization": "Bearer {}".format(self.token)})

        # Merge headers specified at client initialization.
        final_headers.update(self.headers)

        # Merge headers specified for a specific request. i.e. oauth.access
        final_headers.update(request_specific_headers)

        if has_json:
            final_headers.update({"Content-Type": "application/json;charset=utf-8"})

        if has_files:
            # These are set automatically by the aiohttp library.
            final_headers.pop("Content-Type", None)

        return final_headers

    def api_call(
        self,
        api_method: str,
        *,
        http_verb: str = "POST",
        files: dict = None,
        data: Union[dict, FormData] = None,
        params: dict = None,
        json: dict = None,
        headers: dict = {},
        auth: dict = None,
    ) -> Union[asyncio.Future, SlackResponse]:
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
        has_json = json is not None
        has_files = files is not None
        if has_json and http_verb != "POST":
            msg = "Json data can only be submitted as POST requests. GET requests should use the 'params' argument."
            raise err.SlackRequestError(msg)

        api_url = self._get_url(api_method)

        if auth:
            auth = BasicAuth(auth["client_id"], auth["client_secret"])

        req_args = {
            "headers": self._get_headers(has_json, has_files, headers),
            "data": data,
            "files": files,
            "params": params,
            "json": json,
            "ssl": self.ssl,
            "proxy": self.proxy,
            "auth": auth,
        }

        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        future = asyncio.ensure_future(
            self._send(http_verb=http_verb, api_url=api_url, req_args=req_args),
            loop=self._event_loop,
        )

        if self.run_async:
            return future

        return self._event_loop.run_until_complete(future)

    def _get_url(self, api_method):
        """Joins the base Slack URL and an API method to form an absolute URL.

        Args:
            api_method (str): The Slack Web API method. e.g. 'chat.postMessage'

        Returns:
            The absolute API URL.
                e.g. 'https://www.slack.com/api/chat.postMessage'
        """
        return urljoin(self.base_url, api_method)

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
        Returns:
            The response parsed into a SlackResponse object.
        """
        open_files = []
        files = req_args.pop("files", None)
        if files is not None:
            for k, v in files.items():
                if isinstance(v, str):
                    f = open(v.encode("ascii", "ignore"), "rb")
                    open_files.append(f)
                    req_args["data"].update({k: f})
                else:
                    req_args["data"].update({k: v})

        res = await self._request(
            http_verb=http_verb, api_url=api_url, req_args=req_args
        )

        for f in open_files:
            f.close()

        data = {
            "client": self,
            "http_verb": http_verb,
            "api_url": api_url,
            "req_args": req_args,
        }
        return SlackResponse(**{**data, **res}).validate()

    async def _request(self, *, http_verb, api_url, req_args):
        """Submit the HTTP request with the running session or a new session.
        Returns:
            A dictionary of the response data.
        """
        session = None
        use_running_session = self.session and not self.session.closed
        if use_running_session:
            session = self.session
        else:
            session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                auth=req_args.pop("auth", None),
            )

        response = None
        async with session.request(http_verb, api_url, **req_args) as res:
            data = {}
            try:
                data = await res.json()
            except aiohttp.ContentTypeError:
                self._logger.debug(
                    f"No response data returned from the following API call: {api_url}."
                )
            response = {"data": data, "headers": res.headers, "status_code": res.status}

        if not use_running_session:
            await session.close()
        return response

    @staticmethod
    def _get_user_agent():
        """Construct the user-agent header with the package info,
        Python version and OS version.

        Returns:
            The user agent string.
            e.g. 'Python/3.6.7 slackclient/2.0.0 Darwin/17.7.0'
        """
        # __name__ returns all classes, we only want the client
        client = "{0}/{1}".format("slackclient", ver.__version__)
        python_version = "Python/{v.major}.{v.minor}.{v.micro}".format(
            v=sys.version_info
        )
        system_info = "{0}/{1}".format(platform.system(), platform.release())
        user_agent_string = " ".join([python_version, client, system_info])
        return user_agent_string

    @staticmethod
    def validate_slack_signature(
        *, signing_secret: str, data: str, timestamp: str, signature: str
    ) -> bool:
        """
        Slack creates a unique string for your app and shares it with you. Verify
        requests from Slack with confidence by verifying signatures using your
        signing secret.

        On each HTTP request that Slack sends, we add an X-Slack-Signature HTTP
        header. The signature is created by combining the signing secret with the
        body of the request we're sending using a standard HMAC-SHA256 keyed hash.

        https://api.slack.com/docs/verifying-requests-from-slack#how_to_make_a_request_signature_in_4_easy_steps__an_overview

        Args:
            signing_secret: Your application's signing secret, available in the
                Slack API dashboard
            data: The raw body of the incoming request - no headers, just the body.
            timestamp: from the 'X-Slack-Request-Timestamp' header
            signature: from the 'X-Slack-Signature' header - the calculated signature
                should match this.

        Returns:
            True if signatures matches
        """
        format_req = str.encode(f"v0:{timestamp}:{data}")
        encoded_secret = str.encode(signing_secret)
        request_hash = hmac.new(encoded_secret, format_req, hashlib.sha256).hexdigest()
        calculated_signature = f"v0={request_hash}"
        return hmac.compare_digest(calculated_signature, signature)
