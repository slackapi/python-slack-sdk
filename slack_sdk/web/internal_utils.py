import json
import platform
import sys
from ssl import SSLContext
from typing import Dict, Optional, Any
from typing import Union, List
from urllib.parse import urljoin

from slack_sdk import version
from slack_sdk.errors import SlackRequestError
from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block


def convert_bool_to_0_or_1(
    params: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Converts all bool values in dict to "0" or "1".

    Slack APIs safely accept "0"/"1" as boolean values.
    Using True/False (bool in Python) doesn't work with aiohttp.
    This method converts only the bool values in top-level of a given dict.

    :param params: params as a dict
    :return: return modified dict
    """
    if params:
        return {k: _to_0_or_1_if_bool(v) for k, v in params.items()}
    return None


def get_user_agent(prefix: Optional[str] = None, suffix: Optional[str] = None):
    """Construct the user-agent header with the package info,
    Python version and OS version.

    Returns:
        The user agent string.
        e.g. 'Python/3.6.7 slackclient/2.0.0 Darwin/17.7.0'
    """
    # __name__ returns all classes, we only want the client
    client = "{0}/{1}".format("slackclient", version.__version__)
    python_version = "Python/{v.major}.{v.minor}.{v.micro}".format(v=sys.version_info)
    system_info = "{0}/{1}".format(platform.system(), platform.release())
    user_agent_string = " ".join([python_version, client, system_info])
    prefix = f"{prefix} " if prefix else ""
    suffix = f" {suffix}" if suffix else ""
    return prefix + user_agent_string + suffix


def _get_url(base_url: str, api_method: str) -> str:
    """Joins the base Slack URL and an API method to form an absolute URL.

    Args:
        base_url (str): The base URL
        api_method (str): The Slack Web API method. e.g. 'chat.postMessage'

    Returns:
        The absolute API URL.
            e.g. 'https://www.slack.com/api/chat.postMessage'
    """
    return urljoin(base_url, api_method)


def _get_headers(
    *,
    headers: dict,
    token: Optional[str],
    has_json: bool,
    has_files: bool,
    request_specific_headers: Optional[dict],
) -> Dict[str, str]:
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
        "Content-Type": "application/x-www-form-urlencoded",
    }
    if headers is None or "User-Agent" not in headers:
        final_headers["User-Agent"] = get_user_agent()

    if token:
        final_headers.update({"Authorization": "Bearer {}".format(token)})
    if headers is None:
        headers = {}

    # Merge headers specified at client initialization.
    final_headers.update(headers)

    # Merge headers specified for a specific request. e.g. oauth.access
    if request_specific_headers:
        final_headers.update(request_specific_headers)

    if has_json:
        final_headers.update({"Content-Type": "application/json;charset=utf-8"})

    if has_files:
        # These are set automatically by the aiohttp library.
        final_headers.pop("Content-Type", None)

    return final_headers


def _build_req_args(
    *,
    token: Optional[str],
    http_verb: str,
    files: dict,
    data: Union[dict],
    params: dict,
    json: dict,  # skipcq: PYL-W0621
    headers: dict,
    auth: dict,
    ssl: Optional[SSLContext],
    proxy: Optional[str],
) -> dict:
    has_json = json is not None
    has_files = files is not None
    if has_json and http_verb != "POST":
        msg = "Json data can only be submitted as POST requests. GET requests should use the 'params' argument."
        raise SlackRequestError(msg)

    if data is not None and isinstance(data, dict):
        data = {k: v for k, v in data.items() if v is not None}
    if files is not None and isinstance(files, dict):
        files = {k: v for k, v in files.items() if v is not None}
    if params is not None and isinstance(params, dict):
        params = {k: v for k, v in params.items() if v is not None}

    token: Optional[str] = token
    if params is not None and "token" in params:
        token = params.pop("token")
    if json is not None and "token" in json:
        token = json.pop("token")
    req_args = {
        "headers": _get_headers(
            headers=headers,
            token=token,
            has_json=has_json,
            has_files=has_files,
            request_specific_headers=headers,
        ),
        "data": data,
        "files": files,
        "params": params,
        "json": json,
        "ssl": ssl,
        "proxy": proxy,
        "auth": auth,
    }
    return req_args


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


def _update_call_participants(kwargs, users: Union[str, List[Dict[str, str]]]) -> None:
    if users is None:
        return

    if isinstance(users, list):
        kwargs.update({"users": json.dumps(users)})
    elif isinstance(users, str):
        kwargs.update({"users": users})
    else:
        raise SlackRequestError("users must be either str or List[Dict[str, str]]")


def _next_cursor_is_present(data) -> bool:
    """Determine if the response contains 'next_cursor'
    and 'next_cursor' is not empty.

    Returns:
        A boolean value.
    """
    present = (
        "response_metadata" in data
        and "next_cursor" in data["response_metadata"]
        and data["response_metadata"]["next_cursor"] != ""
    )
    return present


def _to_0_or_1_if_bool(v: Any) -> Union[Any, str]:
    if isinstance(v, bool):
        return "1" if v else "0"
    return v
