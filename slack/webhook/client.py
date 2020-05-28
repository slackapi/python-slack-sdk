import json
import logging
from http.client import HTTPResponse
from typing import Dict, Union
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from slack.errors import SlackRequestError
from .webhook_response import WebhookResponse
from ..web import convert_bool_to_0_or_1, get_user_agent
from ..web.classes.blocks import Block


class WebhookClient:
    logger = logging.getLogger(__name__)

    def __init__(
        self, url: str, default_headers: Dict[str, str] = {},
    ):
        """urllib-based API client.
        :param default_headers: request headers to add to all requests
        """
        self.url = url
        self.default_headers = default_headers

    def send(
        self, body: Dict[str, any], additional_headers: Dict[str, str] = {},
    ) -> WebhookResponse:
        """Performs a Slack API request and returns the result.
        :param url: a complete URL (e.g., https://hooks.slack.com/XXX)
        :param json_body: json data structure (it's still a dict at this point),
            if you give this argument, body_params and files will be skipped
        :param body_params: form params
        :param additional_headers: request headers to append
        :return: API response
        """

        body = convert_bool_to_0_or_1(body)
        self._parse_blocks(body)
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(
                f"Slack API Request - url: {self.url}, "
                f"body: {body}, "
                f"additional_headers: {additional_headers}"
            )

        request_headers = self._build_request_headers(
            has_json=json is not None, additional_headers=additional_headers,
        )
        args = {
            "headers": request_headers,
            "body": body,
        }
        return self._perform_http_request(url=self.url, args=args)

    def _perform_http_request(
        self, *, url: str, args: Dict[str, Dict[str, any]]
    ) -> WebhookResponse:
        """Performs an HTTP request and parses the response.
        :param url: a complete URL (e.g., https://www.slack.com/api/chat.postMessage)
        :param args: args has "headers", "data", "params", and "json"
            "headers": Dict[str, str]
            "params": Dict[str, str],
            "json": Dict[str, any],
        :return: a tuple (HTTP response and its body)
        """
        headers = args["headers"]
        body = json.dumps(args["body"]).encode("utf-8")
        headers["Content-Type"] = "application/json;charset=utf-8"

        try:
            if url.lower().startswith("http"):
                req = Request(method="POST", url=url, data=body, headers=headers)
            else:
                raise SlackRequestError(f"Invalid URL detected: {url}")
            resp: HTTPResponse = urlopen(req)
            charset = resp.headers.get_content_charset() or "utf-8"
            return WebhookResponse(
                url=self.url,
                status_code=resp.status,
                body=resp.read().decode(charset),
                headers=resp.headers,
            )
        except HTTPError as e:
            charset = e.headers.get_content_charset() or "utf-8"
            resp = WebhookResponse(
                url=self.url,
                status_code=e.code,
                body=e.read().decode(charset),
                headers=e.headers,
            )
            if e.code == 429:
                resp.headers["Retry-After"] = resp.headers["retry-after"]
            return resp

        except Exception as err:
            self.logger.error(f"Failed to send a request to Slack API server: {err}")
            raise err

    def _build_request_headers(
        self, has_json: bool, additional_headers: dict,
    ):
        headers = {
            "User-Agent": get_user_agent(),
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        headers.update(self.default_headers)
        if additional_headers:
            headers.update(additional_headers)
        if has_json:
            headers.update({"Content-Type": "application/json;charset=utf-8"})
        return headers

    @staticmethod
    def _parse_blocks(body):
        blocks = body.get("blocks", None)

        def to_dict(b: Union[Dict, Block]):
            if isinstance(b, Block):
                return b.to_dict()
            return b

        if blocks is not None and isinstance(blocks, list):
            dict_blocks = [to_dict(b) for b in blocks]
            body.update({"blocks": dict_blocks})
