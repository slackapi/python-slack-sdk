import asyncio
import json
from asyncio import AbstractEventLoop
from logging import Logger
from typing import Optional, BinaryIO, List, Dict

import aiohttp
from aiohttp import ClientSession

from slack_sdk.errors import SlackApiError


def _get_event_loop() -> AbstractEventLoop:
    """Retrieves the event loop or creates a new one."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def _files_to_data(req_args: dict) -> List[BinaryIO]:
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

    response = None
    try:
        async with session.request(http_verb, api_url, **req_args) as res:
            data = {}
            try:
                data = await res.json()
            except aiohttp.ContentTypeError:
                logger.debug(
                    f"No response data returned from the following API call: {api_url}."
                )
            except json.decoder.JSONDecodeError as e:
                message = f"Failed to parse the response body: {str(e)}"
                raise SlackApiError(message, res)

            response = {
                "data": data,
                "headers": res.headers,
                "status_code": res.status,
            }
    finally:
        if not use_running_session:
            await session.close()
    return response
