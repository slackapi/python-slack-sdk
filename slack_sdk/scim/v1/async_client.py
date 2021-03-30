import json
import logging
from ssl import SSLContext
from typing import Any, Union
from typing import Dict, Optional
from urllib.parse import quote

import aiohttp
from aiohttp import BasicAuth, ClientSession

from .internal_utils import (
    _build_request_headers,
    _debug_log_response,
    get_user_agent,
    _to_dict_without_not_given,
    _build_query,
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
from ...proxy_env_variable_loader import load_http_proxy_from_env


class AsyncSCIMClient:
    BASE_URL = "https://api.slack.com/scim/v1/"

    token: str
    timeout: int
    ssl: Optional[SSLContext]
    proxy: Optional[str]
    base_url: str
    session: Optional[ClientSession]
    trust_env_in_session: bool
    auth: Optional[BasicAuth]
    default_headers: Dict[str, str]
    logger: logging.Logger

    def __init__(
        self,
        token: str,
        timeout: int = 30,
        ssl: Optional[SSLContext] = None,
        proxy: Optional[str] = None,
        base_url: str = BASE_URL,
        session: Optional[ClientSession] = None,
        trust_env_in_session: bool = False,
        auth: Optional[BasicAuth] = None,
        default_headers: Optional[Dict[str, str]] = None,
        user_agent_prefix: Optional[str] = None,
        user_agent_suffix: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """API client for SCIM API
        See https://api.slack.com/scim for more details

        Args:
            token: An admin user's token, which starts with `xoxp-`
            timeout: Request timeout (in seconds)
            ssl: `ssl.SSLContext` to use for requests
            proxy: Proxy URL (e.g., `localhost:9000`, `http://localhost:9000`)
            base_url: The base URL for API calls
            session: `aiohttp.ClientSession` instance
            trust_env_in_session: True/False for `aiohttp.ClientSession`
            auth: Basic auth info for `aiohttp.ClientSession`
            default_headers: Request headers to add to all requests
            user_agent_prefix: Prefix for User-Agent header value
            user_agent_suffix: Suffix for User-Agent header value
            logger: Custom logger
        """
        self.token = token
        self.timeout = timeout
        self.ssl = ssl
        self.proxy = proxy
        self.base_url = base_url
        self.session = session
        self.trust_env_in_session = trust_env_in_session
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

    # -------------------------
    # Users
    # -------------------------

    async def search_users(
        self,
        *,
        # Pagination required as of August 30, 2019.
        count: int,
        start_index: int,
        filter: Optional[str] = None,
    ) -> SearchUsersResponse:
        return SearchUsersResponse(
            await self.api_call(
                http_verb="GET",
                path="Users",
                query_params={
                    "filter": filter,
                    "count": count,
                    "startIndex": start_index,
                },
            )
        )

    async def read_user(self, id: str) -> ReadUserResponse:
        return ReadUserResponse(
            await self.api_call(http_verb="GET", path=f"Users/{quote(id)}")
        )

    async def create_user(
        self, user: Union[Dict[str, Any], User]
    ) -> UserCreateResponse:
        return UserCreateResponse(
            await self.api_call(
                http_verb="POST",
                path="Users",
                body_params=user.to_dict()
                if isinstance(user, User)
                else _to_dict_without_not_given(user),
            )
        )

    async def patch_user(
        self, id: str, partial_user: Union[Dict[str, Any], User]
    ) -> UserPatchResponse:
        return UserPatchResponse(
            await self.api_call(
                http_verb="PATCH",
                path=f"Users/{quote(id)}",
                body_params=partial_user.to_dict()
                if isinstance(partial_user, User)
                else _to_dict_without_not_given(partial_user),
            )
        )

    async def update_user(
        self, user: Union[Dict[str, Any], User]
    ) -> UserUpdateResponse:
        return UserUpdateResponse(
            await self.api_call(
                http_verb="PUT",
                path=f"Users/{quote(user.id)}",
                body_params=user.to_dict()
                if isinstance(user, User)
                else _to_dict_without_not_given(user),
            )
        )

    async def delete_user(self, id: str) -> UserDeleteResponse:
        return UserDeleteResponse(
            await self.api_call(
                http_verb="DELETE",
                path=f"Users/{quote(id)}",
            )
        )

    # -------------------------
    # Groups
    # -------------------------

    async def search_groups(
        self,
        *,
        # Pagination required as of August 30, 2019.
        count: int,
        start_index: int,
        filter: Optional[str] = None,
    ) -> SearchGroupsResponse:
        return SearchGroupsResponse(
            await self.api_call(
                http_verb="GET",
                path="Groups",
                query_params={
                    "filter": filter,
                    "count": count,
                    "startIndex": start_index,
                },
            )
        )

    async def read_group(self, id: str) -> ReadGroupResponse:
        return ReadGroupResponse(
            await self.api_call(http_verb="GET", path=f"Groups/{quote(id)}")
        )

    async def create_group(
        self, group: Union[Dict[str, Any], Group]
    ) -> GroupCreateResponse:
        return GroupCreateResponse(
            await self.api_call(
                http_verb="POST",
                path="Groups",
                body_params=group.to_dict()
                if isinstance(group, Group)
                else _to_dict_without_not_given(group),
            )
        )

    async def patch_group(
        self, id: str, partial_group: Union[Dict[str, Any], Group]
    ) -> GroupPatchResponse:
        return GroupPatchResponse(
            await self.api_call(
                http_verb="PATCH",
                path=f"Groups/{quote(id)}",
                body_params=partial_group.to_dict()
                if isinstance(partial_group, Group)
                else _to_dict_without_not_given(partial_group),
            )
        )

    async def update_group(
        self, group: Union[Dict[str, Any], Group]
    ) -> GroupUpdateResponse:
        return GroupUpdateResponse(
            await self.api_call(
                http_verb="PUT",
                path=f"Groups/{quote(group.id)}",
                body_params=group.to_dict()
                if isinstance(group, Group)
                else _to_dict_without_not_given(group),
            )
        )

    async def delete_group(self, id: str) -> GroupDeleteResponse:
        return GroupDeleteResponse(
            await self.api_call(
                http_verb="DELETE",
                path=f"Groups/{quote(id)}",
            )
        )

    # -------------------------

    async def api_call(
        self,
        *,
        http_verb: str,
        path: str,
        query_params: Optional[Dict[str, any]] = None,
        body_params: Optional[Dict[str, any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> SCIMResponse:
        url = f"{self.base_url}{path}"
        query = _build_query(query_params)
        if len(query) > 0:
            url += f"?{query}"
        return await self._perform_http_request(
            http_verb=http_verb,
            url=url,
            body_params=body_params,
            headers=_build_request_headers(
                token=self.token,
                default_headers=self.default_headers,
                additional_headers=headers,
            ),
        )

    async def _perform_http_request(
        self,
        *,
        http_verb: str,
        url: str,
        body_params: Optional[Dict[str, Any]],
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
                f"Sending a request - url: {url}, params: {body_params}, headers: {headers_for_logging}"
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

        resp: SCIMResponse
        try:
            request_kwargs = {
                "headers": headers,
                "data": body_params,
                "ssl": self.ssl,
                "proxy": self.proxy,
            }
            async with session.request(http_verb, url, **request_kwargs) as res:
                response_body: str = ""
                try:
                    response_body = await res.text()
                except aiohttp.ContentTypeError:
                    self.logger.debug(
                        f"No response data returned from the following API call: {url}."
                    )

                resp = SCIMResponse(
                    url=url,
                    status_code=res.status,
                    raw_body=response_body,
                    headers=res.headers,
                )
                _debug_log_response(self.logger, resp)
        finally:
            if not use_running_session:
                await session.close()

        return resp
