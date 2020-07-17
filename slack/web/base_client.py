"""A Python module for interacting with Slack's Web API."""

import asyncio
import copy
import hashlib
import hmac
import io
import json
import logging
import mimetypes
import os
import re
import uuid
import warnings
from http.client import HTTPResponse
from typing import BinaryIO, Dict, List
from typing import Optional, Union
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import aiohttp
from aiohttp import FormData, BasicAuth

import slack.errors as err
from slack.errors import SlackRequestError
from slack.web import convert_bool_to_0_or_1, get_user_agent
from slack.web.classes.attachments import Attachment
from slack.web.classes.blocks import Block
from slack.web.slack_response import SlackResponse


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
        use_sync_aiohttp=False,
        session=None,
        headers: Optional[dict] = None,
    ):
        self.token = None if token is None else token.strip()
        self.base_url = base_url
        self.timeout = timeout
        self.ssl = ssl
        self.proxy = proxy
        self.run_async = run_async
        self.use_sync_aiohttp = use_sync_aiohttp
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

    def api_call(
        self,
        api_method: str,
        *,
        http_verb: str = "POST",
        files: dict = None,
        data: Union[dict, FormData] = None,
        params: dict = None,
        json: dict = None,
        headers: dict = None,
        auth: dict = None,
    ) -> Union[asyncio.Future, SlackResponse]:
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

        if self.run_async or self.use_sync_aiohttp:

            if self._event_loop is None:
                self._event_loop = self._get_event_loop()

            future = asyncio.ensure_future(
                self._send(http_verb=http_verb, api_url=api_url, req_args=req_args),
                loop=self._event_loop,
            )
            if self.run_async:
                return future
            if self.use_sync_aiohttp:
                # Using this is no longer recommended - just keep this for backward-compatibility
                return self._event_loop.run_until_complete(future)
        else:
            return self._sync_send(api_url=api_url, req_args=req_args)

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
            The response parsed into a SlackResponse object.
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
            "use_sync_aiohttp": self.use_sync_aiohttp,
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

    # =================================================================
    # urllib based WebClient
    # =================================================================

    def _sync_send(self, api_url, req_args):
        params = req_args["params"] if "params" in req_args else None
        data = req_args["data"] if "data" in req_args else None
        files = req_args["files"] if "files" in req_args else None
        _json = req_args["json"] if "json" in req_args else None
        headers = req_args["headers"] if "headers" in req_args else None
        token = params.get("token") if params and "token" in params else None
        auth = (
            req_args["auth"] if "auth" in req_args else None
        )  # Basic Auth for oauth.v2.access / oauth.access
        if auth is not None:
            if isinstance(auth, BasicAuth):
                headers["Authorization"] = auth.encode()
            elif isinstance(auth, str):
                headers["Authorization"] = auth
            else:
                self._logger.warning(
                    f"As the auth: {auth}: {type(auth)} is unsupported, skipped"
                )

        body_params = {}
        if params:
            body_params.update(params)
        if data:
            body_params.update(data)

        return self._urllib_api_call(
            token=token,
            url=api_url,
            query_params={},
            body_params=body_params,
            files=files,
            json_body=_json,
            additional_headers=headers,
        )

    def _request_for_pagination(self, api_url, req_args) -> Dict[str, any]:
        """This method is supposed to be used only for SlackResponse pagination

        You can paginate using Python's for iterator as below:

          for response in client.conversations_list(limit=100):
              # do something with each response here
        """
        response = self._perform_urllib_http_request(url=api_url, args=req_args)
        return {
            "status_code": int(response["status"]),
            "headers": dict(response["headers"]),
            "data": json.loads(response["body"]),
        }

    def _urllib_api_call(
        self,
        *,
        token: str = None,
        url: str,
        query_params: Dict[str, str] = {},
        json_body: Dict = {},
        body_params: Dict[str, str] = {},
        files: Dict[str, io.BytesIO] = {},
        additional_headers: Dict[str, str] = {},
    ) -> SlackResponse:
        """Performs a Slack API request and returns the result.

        :param token: Slack API Token (either bot token or user token)
        :param url: a complete URL (e.g., https://www.slack.com/api/chat.postMessage)
        :param query_params: query string
        :param json_body: json data structure (it's still a dict at this point),
            if you give this argument, body_params and files will be skipped
        :param body_params: form params
        :param files: files to upload
        :param additional_headers: request headers to append
        :return: API response
        """

        files_to_close: List[BinaryIO] = []
        try:
            # True/False -> "1"/"0"
            query_params = convert_bool_to_0_or_1(query_params)
            body_params = convert_bool_to_0_or_1(body_params)

            if self._logger.level <= logging.DEBUG:

                def convert_params(values: dict) -> dict:
                    if not values or not isinstance(values, dict):
                        return {}
                    return {
                        k: ("(bytes)" if isinstance(v, bytes) else v)
                        for k, v in values.items()
                    }

                headers = {
                    k: "(redacted)" if k.lower() == "authorization" else v
                    for k, v in additional_headers.items()
                }
                self._logger.debug(
                    f"Sending a request - url: {url}, "
                    f"query_params: {convert_params(query_params)}, "
                    f"body_params: {convert_params(body_params)}, "
                    f"files: {convert_params(files)}, "
                    f"json_body: {json_body}, "
                    f"headers: {headers}"
                )

            request_data = {}
            if files is not None and isinstance(files, dict) and len(files) > 0:
                if body_params:
                    for k, v in body_params.items():
                        request_data.update({k: v})

                for k, v in files.items():
                    if isinstance(v, str):
                        f: BinaryIO = open(v.encode("utf-8", "ignore"), "rb")
                        files_to_close.append(f)
                        request_data.update({k: f})
                    elif isinstance(v, bytearray):
                        request_data.update({k: io.BytesIO(v)})
                    else:
                        request_data.update({k: v})

            request_headers = self._build_urllib_request_headers(
                token=token or self.token,
                has_json=json is not None,
                has_files=files is not None,
                additional_headers=additional_headers,
            )
            request_args = {
                "headers": request_headers,
                "data": request_data,
                "params": body_params,
                "files": files,
                "json": json_body,
            }
            if query_params:
                q = urlencode(query_params)
                url = f"{url}&{q}" if "?" in url else f"{url}?{q}"

            response = self._perform_urllib_http_request(url=url, args=request_args)
            if response.get("body", None):
                try:
                    response_body_data: dict = json.loads(response["body"])
                except json.decoder.JSONDecodeError as e:
                    message = f"Failed to parse the response body: {str(e)}"
                    raise err.SlackApiError(message, response)
            else:
                response_body_data: dict = None

            if query_params:
                all_params = copy.copy(body_params)
                all_params.update(query_params)
            else:
                all_params = body_params
            request_args["params"] = all_params  # for backward-compatibility

            return SlackResponse(
                client=self,
                http_verb="POST",  # you can use POST method for all the Web APIs
                api_url=url,
                req_args=request_args,
                data=response_body_data,
                headers=dict(response["headers"]),
                status_code=response["status"],
                use_sync_aiohttp=False,
            ).validate()
        finally:
            for f in files_to_close:
                if not f.closed:
                    f.close()

    def _perform_urllib_http_request(
        self, *, url: str, args: Dict[str, Dict[str, any]]
    ) -> Dict[str, any]:
        """Performs an HTTP request and parses the response.

        :param url: a complete URL (e.g., https://www.slack.com/api/chat.postMessage)
        :param args: args has "headers", "data", "params", and "json"
            "headers": Dict[str, str]
            "data": Dict[str, any]
            "params": Dict[str, str],
            "json": Dict[str, any],
        :return: dict {status: int, headers: Headers, body: str}
        """
        headers = args["headers"]
        if args["json"]:
            body = json.dumps(args["json"])
            headers["Content-Type"] = "application/json;charset=utf-8"
        elif args["data"]:
            boundary = f"--------------{uuid.uuid4()}"
            sep_boundary = b"\r\n--" + boundary.encode("ascii")
            end_boundary = sep_boundary + b"--\r\n"
            body = io.BytesIO()
            data = args["data"]
            for key, value in data.items():
                readable = getattr(value, "readable", None)
                if readable and value.readable():
                    filename = "Uploaded file"
                    name_attr = getattr(value, "name", None)
                    if name_attr:
                        filename = (
                            name_attr.decode("utf-8")
                            if isinstance(name_attr, bytes)
                            else name_attr
                        )
                    if "filename" in data:
                        filename = data["filename"]
                    mimetype = (
                        mimetypes.guess_type(filename)[0] or "application/octet-stream"
                    )
                    title = (
                        f'\r\nContent-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'
                        + f"Content-Type: {mimetype}\r\n"
                    )
                    value = value.read()
                else:
                    title = f'\r\nContent-Disposition: form-data; name="{key}"\r\n'
                    value = str(value).encode("utf-8")
                body.write(sep_boundary)
                body.write(title.encode("utf-8"))
                body.write(b"\r\n")
                body.write(value)

            body.write(end_boundary)
            body = body.getvalue()
            headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
            headers["Content-Length"] = len(body)
        elif args["params"]:
            body = urlencode(args["params"])
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            body = None

        if isinstance(body, str):
            body = body.encode("utf-8")

        # NOTE: Intentionally ignore the `http_verb` here
        # Slack APIs accepts any API method requests with POST methods
        try:
            # urllib not only opens http:// or https:// URLs, but also ftp:// and file://.
            # With this it might be possible to open local files on the executing machine
            # which might be a security risk if the URL to open can be manipulated by an external user.
            if url.lower().startswith("http"):
                req = Request(method="POST", url=url, data=body, headers=headers)
                if self.proxy is not None:
                    if isinstance(self.proxy, str):
                        host = re.sub("^https?://", "", self.proxy)
                        req.set_proxy(host, "http")
                        req.set_proxy(host, "https")
                    else:
                        raise SlackRequestError(
                            f"Invalid proxy detected: {self.proxy} must be a str value"
                        )

                resp: HTTPResponse = urlopen(
                    req, context=self.ssl, timeout=self.timeout
                )
                charset = resp.headers.get_content_charset()
                body: str = resp.read().decode(charset)  # read the response body here
                return {"status": resp.code, "headers": resp.headers, "body": body}
            raise SlackRequestError(f"Invalid URL detected: {url}")
        except HTTPError as e:
            resp = {"status": e.code, "headers": e.headers}
            if e.code == 429:
                # for compatibility with aiohttp
                resp["headers"]["Retry-After"] = resp["headers"]["retry-after"]

            charset = e.headers.get_content_charset()
            body: str = e.read().decode(charset)  # read the response body here
            resp["body"] = body
            return resp

        except Exception as err:
            self._logger.error(f"Failed to send a request to Slack API server: {err}")
            raise err

    def _build_urllib_request_headers(
        self, token: str, has_json: bool, has_files: bool, additional_headers: dict
    ):
        headers = {
            "User-Agent": get_user_agent(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        headers.update(self.headers)
        if token:
            headers.update({"Authorization": "Bearer {}".format(token)})
        if additional_headers:
            headers.update(additional_headers)
        if has_json:
            headers.update({"Content-Type": "application/json;charset=utf-8"})
        if has_files:
            # will be set afterwards
            headers.pop("Content-Type", None)
        return headers

    # =================================================================

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
        warnings.warn(
            "As this method is deprecated since slackclient 2.6.0, "
            "use `from slack.signature import SignatureVerifier` instead",
            DeprecationWarning,
        )
        format_req = str.encode(f"v0:{timestamp}:{data}")
        encoded_secret = str.encode(signing_secret)
        request_hash = hmac.new(encoded_secret, format_req, hashlib.sha256).hexdigest()
        calculated_signature = f"v0={request_hash}"
        return hmac.compare_digest(calculated_signature, signature)

    @staticmethod
    def _parse_web_class_objects(kwargs) -> None:
        def to_dict(obj: Union[Dict, Block, Attachment]):
            if isinstance(obj, Block):
                return obj.to_dict()
            if isinstance(obj, Attachment):
                return obj.to_dict()
            return obj

        blocks = kwargs.get("blocks", None)
        if blocks is not None and isinstance(blocks, list):
            dict_blocks = [to_dict(b) for b in blocks]
            kwargs.update({"blocks": dict_blocks})

        attachments = kwargs.get("attachments", None)
        if attachments is not None and isinstance(attachments, list):
            dict_attachments = [to_dict(a) for a in attachments]
            kwargs.update({"attachments": dict_attachments})

    @staticmethod
    def _update_call_participants(kwargs, users: Union[str, List[Dict[str, str]]]):
        if users is None:
            return

        if isinstance(users, list):
            kwargs.update({"users": json.dumps(users)})
        elif isinstance(users, str):
            kwargs.update({"users": users})
        else:
            raise SlackRequestError("users must be either str or List[Dict[str, str]]")


# https://api.slack.com/changelog/2020-01-deprecating-antecedents-to-the-conversations-api
deprecated_method_prefixes_2020_01 = [
    "channels.",
    "groups.",
    "im.",
    "mpim.",
    "admin.conversations.whitelist.",
]


def show_2020_01_deprecation(method_name: str):
    skip_deprecation = os.environ.get(
        "SLACKCLIENT_SKIP_DEPRECATION"
    )  # for unit tests etc.
    if skip_deprecation:
        return
    if not method_name:
        return

    matched_prefixes = [
        prefix
        for prefix in deprecated_method_prefixes_2020_01
        if method_name.startswith(prefix)
    ]
    if len(matched_prefixes) > 0:
        message = (
            f"{method_name} is deprecated. Please use the Conversations API instead. "
            "For more info, go to "
            "https://api.slack.com/changelog/2020-01-deprecating-antecedents-to-the-conversations-api"
        )
        warnings.warn(message)
