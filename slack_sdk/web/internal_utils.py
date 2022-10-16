import json
import logging
import os
import platform
import sys
import urllib
import warnings
from asyncio import Future
from http.client import HTTPResponse
from ssl import SSLContext
from typing import Any, Dict, Optional, Sequence, Union
from urllib.parse import urljoin
from urllib.request import OpenerDirector, ProxyHandler, HTTPSHandler, Request, urlopen

from slack_sdk import version
from slack_sdk.errors import SlackRequestError
from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block
from slack_sdk.models.metadata import Metadata


def convert_bool_to_0_or_1(params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Converts all bool values in dict to "0" or "1".

    Slack APIs safely accept "0"/"1" as boolean values.
    Using True/False (bool in Python) doesn't work with aiohttp.
    This method converts only the bool values in top-level of a given dict.

    Args:
        params: params as a dict

    Returns:
        Modified dict
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


def _set_default_params(target: dict, default_params: dict) -> None:
    for name, value in default_params.items():
        if name not in target:
            target[name] = value


def _build_req_args(
    *,
    token: Optional[str],
    http_verb: str,
    files: dict,
    data: dict,
    default_params: dict,
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
        _set_default_params(data, default_params)
    if files is not None and isinstance(files, dict):
        files = {k: v for k, v in files.items() if v is not None}
        # NOTE: We do not need to all #_set_default_params here
        # because other parameters in binary data requests can exist
        # only in either data or params, not in files.
    if params is not None and isinstance(params, dict):
        params = {k: v for k, v in params.items() if v is not None}
        _set_default_params(params, default_params)
    if json is not None and isinstance(json, dict):
        _set_default_params(json, default_params)

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
    def to_dict(obj: Union[Dict, Block, Attachment, Metadata]):
        if isinstance(obj, Block):
            return obj.to_dict()
        if isinstance(obj, Attachment):
            return obj.to_dict()
        if isinstance(obj, Metadata):
            return obj.to_dict()
        return obj

    blocks = kwargs.get("blocks", None)
    if blocks is not None and isinstance(blocks, Sequence) and (not isinstance(blocks, str)):
        dict_blocks = [to_dict(b) for b in blocks]
        kwargs.update({"blocks": dict_blocks})

    attachments = kwargs.get("attachments", None)
    if attachments is not None and isinstance(attachments, Sequence) and (not isinstance(attachments, str)):
        dict_attachments = [to_dict(a) for a in attachments]
        kwargs.update({"attachments": dict_attachments})

    metadata = kwargs.get("metadata", None)
    if metadata is not None and isinstance(metadata, Metadata):
        kwargs.update({"metadata": to_dict(metadata)})


def _update_call_participants(kwargs, users: Union[str, Sequence[Dict[str, str]]]) -> None:
    if users is None:
        return

    if isinstance(users, list):
        kwargs.update({"users": json.dumps(users)})
    elif isinstance(users, str):
        kwargs.update({"users": users})
    else:
        raise SlackRequestError("users must be either str or Sequence[Dict[str, str]]")


def _next_cursor_is_present(data) -> bool:
    """Determine if the response contains 'next_cursor'
    and 'next_cursor' is not empty.

    Returns:
        A boolean value.
    """
    # Only admin.conversations.search returns next_cursor at the top level
    present = ("next_cursor" in data and data["next_cursor"] != "") or (
        "response_metadata" in data
        and "next_cursor" in data["response_metadata"]
        and data["response_metadata"]["next_cursor"] != ""
    )
    return present


def _to_0_or_1_if_bool(v: Any) -> Union[Any, str]:
    if isinstance(v, bool):
        return "1" if v else "0"
    return v


def _warn_if_text_or_attachment_fallback_is_missing(endpoint: str, kwargs: Dict[str, Any]) -> None:
    text = kwargs.get("text")
    if text and len(text.strip()) > 0:
        # If a top-level text arg is provided, we are good. This is the recommended accessibility field to always provide.
        return

    # for unit tests etc.
    skip_deprecation = os.environ.get("SKIP_SLACK_SDK_WARNING")
    if skip_deprecation:
        return

    # At this point, at a minimum, text argument is missing. Warn the user about this.
    message = (
        f"The top-level `text` argument is missing in the request payload for a {endpoint} call - "
        f"It's a best practice to always provide a `text` argument when posting a message. "
        f"The `text` argument is used in places where content cannot be rendered such as: "
        "system push notifications, assistive technology such as screen readers, etc."
    )
    warnings.warn(message, UserWarning)

    # Additionally, specifically for attachments, there is a legacy field available at the attachment level called `fallback`
    # Even with a missing text, one can provide a `fallback` per attachment.
    # More details here: https://api.slack.com/reference/messaging/attachments#legacy_fields
    attachments = kwargs.get("attachments")
    # Note that this method does not verify attachments
    # if the value is already serialized as a single str value.
    if (
        attachments is not None
        and isinstance(attachments, list)
        and not all(
            [isinstance(attachment, dict) and len(attachment.get("fallback", "").strip()) > 0 for attachment in attachments]
        )
    ):
        # https://api.slack.com/reference/messaging/attachments
        # Check if the fallback field exists for all the attachments
        # Not all attachments have a fallback property; warn about this too!
        message = (
            f"Additionally, the attachment-level `fallback` argument is missing in the request payload for a {endpoint} call"
            f" - To avoid this warning, it is recommended to always provide a top-level `text` argument when posting a"
            f" message. Alternatively you can provide an attachment-level `fallback` argument, though this is now considered"
            f" a legacy field (see https://api.slack.com/reference/messaging/attachments#legacy_fields for more details)."
        )
        warnings.warn(message, UserWarning)


def _build_unexpected_body_error_message(body: str) -> str:
    body_for_logging = "".join([line.strip() for line in body.replace("\r", "\n").split("\n")])
    if len(body_for_logging) > 100:
        body_for_logging = body_for_logging[:100] + "..."
    message = f"Received a response in a non-JSON format: {body_for_logging}"
    return message


def _remove_none_values(d: dict) -> dict:
    # To avoid having null values in JSON (Slack API does not work with null in many situations)
    #
    # >>> import json
    # >>> d = {"a": None, "b":123}
    # >>> json.dumps(d)
    # '{"a": null, "b": 123}'
    #
    return {k: v for k, v in d.items() if v is not None}


def _to_v2_file_upload_item(upload_file: Dict[str, Any]) -> Dict[str, Optional[Any]]:
    file = upload_file.get("file")
    content = upload_file.get("content")
    data: Optional[bytes] = None
    if file is not None:
        if isinstance(file, str):  # filepath
            with open(file.encode("utf-8", "ignore"), "rb") as readable:
                data = readable.read()
        else:
            data = file
    elif content is not None:
        if isinstance(content, str):
            data = content.encode("utf-8")
        elif isinstance(content, bytes):
            data = content
        else:
            raise SlackRequestError("content for file upload must be 'str' (UTF-8 encoded) or 'bytes' (for data)")

    filename = upload_file.get("filename")
    if upload_file.get("filename") is None and isinstance(file, str):
        # use the local filename if filename is missing
        if upload_file.get("filename") is None:
            filename = file.split(os.path.sep)[-1]
        else:
            filename = "Uploaded file"

    title = upload_file.get("title", "Uploaded file")
    if data is None:
        raise SlackRequestError(f"File content not found for filename: {filename}, title: {title}")

    if title is None:
        title = filename  # to be consistent with files.upload API

    return {
        "filename": filename,
        "data": data,
        "length": len(data),
        "title": title,
        "alt_txt": upload_file.get("alt_txt"),
        "snippet_type": upload_file.get("snippet_type"),
    }


def _upload_file_via_v2_url(
    url: str,
    data: bytes,
    timeout: int,
    logger: logging.Logger,
    proxy: Optional[str] = None,
    ssl: Optional[SSLContext] = None,
) -> Dict[str, Any]:
    opener: Optional[OpenerDirector] = None
    if proxy is not None:
        if isinstance(proxy, str):
            opener = urllib.request.build_opener(
                ProxyHandler({"http": proxy, "https": proxy}),
                HTTPSHandler(context=ssl),
            )
        else:
            raise SlackRequestError(f"Invalid proxy detected: {proxy} must be a str value")

    resp: Optional[HTTPResponse] = None
    req: Request = Request(method="POST", url=url, data=data, headers={})
    if opener:
        resp = opener.open(req, timeout=timeout)
    else:
        resp = urlopen(req, context=ssl, timeout=timeout)  # skipcq: BAN-B310

    charset = resp.headers.get_content_charset() or "utf-8"
    body: str = resp.read().decode(charset)  # read the response body here
    if logger.level <= logging.DEBUG:
        message = (
            "Received the following response - ",
            f"status: {resp.status}, " f"headers: {dict(resp.headers)}, " f"body: {body}",
        )
        logger.debug(message)

    return {"status": resp.status, "headers": resp.headers, "body": body}


def _validate_for_legacy_client(
    response: Union["SlackResponse", Future],  # noqa: F821
) -> None:  # type: ignore
    # Only LegacyWebClient can return this union type
    if isinstance(response, Future):
        message = (
            "Sorry! This SDK does not support run_async=True option for this API calls. "
            "Please migrate to AsyncWebClient, which is a new and stable way to go."
        )
        raise SlackRequestError(message)


def _attach_full_file_metadata(
    client,  # type: ignore
    token_as_arg: Optional[str],
    completion: Union["SlackResponse", Future],  # noqa: F821
) -> None:
    _validate_for_legacy_client(completion)
    _completion: Any = completion  # just for satisfying pytype
    # fetch all the file metadata for backward-compatibility
    for f in _completion.get("files"):
        full_info = client.files_info(
            file=f.get("id"),
            token=token_as_arg,
        )
        f.update(full_info["file"])
    if len(_completion.get("files")) == 1:
        _completion.data["file"] = _completion.get("files")[0]


async def _attach_full_file_metadata_async(
    client,  # type: ignore
    token_as_arg: Optional[str],
    completion: "SlackResponse",  # noqa: F821
) -> None:
    # fetch all the file metadata for backward-compatibility
    for f in completion.get("files"):
        full_info = await client.files_info(
            file=f.get("id"),
            token=token_as_arg,
        )
        f.update(full_info["file"])
    if len(completion.get("files")) == 1:
        completion.data["file"] = completion.get("files")[0]


def _print_files_upload_v2_suggestion():
    message = (
        "client.files_upload() may cause some issues like timeouts for relatively large files. "
        "Our latest recommendation is to use client.files_upload_v2(), "
        "which is mostly compatible and much stabler, instead."
    )
    warnings.warn(message)
