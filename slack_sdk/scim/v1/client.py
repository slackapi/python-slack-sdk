import json
import logging
import urllib
from http.client import HTTPResponse
from ssl import SSLContext
from typing import Dict, Optional, Union, Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen, OpenerDirector, ProxyHandler, HTTPSHandler

from slack_sdk.errors import SlackRequestError
from .internal_utils import (
    _build_query,
    _build_request_headers,
    _debug_log_response,
    get_user_agent,
    _to_dict_without_not_given,
)
from .response import (
    SCIMResponse,
    SearchUsersResponse,
    ReadUserResponse,
    SearchGroupsResponse,
    ReadGroupResponse,
    UserCreateResponse,
    UserPatchResponse,
    UserUpdateResponse,
    UserDeleteResponse,
    GroupCreateResponse,
    GroupPatchResponse,
    GroupUpdateResponse,
    GroupDeleteResponse,
)
from .user import User
from .group import Group


class SCIMClient:
    BASE_URL = "https://api.slack.com/scim/v1/"

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
        """API client for SCIM API
        See https://api.slack.com/scim for more details
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

    # -------------------------
    # Users
    # -------------------------

    def search_users(
        self,
        *,
        # Pagination required as of August 30, 2019.
        count: int,
        start_index: int,
        filter: Optional[str] = None,
    ) -> SearchUsersResponse:
        return SearchUsersResponse(
            self.api_call(
                http_verb="GET",
                path="Users",
                query_params={
                    "filter": filter,
                    "count": count,
                    "startIndex": start_index,
                },
            )
        )

    def read_user(self, id: str) -> ReadUserResponse:
        return ReadUserResponse(
            self.api_call(http_verb="GET", path=f"Users/{quote(id)}")
        )

    def create_user(self, user: Union[Dict[str, Any], User]) -> UserCreateResponse:
        return UserCreateResponse(
            self.api_call(
                http_verb="POST",
                path="Users",
                body_params=user.to_dict()
                if isinstance(user, User)
                else _to_dict_without_not_given(user),
            )
        )

    def patch_user(
        self, id: str, partial_user: Union[Dict[str, Any], User]
    ) -> UserPatchResponse:
        return UserPatchResponse(
            self.api_call(
                http_verb="PATCH",
                path=f"Users/{quote(id)}",
                body_params=partial_user.to_dict()
                if isinstance(partial_user, User)
                else _to_dict_without_not_given(partial_user),
            )
        )

    def update_user(self, user: Union[Dict[str, Any], User]) -> UserUpdateResponse:
        return UserUpdateResponse(
            self.api_call(
                http_verb="PUT",
                path=f"Users/{quote(user.id)}",
                body_params=user.to_dict()
                if isinstance(user, User)
                else _to_dict_without_not_given(user),
            )
        )

    def delete_user(self, id: str) -> UserDeleteResponse:
        return UserDeleteResponse(
            self.api_call(
                http_verb="DELETE",
                path=f"Users/{quote(id)}",
            )
        )

    # -------------------------
    # Groups
    # -------------------------

    def search_groups(
        self,
        *,
        # Pagination required as of August 30, 2019.
        count: int,
        start_index: int,
        filter: Optional[str] = None,
    ) -> SearchGroupsResponse:
        return SearchGroupsResponse(
            self.api_call(
                http_verb="GET",
                path="Groups",
                query_params={
                    "filter": filter,
                    "count": count,
                    "startIndex": start_index,
                },
            )
        )

    def read_group(self, id: str) -> ReadGroupResponse:
        return ReadGroupResponse(
            self.api_call(http_verb="GET", path=f"Groups/{quote(id)}")
        )

    def create_group(self, group: Union[Dict[str, Any], Group]) -> GroupCreateResponse:
        return GroupCreateResponse(
            self.api_call(
                http_verb="POST",
                path="Groups",
                body_params=group.to_dict()
                if isinstance(group, Group)
                else _to_dict_without_not_given(group),
            )
        )

    def patch_group(
        self, id: str, partial_group: Union[Dict[str, Any], Group]
    ) -> GroupPatchResponse:
        return GroupPatchResponse(
            self.api_call(
                http_verb="PATCH",
                path=f"Groups/{quote(id)}",
                body_params=partial_group.to_dict()
                if isinstance(partial_group, Group)
                else _to_dict_without_not_given(partial_group),
            )
        )

    def update_group(self, group: Union[Dict[str, Any], Group]) -> GroupUpdateResponse:
        return GroupUpdateResponse(
            self.api_call(
                http_verb="PUT",
                path=f"Groups/{quote(group.id)}",
                body_params=group.to_dict()
                if isinstance(group, Group)
                else _to_dict_without_not_given(group),
            )
        )

    def delete_group(self, id: str) -> GroupDeleteResponse:
        return GroupDeleteResponse(
            self.api_call(
                http_verb="DELETE",
                path=f"Groups/{quote(id)}",
            )
        )

    # -------------------------

    def api_call(
        self,
        *,
        http_verb: str,
        path: str,
        query_params: Optional[Dict[str, Any]] = None,
        body_params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> SCIMResponse:
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
        body_params: Optional[Dict[str, Any]] = None,
        headers: Dict[str, str],
    ) -> SCIMResponse:
        if body_params is not None:
            if body_params.get("schemas") is None:
                body_params["schemas"] = ["urn:scim:schemas:core:1.0"]
            body_params = json.dumps(body_params)
        headers["Content-Type"] = "application/json;charset=utf-8"

        if self.logger.level <= logging.DEBUG:
            headers_for_logging = {
                k: "(redacted)" if k.lower() == "authorization" else v
                for k, v in headers.items()
            }
            self.logger.debug(
                f"Sending a request - {http_verb} url: {url}, body: {body_params}, headers: {headers_for_logging}"
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
            resp = SCIMResponse(
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
            resp = SCIMResponse(
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
