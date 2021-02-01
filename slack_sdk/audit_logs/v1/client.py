import json
import logging
import urllib
from http.client import HTTPResponse
from ssl import SSLContext
from typing import Dict, Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen, OpenerDirector, ProxyHandler, HTTPSHandler

from slack_sdk.errors import SlackRequestError
from .internal_utils import (
    _build_query,
    _build_request_headers,
    _debug_log_response,
    get_user_agent,
)
from .response import AuditLogsResponse


class AuditLogsClient:
    BASE_URL = "https://api.slack.com/audit/v1/"

    token: str
    timeout: int
    ssl: Optional[SSLContext]
    proxy: Optional[str]
    base_url: str
    default_headers: Dict[str, str]
    logger: logging.Logger

    def __init__(
        self,
        token: str,
        timeout: int = 30,
        ssl: Optional[SSLContext] = None,
        proxy: Optional[str] = None,
        base_url: str = BASE_URL,
        default_headers: Optional[Dict[str, str]] = None,
        user_agent_prefix: Optional[str] = None,
        user_agent_suffix: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """API client for Audit Logs API
        See https://api.slack.com/admins/audit-logs for more details

        :param token: An admin user's token, which starts with xoxp-
        :param timeout: request timeout (in seconds)
        :param ssl: ssl.SSLContext to use for requests
        :param proxy: proxy URL (e.g., localhost:9000, http://localhost:9000)
        :param base_url: the base URL for API calls
        :param default_headers: request headers to add to all requests
        :param user_agent_prefix: prefix for User-Agent header value
        :param user_agent_suffix: suffix for User-Agent header value
        :param logger: custom logger
        """
        self.token = token
        self.timeout = timeout
        self.ssl = ssl
        self.proxy = proxy
        self.base_url = base_url
        self.default_headers = default_headers if default_headers else {}
        self.default_headers["User-Agent"] = get_user_agent(
            user_agent_prefix, user_agent_suffix
        )
        self.logger = logger if logger is not None else logging.getLogger(__name__)

    def schemas(
        self,
        *,
        query_params: Optional[Dict[str, any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> AuditLogsResponse:
        """
        Returns information about the kind of objects which the Audit Logs API
        returns as a list of all objects and a short description.
        Authentication not required.

        :param query_params: Set any values if you want to add query params
        :param headers: additional request headers
        :return: API response
        """
        return self.api_call(
            path="schemas",
            query_params=query_params,
            headers=headers,
        )

    def actions(
        self,
        *,
        query_params: Optional[Dict[str, any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> AuditLogsResponse:
        """
        Returns information about the kind of actions that the Audit Logs API
        returns as a list of all actions and a short description of each.
        Authentication not required.

        :param query_params: Set any values if you want to add query params
        :param headers: additional request headers
        :return: API response
        """
        return self.api_call(
            path="actions",
            query_params=query_params,
            headers=headers,
        )

    def logs(
        self,
        *,
        latest: Optional[int] = None,
        oldest: Optional[int] = None,
        limit: Optional[int] = None,
        action: Optional[str] = None,
        actor: Optional[str] = None,
        entity: Optional[str] = None,
        additional_query_params: Optional[Dict[str, any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> AuditLogsResponse:
        """
        This is the primary endpoint for retrieving actual audit events from your organization.
        It will return a list of actions that have occurred on the installed workspace or grid organization.
        Authentication required.

        The following filters can be applied in order to narrow the range of actions returned.
        Filters are added as query string parameters and can be combined together.
        Multiple filter parameters are additive (a boolean AND) and are separated
        with an ampersand (&) in the query string. Filtering is entirely optional.

        :param latest: Unix timestamp of the most recent audit event to include (inclusive).
        :param oldest: Unix timestamp of the least recent audit event to include (inclusive).
            Data is not available prior to March 2018.
        :param limit: Number of results to optimistically return, maximum 9999.
        :param action: Name of the action.
        :param actor: User ID who initiated the action.
        :param entity: ID of the target entity of the action (such as a channel, workspace, organization, file).
        :param additional_query_params: Add anything else if you need to use the ones this library does not support
        :param headers: additional request headers
        :return: API response
        """
        query_params = {
            "latest": latest,
            "oldest": oldest,
            "limit": limit,
            "action": action,
            "actor": actor,
            "entity": entity,
        }
        if additional_query_params is not None:
            query_params.update(additional_query_params)
        query_params = {k: v for k, v in query_params.items() if v is not None}
        return self.api_call(
            path="logs",
            query_params=query_params,
            headers=headers,
        )

    def api_call(
        self,
        *,
        http_verb: str = "GET",
        path: str,
        query_params: Optional[Dict[str, any]] = None,
        body_params: Optional[Dict[str, any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> AuditLogsResponse:
        """Performs a Slack API request and returns the result."""
        url = f"{self.base_url}{path}"
        query = _build_query(query_params)
        if len(query) > 0:
            url += f"?{query}"

        return self._perform_http_request(
            http_verb=http_verb,
            url=url,
            body_params=body_params,
            headers=_build_request_headers(
                token=self.token,
                default_headers=self.default_headers,
                additional_headers=headers,
            ),
        )

    def _perform_http_request(
        self,
        *,
        http_verb: str = "GET",
        url: str,
        body_params: Optional[Dict[str, any]] = None,
        headers: Dict[str, str],
    ) -> AuditLogsResponse:
        if body_params is not None:
            body_params = json.dumps(body_params)
        headers["Content-Type"] = "application/json;charset=utf-8"

        if self.logger.level <= logging.DEBUG:
            headers_for_logging = {
                k: "(redacted)" if k.lower() == "authorization" else v
                for k, v in headers.items()
            }
            self.logger.debug(
                f"Sending a request - url: {url}, body: {body_params}, headers: {headers_for_logging}"
            )
        try:
            opener: Optional[OpenerDirector] = None
            # for security (BAN-B310)
            if url.lower().startswith("http"):
                req = Request(
                    method=http_verb,
                    url=url,
                    data=body_params.encode("utf-8")
                    if body_params is not None
                    else None,
                    headers=headers,
                )
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
            else:
                raise SlackRequestError(f"Invalid URL detected: {url}")

            # NOTE: BAN-B310 is already checked above
            resp: Optional[HTTPResponse] = None
            if opener:
                resp = opener.open(req, timeout=self.timeout)  # skipcq: BAN-B310
            else:
                resp = urlopen(  # skipcq: BAN-B310
                    req, context=self.ssl, timeout=self.timeout
                )
            charset: str = resp.headers.get_content_charset() or "utf-8"
            response_body: str = resp.read().decode(charset)
            resp = AuditLogsResponse(
                url=url,
                status_code=resp.status,
                raw_body=response_body,
                headers=resp.headers,
            )
            _debug_log_response(self.logger, resp)
            return resp

        except HTTPError as e:
            # read the response body here
            charset = e.headers.get_content_charset() or "utf-8"
            body_params: str = e.read().decode(charset)
            resp = AuditLogsResponse(
                url=url,
                status_code=e.code,
                raw_body=body_params,
                headers=e.headers,
            )
            if e.code == 429:
                # for backward-compatibility with WebClient (v.2.5.0 or older)
                resp.headers["Retry-After"] = resp.headers["retry-after"]
            _debug_log_response(self.logger, resp)
            return resp

        except Exception as err:
            self.logger.error(f"Failed to send a request to Slack API server: {err}")
            raise err
