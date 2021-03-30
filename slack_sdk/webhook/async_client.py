import json
import logging
from ssl import SSLContext
from typing import Dict, Union, Optional, Any, Sequence

import aiohttp
from aiohttp import BasicAuth, ClientSession

from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block
from .internal_utils import (
    _debug_log_response,
    _build_request_headers,
    _build_body,
    get_user_agent,
)
from .webhook_response import WebhookResponse
from ..proxy_env_variable_loader import load_http_proxy_from_env


class AsyncWebhookClient:
    url: str
    timeout: int
    ssl: Optional[SSLContext]
    proxy: Optional[str]
    session: Optional[ClientSession]
    trust_env_in_session: bool
    auth: Optional[BasicAuth]
    default_headers: Dict[str, str]
    logger: logging.Logger

    def __init__(
        self,
        url: str,
        timeout: int = 30,
        ssl: Optional[SSLContext] = None,
        proxy: Optional[str] = None,
        session: Optional[ClientSession] = None,
        trust_env_in_session: bool = False,
        auth: Optional[BasicAuth] = None,
        default_headers: Optional[Dict[str, str]] = None,
        user_agent_prefix: Optional[str] = None,
        user_agent_suffix: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """API client for Incoming Webhooks and `response_url`

        https://api.slack.com/messaging/webhooks

        Args:
            url: Complete URL to send data (e.g., `https://hooks.slack.com/XXX`)
            timeout: Request timeout (in seconds)
            ssl: `ssl.SSLContext` to use for requests
            proxy: Proxy URL (e.g., `localhost:9000`, `http://localhost:9000`)
            session: `aiohttp.ClientSession` instance
            trust_env_in_session: True/False for `aiohttp.ClientSession`
            auth: Basic auth info for `aiohttp.ClientSession`
            default_headers: Request headers to add to all requests
            user_agent_prefix: Prefix for User-Agent header value
            user_agent_suffix: Suffix for User-Agent header value
            logger: Custom logger
        """
        self.url = url
        self.timeout = timeout
        self.ssl = ssl
        self.proxy = proxy
        self.trust_env_in_session = trust_env_in_session
        self.session = session
        self.auth = auth
        self.default_headers = default_headers if default_headers else {}
        self.default_headers["User-Agent"] = get_user_agent(
            user_agent_prefix, user_agent_suffix
        )
        self.logger = logger if logger is not None else logging.getLogger(__name__)

        if self.proxy is None or len(self.proxy.strip()) == 0:
            env_variable = load_http_proxy_from_env(self.logger)
            if env_variable is not None:
                self.proxy = env_variable

    async def send(
        self,
        *,
        text: Optional[str] = None,
        attachments: Optional[Sequence[Union[Dict[str, Any], Attachment]]] = None,
        blocks: Optional[Sequence[Union[Dict[str, Any], Block]]] = None,
        response_type: Optional[str] = None,
        replace_original: Optional[bool] = None,
        delete_original: Optional[bool] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> WebhookResponse:
        """Performs a Slack API request and returns the result.

        Args:
            text: The text message (even when having blocks, setting this as well is recommended as it works as fallback)
            attachments: A collection of attachments
            blocks: A collection of Block Kit UI components
            response_type: The type of message (either 'in_channel' or 'ephemeral')
            replace_original: True if you use this option for response_url requests
            delete_original: True if you use this option for response_url requests
            headers: Request headers to append only for this request

        Returns:
            Webhook response
        """
        return await self.send_dict(
            # It's fine to have None value elements here
            # because _build_body() filters them out when constructing the actual body data
            body={
                "text": text,
                "attachments": attachments,
                "blocks": blocks,
                "response_type": response_type,
                "replace_original": replace_original,
                "delete_original": delete_original,
            },
            headers=headers,
        )

    async def send_dict(
        self, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> WebhookResponse:
        """Performs a Slack API request and returns the result.

        Args:
            body: JSON data structure (it's still a dict at this point),
                if you give this argument, body_params and files will be skipped
            headers: Request headers to append only for this request
        Returns:
            Webhook response
        """
        return await self._perform_http_request(
            body=_build_body(body),
            headers=_build_request_headers(self.default_headers, headers),
        )

    async def _perform_http_request(
        self, *, body: Dict[str, Any], headers: Dict[str, str]
    ) -> WebhookResponse:
        body = json.dumps(body)
        headers["Content-Type"] = "application/json;charset=utf-8"

        if self.logger.level <= logging.DEBUG:
            self.logger.debug(
                f"Sending a request - url: {self.url}, body: {body}, headers: {headers}"
            )
        session: Optional[ClientSession] = None
        use_running_session = self.session and not self.session.closed
        if use_running_session:
            session = self.session
        else:
            session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                auth=self.auth,
                trust_env=self.trust_env_in_session,
            )

        resp: WebhookResponse
        try:
            request_kwargs = {
                "headers": headers,
                "data": body,
                "ssl": self.ssl,
                "proxy": self.proxy,
            }
            async with session.request("POST", self.url, **request_kwargs) as res:
                response_body: str = ""
                try:
                    response_body = await res.text()
                except aiohttp.ContentTypeError:
                    self.logger.debug(
                        f"No response data returned from the following API call: {self.url}"
                    )

                resp = WebhookResponse(
                    url=self.url,
                    status_code=res.status,
                    body=response_body,
                    headers=res.headers,
                )
                _debug_log_response(self.logger, resp)
        finally:
            if not use_running_session:
                await session.close()

        return resp
