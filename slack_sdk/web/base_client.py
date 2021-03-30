"""A Python module for interacting with Slack's Web API."""

import copy
import hashlib
import hmac
import io
import json
import logging
import mimetypes
import urllib
import uuid
import warnings
from base64 import b64encode
from http.client import HTTPResponse
from ssl import SSLContext
from typing import BinaryIO, Dict, List
from typing import Optional, Union
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen, OpenerDirector, ProxyHandler, HTTPSHandler

import slack_sdk.errors as err
from slack_sdk.errors import SlackRequestError
from .deprecation import show_2020_01_deprecation
from .internal_utils import (
    convert_bool_to_0_or_1,
    get_user_agent,
    _get_url,
    _build_req_args,
    _build_unexpected_body_error_message,
)
from .slack_response import SlackResponse
from ..proxy_env_variable_loader import load_http_proxy_from_env


class BaseClient:
    BASE_URL = "https://www.slack.com/api/"

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = BASE_URL,
        timeout: int = 30,
        ssl: Optional[SSLContext] = None,
        proxy: Optional[str] = None,
        headers: Optional[dict] = None,
        user_agent_prefix: Optional[str] = None,
        user_agent_suffix: Optional[str] = None,
        # for Org-Wide App installation
        team_id: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.token = None if token is None else token.strip()
        self.base_url = base_url
        self.timeout = timeout
        self.ssl = ssl
        self.proxy = proxy
        self.headers = headers or {}
        self.headers["User-Agent"] = get_user_agent(
            user_agent_prefix, user_agent_suffix
        )
        self.default_params = {}
        if team_id is not None:
            self.default_params["team_id"] = team_id
        self._logger = logger if logger is not None else logging.getLogger(__name__)

        if self.proxy is None or len(self.proxy.strip()) == 0:
            env_variable = load_http_proxy_from_env(self._logger)
            if env_variable is not None:
                self.proxy = env_variable

    def api_call(  # skipcq: PYL-R1710
        self,
        api_method: str,
        *,
        http_verb: str = "POST",
        files: dict = None,
        data: Union[dict] = None,
        params: dict = None,
        json: dict = None,  # skipcq: PYL-W0621
        headers: dict = None,
        auth: dict = None,
    ) -> SlackResponse:
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
            headers (dict): Additional request headers
            auth (dict): A dictionary that consists of client_id and client_secret

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

        api_url = _get_url(self.base_url, api_method)
        headers = headers or {}
        headers.update(self.headers)
        req_args = _build_req_args(
            token=self.token,
            http_verb=http_verb,
            files=files,
            data=data,
            default_params=self.default_params,
            params=params,
            json=json,  # skipcq: PYL-W0621
            headers=headers,
            auth=auth,
            ssl=self.ssl,
            proxy=self.proxy,
        )

        show_2020_01_deprecation(api_method)
        return self._sync_send(api_url=api_url, req_args=req_args)

    # =================================================================
    # urllib based WebClient
    # =================================================================

    def _sync_send(self, api_url, req_args) -> SlackResponse:
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
            if isinstance(auth, str):
                headers["Authorization"] = auth
            elif isinstance(auth, dict):
                client_id, client_secret = auth["client_id"], auth["client_secret"]
                value = b64encode(
                    f"{client_id}:{client_secret}".encode("utf-8")
                ).decode("ascii")
                headers["Authorization"] = f"Basic {value}"
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

        Args:
            token: Slack API Token (either bot token or user token)
            url: Complete URL (e.g., https://www.slack.com/api/chat.postMessage)
            query_params: Query string
            json_body: JSON data structure (it's still a dict at this point),
                if you give this argument, body_params and files will be skipped
            body_params: Form body params
            files: Files to upload
            additional_headers: Request headers to append

        Returns:
            API response
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
                    elif isinstance(v, (bytearray, bytes)):
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
            body = response.get("body", None)  # skipcq: PTC-W0039
            response_body_data: Optional[Union[dict, bytes]] = body
            if body is not None and not isinstance(body, bytes):
                try:
                    response_body_data = json.loads(response["body"])
                except json.decoder.JSONDecodeError:
                    message = _build_unexpected_body_error_message(
                        response.get("body", "")
                    )
                    raise err.SlackApiError(message, response)

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
            ).validate()
        finally:
            for f in files_to_close:
                if not f.closed:
                    f.close()

    def _perform_urllib_http_request(
        self, *, url: str, args: Dict[str, Dict[str, any]]
    ) -> Dict[str, any]:
        """Performs an HTTP request and parses the response.

        Args:
            url: Complete URL (e.g., https://www.slack.com/api/chat.postMessage)
            args: args has "headers", "data", "params", and "json"
                "headers": Dict[str, str]
                "data": Dict[str, any]
                "params": Dict[str, str],
                "json": Dict[str, any],

        Returns:
            dict {status: int, headers: Headers, body: str}
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
            # (BAN-B310)
            if url.lower().startswith("http"):
                req = Request(method="POST", url=url, data=body, headers=headers)
                opener: Optional[OpenerDirector] = None
                if self.proxy is not None:
                    if isinstance(self.proxy, str):
                        opener = urllib.request.build_opener(
                            ProxyHandler({"http": self.proxy, "https": self.proxy}),
                            HTTPSHandler(context=self.ssl),
                        )
                    else:
                        raise SlackRequestError(
                            f"Invalid proxy detected: {self.proxy} must be a str value"
                        )

                # NOTE: BAN-B310 is already checked above
                resp: Optional[HTTPResponse] = None
                if opener:
                    resp = opener.open(req, timeout=self.timeout)  # skipcq: BAN-B310
                else:
                    resp = urlopen(  # skipcq: BAN-B310
                        req, context=self.ssl, timeout=self.timeout
                    )
                if resp.headers.get_content_type() == "application/gzip":
                    # admin.analytics.getFile
                    body: bytes = resp.read()
                    return {"status": resp.code, "headers": resp.headers, "body": body}

                charset = resp.headers.get_content_charset() or "utf-8"
                body: str = resp.read().decode(charset)  # read the response body here
                return {"status": resp.code, "headers": resp.headers, "body": body}
            raise SlackRequestError(f"Invalid URL detected: {url}")
        except HTTPError as e:
            resp = {"status": e.code, "headers": e.headers}
            if e.code == 429:
                # for compatibility with aiohttp
                resp["headers"]["Retry-After"] = resp["headers"]["retry-after"]

            # read the response body here
            charset = e.headers.get_content_charset() or "utf-8"
            body: str = e.read().decode(charset)
            resp["body"] = body
            return resp

        except Exception as err:
            self._logger.error(f"Failed to send a request to Slack API server: {err}")
            raise err

    def _build_urllib_request_headers(
        self, token: str, has_json: bool, has_files: bool, additional_headers: dict
    ) -> Dict[str, str]:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
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
