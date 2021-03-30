import asyncio
import json
import logging
from asyncio import AbstractEventLoop
from logging import Logger
from typing import Optional, BinaryIO, Dict, Sequence, Union

import aiohttp
from aiohttp import ClientSession

from slack_sdk.errors import SlackApiError
from slack_sdk.web.internal_utils import _build_unexpected_body_error_message


def _get_event_loop() -> AbstractEventLoop:
    """Retrieves the event loop or creates a new one."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def _files_to_data(req_args: dict) -> Sequence[BinaryIO]:
    open_files = []
    files = req_args.pop("files", None)
    if files is not None:
        for k, v in files.items():
            if isinstance(v, str):
                f = open(v.encode("utf-8", "ignore"), "rb")
                open_files.append(f)
                req_args["data"].update({k: f})
            else:
                req_args["data"].update({k: v})
    return open_files


async def _request_with_session(
    *,
    current_session: Optional[ClientSession],
    timeout: int,
    logger: Logger,
    http_verb: str,
    api_url: str,
    req_args: dict,
) -> Dict[str, any]:
    """Submit the HTTP request with the running session or a new session.
    Returns:
        A dictionary of the response data.
    """
    session = None
    use_running_session = current_session and not current_session.closed
    if use_running_session:
        session = current_session
    else:
        session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout),
            auth=req_args.pop("auth", None),
        )

    if logger.level <= logging.DEBUG:

        def convert_params(values: dict) -> dict:
            if not values or not isinstance(values, dict):
                return {}
            return {
                k: ("(bytes)" if isinstance(v, bytes) else v) for k, v in values.items()
            }

        headers = {
            k: "(redacted)" if k.lower() == "authorization" else v
            for k, v in req_args.get("headers", {}).items()
        }
        logger.debug(
            f"Sending a request - url: {http_verb} {api_url}, "
            f"params: {convert_params(req_args.get('params'))}, "
            f"files: {convert_params(req_args.get('files'))}, "
            f"data: {convert_params(req_args.get('data'))}, "
            f"json: {convert_params(req_args.get('json'))}, "
            f"proxy: {convert_params(req_args.get('proxy'))}, "
            f"headers: {headers}"
        )

    response = None
    try:
        async with session.request(http_verb, api_url, **req_args) as res:
            data: Union[dict, bytes] = {}
            if res.content_type == "application/gzip":
                # admin.analytics.getFile
                data = await res.read()
            else:
                try:
                    data = await res.json()
                except aiohttp.ContentTypeError:
                    logger.debug(
                        f"No response data returned from the following API call: {api_url}."
                    )
                except json.decoder.JSONDecodeError:
                    try:
                        body: str = await res.text()
                        message = _build_unexpected_body_error_message(body)
                        raise SlackApiError(message, res)
                    except Exception as e:
                        raise SlackApiError(
                            f"Unexpectedly failed to read the response body: {str(e)}",
                            res,
                        )

            response = {
                "data": data,
                "headers": res.headers,
                "status_code": res.status,
            }
    finally:
        if not use_running_session:
            await session.close()
    return response
