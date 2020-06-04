import json
import logging
import re
from http.client import HTTPResponse
from ssl import SSLContext
from typing import Dict, Union, List, Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from slack.errors import SlackRequestError
from .webhook_response import WebhookResponse
from ..web import convert_bool_to_0_or_1, get_user_agent
from ..web.classes.attachments import Attachment
from ..web.classes.blocks import Block


class WebhookClient:
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        url: str,
        timeout: int = 30,
        ssl: Optional[SSLContext] = None,
        proxy: Optional[str] = None,
        default_headers: Dict[str, str] = {},
    ):
        """API client for Incoming Webhooks and response_url
        :param url: a complete URL to send data (e.g., https://hooks.slack.com/XXX)
        :param timeout: request timeout (in seconds)
        :param ssl: ssl.SSLContext to use for requests
        :param proxy: proxy URL (e.g., localhost:9000, http://localhost:9000)
        :param default_headers: request headers to add to all requests
        """
        self.url = url
        self.timeout = timeout
        self.ssl = ssl
        self.proxy = proxy
        self.default_headers = default_headers

    def send(
        self,
        *,
        text: Optional[str] = None,
        attachments: Optional[List[Union[Dict[str, any], Attachment]]] = None,
        blocks: Optional[List[Union[Dict[str, any], Block]]] = None,
        response_type: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> WebhookResponse:
        """Performs a Slack API request and returns the result.
        :param text: the text message (even when having blocks, setting this as well is recommended as it works as fallback)
        :param attachments: a collection of attachments
        :param blocks: a collection of Block Kit UI components
        :param response_type: the type of message (either 'in_channel' or 'ephemeral')
        :param headers: request headers to append only for this request
        :return: API response
        """
        return self.send_dict(
            body={
                "text": text,
                "attachments": attachments,
                "blocks": blocks,
                "response_type": response_type,
            },
            headers=headers,
        )

    def send_dict(
        self, body: Dict[str, any], headers: Optional[Dict[str, str]] = None
    ) -> WebhookResponse:
        """Performs a Slack API request and returns the result.
        :param body: json data structure (it's still a dict at this point),
            if you give this argument, body_params and files will be skipped
        :param headers: request headers to append only for this request
        :return: API response
        """
        body = {k: v for k, v in body.items() if v is not None}
        body = convert_bool_to_0_or_1(body)
        self._parse_web_class_objects(body)
        return self._perform_http_request(
            body=body, headers=self._build_request_headers(headers)
        )

    def _perform_http_request(
        self, *, body: Dict[str, any], headers: Dict[str, str]
    ) -> WebhookResponse:
        """Performs an HTTP request and parses the response.
        :param url: a complete URL to send data (e.g., https://hooks.slack.com/XXX)
        :param body: request body data
        :param headers: complete set of request headers
        :return: API response
        """
        body = json.dumps(body)
        headers["Content-Type"] = "application/json;charset=utf-8"

        if self.logger.level <= logging.DEBUG:
            self.logger.debug(
                f"Sending a request - url: {self.url}, body: {body}, headers: {headers}"
            )
        try:
            url = self.url
            # for security
            if url.lower().startswith("http"):
                req = Request(
                    method="POST", url=url, data=body.encode("utf-8"), headers=headers
                )
                if self.proxy is not None:
                    host = re.sub("^https?://", "", self.proxy)
                    req.set_proxy(host, "http")
                    req.set_proxy(host, "https")
            else:
                raise SlackRequestError(f"Invalid URL detected: {url}")

            resp: HTTPResponse = urlopen(req, context=self.ssl, timeout=self.timeout)
            charset: str = resp.headers.get_content_charset() or "utf-8"
            response_body: str = resp.read().decode(charset)
            resp = WebhookResponse(
                url=url,
                status_code=resp.status,
                body=response_body,
                headers=resp.headers,
            )
            self._debug_log_response(resp)
            return resp

        except HTTPError as e:
            charset: str = e.headers.get_content_charset() or "utf-8"
            response_body: str = resp.read().decode(charset)
            resp = WebhookResponse(
                url=url, status_code=e.code, body=response_body, headers=e.headers,
            )
            if e.code == 429:
                # for backward-compatibility with WebClient (v.2.5.0 or older)
                resp.headers["Retry-After"] = resp.headers["retry-after"]
            self._debug_log_response(resp)
            return resp

        except Exception as err:
            self.logger.error(f"Failed to send a request to Slack API server: {err}")
            raise err

    def _build_request_headers(
        self, additional_headers: Optional[Dict[str, str]],
    ) -> Dict[str, str]:
        if additional_headers is None:
            return {}

        request_headers = {
            "User-Agent": get_user_agent(),
            "Content-Type": "application/json;charset=utf-8",
        }
        request_headers.update(self.default_headers)
        if additional_headers:
            request_headers.update(additional_headers)
        return request_headers

    @staticmethod
    def _parse_web_class_objects(body) -> None:
        def to_dict(obj: Union[Dict, Block, Attachment]):
            if isinstance(obj, Block):
                return obj.to_dict()
            if isinstance(obj, Attachment):
                return obj.to_dict()
            return obj

        blocks = body.get("blocks", None)

        if blocks is not None and isinstance(blocks, list):
            dict_blocks = [to_dict(b) for b in blocks]
            body.update({"blocks": dict_blocks})

        attachments = body.get("attachments", None)
        if attachments is not None and isinstance(attachments, list):
            dict_attachments = [to_dict(a) for a in attachments]
            body.update({"attachments": dict_attachments})

    def _debug_log_response(self, resp: WebhookResponse) -> None:
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(
                "Received the following response - "
                f"status: {resp.status_code}, "
                f"headers: {(dict(resp.headers))}, "
                f"body: {resp.body}"
            )
