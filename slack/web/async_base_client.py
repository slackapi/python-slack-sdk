import asyncio
import json
import logging
from typing import Optional, Union
from urllib.parse import urljoin

import aiohttp
from aiohttp import FormData, BasicAuth

import slack.errors as err
from slack.web import convert_bool_to_0_or_1, get_user_agent
from slack.web.async_slack_response import AsyncSlackResponse
from slack.web.deprecation import show_2020_01_deprecation


class AsyncBaseClient:
    BASE_URL = "https://www.slack.com/api/"

    def __init__(
        self,
        token=None,
        base_url=BASE_URL,
        timeout=30,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        ssl=None,
        proxy=None,
        trust_env_in_session: bool = False,
        session: Optional[aiohttp.ClientSession] = None,
        headers: Optional[dict] = None,
    ):
        self.token = None if token is None else token.strip()
        self.base_url = base_url
        self.timeout = timeout
        self.ssl = ssl
        self.proxy = proxy
        self.session = session
        # https://github.com/slackapi/python-slackclient/issues/738
        self.trust_env_in_session = trust_env_in_session
        self.headers = headers or {}
        self._logger = logging.getLogger(__name__)
        self._event_loop = loop

    @staticmethod
    def _get_event_loop():
        """Retrieves the event loop or creates a new one."""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def _get_headers(
        self,
        *,
        token: Optional[str],
        has_json: bool,
        has_files: bool,
        request_specific_headers: Optional[dict],
    ):
        """Constructs the headers need for a request.
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
            "User-Agent": get_user_agent(),
            "Content-Type": "application/x-www-form-urlencoded",
        }

        if token:
            final_headers.update({"Authorization": "Bearer {}".format(token)})

        # Merge headers specified at client initialization.
        final_headers.update(self.headers)

        # Merge headers specified for a specific request. e.g. oauth.access
        if request_specific_headers:
            final_headers.update(request_specific_headers)

        if has_json:
            final_headers.update({"Content-Type": "application/json;charset=utf-8"})

        if has_files:
            # These are set automatically by the aiohttp library.
            final_headers.pop("Content-Type", None)

        return final_headers

    async def api_call(  # skipcq: PYL-R1710
        self,
        api_method: str,
        *,
        http_verb: str = "POST",
        files: dict = None,
        data: Union[dict, FormData] = None,
        params: dict = None,
        json: dict = None,  # skipcq: PYL-W0621
        headers: dict = None,
        auth: dict = None,
    ) -> AsyncSlackResponse:
        """Create a request and execute the API call to Slack.

        Args:
            api_method (str): The target Slack API method.
                e.g. 'chat.postMessage'
            http_verb (str): HTTP Verb. e.g. 'POST'
            files (dict): Files to multipart upload.
                e.g. {image OR file: file_object OR file_path}
            data: The body to attach to the request. If a dictionary is
                provided, form-encoding will take place.
                e.g. {'key1': 'value1', 'key2': 'value2'}
            params (dict): The URL parameters to append to the URL.
                e.g. {'key1': 'value1', 'key2': 'value2'}
            json (dict): JSON for the body to attach to the request
                (if files or data is not specified).
                e.g. {'key1': 'value1', 'key2': 'value2'}

        Returns:
            (AsyncSlackResponse)
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

        if data is not None and isinstance(data, dict):
            data = {k: v for k, v in data.items() if v is not None}
        if files is not None and isinstance(files, dict):
            files = {k: v for k, v in files.items() if v is not None}
        if params is not None and isinstance(params, dict):
            params = {k: v for k, v in params.items() if v is not None}

        token: Optional[str] = self.token
        if params is not None and "token" in params:
            token = params.pop("token")
        if json is not None and "token" in json:
            token = json.pop("token")
        req_args = {
            "headers": self._get_headers(
                token=token,
                has_json=has_json,
                has_files=has_files,
                request_specific_headers=headers,
            ),
            "data": data,
            "files": files,
            "params": params,
            "json": json,
            "ssl": self.ssl,
            "proxy": self.proxy,
            "auth": auth,
        }

        show_2020_01_deprecation(api_method)

        return await self._send(
            http_verb=http_verb, api_url=api_url, req_args=req_args,
        )

    def _get_url(self, api_method):
        """Joins the base Slack URL and an API method to form an absolute URL.

        Args:
            api_method (str): The Slack Web API method. e.g. 'chat.postMessage'

        Returns:
            The absolute API URL.
                e.g. 'https://www.slack.com/api/chat.postMessage'
        """
        return urljoin(self.base_url, api_method)

    # =================================================================
    # aiohttp based async WebClient
    # =================================================================

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
            The response parsed into a AsyncSlackResponse object.
        """
        open_files = []
        files = req_args.pop("files", None)
        if files is not None:
            for k, v in files.items():
                if isinstance(v, str):
                    f = open(v.encode("utf-8", "ignore"), "rb")
                    open_files.append(f)
                    req_args["data"].update({k: f})
                else:
                    req_args["data"].update({k: v})

        if "params" in req_args:
            # True/False -> "1"/"0"
            req_args["params"] = convert_bool_to_0_or_1(req_args["params"])

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
        return AsyncSlackResponse(**{**data, **res}).validate()

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
                trust_env=self.trust_env_in_session,
            )

        response = None
        try:
            async with session.request(http_verb, api_url, **req_args) as res:
                data = {}
                try:
                    data = await res.json()
                except aiohttp.ContentTypeError:
                    self._logger.debug(
                        f"No response data returned from the following API call: {api_url}."
                    )
                except json.decoder.JSONDecodeError as e:
                    message = f"Failed to parse the response body: {str(e)}"
                    raise err.SlackApiError(message, res)

                response = {
                    "data": data,
                    "headers": res.headers,
                    "status_code": res.status,
                }
        finally:
            if not use_running_session:
                await session.close()
        return response
