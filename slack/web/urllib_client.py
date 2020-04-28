import copy
import io
import json
import logging
import mimetypes
import uuid
from http.client import HTTPResponse
from typing import BinaryIO, Dict, List, Union
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from slack.web import get_user_agent, show_2020_01_deprecation, convert_bool_to_0_or_1
from slack.web.slack_response import SlackResponse


class HttpErrorResponse(object):
    pass


class UrllibWebClient:
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        *,
        token: str = None,
        default_headers: Dict[str, str] = dict(),
        # Not type here to avoid ImportError: cannot import name 'WebClient' from partially initialized module
        # 'slack.web.client' (most likely due to a circular import
        web_client=None,
    ):
        """urllib-based API client.

        :param token: Slack API Token (either bot token or user token)
        :param default_headers: request headers to add to all requests
        :param web_client: WebClient instance for pagination
        """
        self.token = token
        self.default_headers = default_headers
        self.web_client = web_client

    def api_call(
        self,
        *,
        token: str = None,
        url: str,
        query_params: Dict[str, str] = dict(),
        json_body: Dict = dict(),
        body_params: Dict[str, str] = dict(),
        files: Dict[str, io.BytesIO] = dict(),
        additional_headers: Dict[str, str] = dict(),
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

        show_2020_01_deprecation(self._to_api_method(url))

        files_to_close: List[BinaryIO] = []
        try:
            # True/False -> "1"/"0"
            query_params = convert_bool_to_0_or_1(query_params)
            body_params = convert_bool_to_0_or_1(body_params)

            if self.logger.level <= logging.DEBUG:
                self.logger.debug(
                    f"Slack API Request - url: {url}, "
                    f"query_params: {query_params}, "
                    f"json_body: {json_body}, "
                    f"body_params: {body_params}, "
                    f"files: {files}, "
                    f"additional_headers: {additional_headers}"
                )

            request_data = {}
            if files:
                if body_params:
                    for k, v in body_params.items():
                        request_data.update({k: v})

                for k, v in files.items():
                    if isinstance(v, str):
                        f: BinaryIO = open(v.encode("ascii", "ignore"), "rb")
                        files_to_close.append(f)
                        request_data.update({k: f})
                    else:
                        request_data.update({k: v})

            request_headers = self._build_request_headers(
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

            response, response_body = self._perform_http_request(
                url=url, args=request_args
            )
            if response_body:
                response_body_data: dict = json.loads(response_body)
            else:
                response_body_data: dict = None

            if query_params:
                all_params = copy.copy(body_params)
                all_params.update(query_params)
            else:
                all_params = body_params
            request_args["params"] = all_params  # for backward-compatibility
            return SlackResponse(
                client=self.web_client,
                http_verb="POST",  # you can use POST method for all the Web APIs
                api_url=url,
                req_args=request_args,
                data=response_body_data,
                headers=dict(response.headers),
                status_code=response.status,
                use_sync_aiohttp=False,
            ).validate()
        finally:
            for f in files_to_close:
                if not f.closed:
                    f.close()

    def _perform_http_request(
        self, *, url: str, args: Dict[str, Dict[str, any]]
    ) -> (Union[HTTPResponse, HttpErrorResponse], str):
        """Performs an HTTP request and parses the response.

        :param url: a complete URL (e.g., https://www.slack.com/api/chat.postMessage)
        :param args: args has "headers", "data", "params", and "json"
            "headers": Dict[str, str]
            "data": Dict[str, any]
            "params": Dict[str, str],
            "json": Dict[str, any],
        :return: a tuple (HTTP response and its body)
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
            headers["Content-Type"] = "application/x-www-form-urlencoded;charset=utf-8"
        else:
            body = None

        if isinstance(body, str):
            body = body.encode("utf-8")

        try:
            # NOTE: Intentionally ignore the `http_verb` here
            # Slack APIs accepts any API method requests with POST methods
            req = Request(method="POST", url=url, data=body, headers=headers)
            resp: HTTPResponse = urlopen(req)
            charset = resp.headers.get_content_charset()
            body: str = resp.read().decode(charset)  # read the response body here
            return resp, body
        except HTTPError as e:
            resp: HttpErrorResponse = HttpErrorResponse()
            resp.status = e.code
            resp.reason = e.reason
            resp.headers = e.headers
            charset = resp.headers.get_content_charset()
            body: str = e.read().decode(charset)  # read the response body here
            if e.code == 429:
                # for compatibility with aiohttp
                resp.headers["Retry-After"] = resp.headers["retry-after"]

            return resp, body

        except Exception as err:
            self.logger.error(f"Failed to send a request to Slack API server: {err}")
            raise err

    def _build_request_headers(
        self, token: str, has_json: bool, has_files: bool, additional_headers: dict,
    ):
        headers = {
            "User-Agent": get_user_agent(),
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        headers.update(self.default_headers)
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

    def _to_api_method(self, url: str):
        if url:
            elements = url.split("/")
            if elements and len(elements) > 0:
                return elements[len(elements) - 1].split("?", 1)[0]
        return None
