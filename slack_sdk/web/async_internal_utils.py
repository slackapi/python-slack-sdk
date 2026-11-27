import asyncio
import json
import logging
from asyncio import AbstractEventLoop
from contextlib import ExitStack
from logging import Logger
from typing import Optional, Dict, Union, List, Any

import aiohttp
from aiohttp import ClientSession

from slack_sdk.errors import SlackApiError
from slack_sdk.web.internal_utils import _build_unexpected_body_error_message

from slack_sdk.http_retry.async_handler import AsyncRetryHandler
from slack_sdk.http_retry.request import HttpRequest as RetryHttpRequest
from slack_sdk.http_retry.response import HttpResponse as RetryHttpResponse
from slack_sdk.http_retry.state import RetryState


def _get_event_loop() -> AbstractEventLoop:
    """Retrieves the event loop or creates a new one."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def _files_to_data(req_args: dict) -> ExitStack:
    with ExitStack() as stack:
        files = req_args.pop("files", None)
        if files is not None:
            for k, v in files.items():
                if isinstance(v, str):
                    f = stack.enter_context(open(v.encode("utf-8", "ignore"), "rb"))
                    req_args["data"].update({k: f})
                else:
                    req_args["data"].update({k: v})
        return stack.pop_all()


async def _request_with_session(
    *,
    current_session: Optional[ClientSession],
    timeout: int,
    logger: Logger,
    http_verb: str,
    api_url: str,
    req_args: dict,
    # set the default to an empty array for legacy clients
    retry_handlers: Optional[List[AsyncRetryHandler]] = None,
) -> Dict[str, Any]:
    """Submit the HTTP request with the running session or a new session.

    Returns:
        A dictionary of the response data.
    """
    retry_handlers = retry_handlers if retry_handlers is not None else []
    session = None
    use_running_session = current_session and not current_session.closed
    if use_running_session:
        session = current_session
    else:
        session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout),
            auth=req_args.pop("auth", None),
        )

    last_error: Optional[Exception] = None
    response: Optional[Dict[str, Any]] = None
    try:
        retry_request = RetryHttpRequest(
            method=http_verb,
            url=api_url,
            headers=req_args.get("headers", {}),
            body_params=req_args.get("params"),
            data=req_args.get("data"),
        )

        retry_state = RetryState()
        counter_for_safety = 0
        while counter_for_safety < 100:
            counter_for_safety += 1
            # If this is a retry, the next try started here. We can reset the flag.
            retry_state.next_attempt_requested = False
            retry_response: Optional[RetryHttpResponse] = None

            if logger.isEnabledFor(logging.DEBUG):

                def convert_params(values: dict) -> dict:
                    if not values or not isinstance(values, dict):
                        return {}
                    return {k: ("(bytes)" if isinstance(v, bytes) else v) for k, v in values.items()}

                headers = {
                    k: "(redacted)" if k.lower() == "authorization" else v for k, v in req_args.get("headers", {}).items()
                }
                logger.debug(
                    f"Sending a request - url: {http_verb} {api_url}, "
                    f"params: {convert_params(req_args.get('params', 'n/a'))}, "
                    f"files: {convert_params(req_args.get('files', 'n/a'))}, "
                    f"data: {convert_params(req_args.get('data', 'n/a'))}, "
                    f"json: {convert_params(req_args.get('json', 'n/a'))}, "
                    f"proxy: {convert_params(req_args.get('proxy', 'n/a'))}, "
                    f"headers: {headers}"
                )

            try:
                async with session.request(http_verb, api_url, **req_args) as res:  # type: ignore[union-attr]
                    data: Union[dict, bytes, str] = {}
                    if res.content_type == "application/gzip":
                        # admin.analytics.getFile
                        data = await res.read()
                        retry_response = RetryHttpResponse(
                            status_code=res.status,
                            headers=res.headers,  # type: ignore[arg-type]
                            data=data,
                        )
                    elif res.content_type == "text/plain":
                        # https://files.slack.com/upload/v1/...
                        data = await res.text()
                        retry_response = RetryHttpResponse(
                            status_code=res.status,
                            headers=res.headers,  # type: ignore[arg-type]
                            data=data,  # type: ignore[arg-type]
                        )
                    else:
                        try:
                            data = await res.json()
                            retry_response = RetryHttpResponse(
                                status_code=res.status,
                                headers=res.headers,  # type: ignore[arg-type]
                                body=data,  # type: ignore[arg-type]
                            )
                        except aiohttp.ContentTypeError:
                            logger.debug(f"No response data returned from the following API call: {api_url}.")
                            retry_response = RetryHttpResponse(
                                status_code=res.status,
                                headers=res.headers,  # type: ignore[arg-type]
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

                    if logger.isEnabledFor(logging.DEBUG):
                        body = "(binary)"
                        if isinstance(data, dict) or isinstance(data, str):
                            body = data  # type: ignore[assignment]
                        logger.debug(
                            "Received the following response - "
                            f"status: {res.status}, "
                            f"headers: {dict(res.headers)}, "
                            f"body: {body}"
                        )

                    error: Optional[aiohttp.ClientResponseError] = None
                    try:
                        res.raise_for_status()
                    except aiohttp.ClientResponseError as e:
                        error = e

                    for handler in retry_handlers:
                        if await handler.can_retry_async(
                            state=retry_state,
                            request=retry_request,
                            response=retry_response,
                            error=error,
                        ):
                            if logger.isEnabledFor(logging.DEBUG):
                                logger.debug(f"A retry handler found: {type(handler).__name__} for {http_verb} {api_url}")
                            await handler.prepare_for_next_attempt_async(
                                state=retry_state,
                                request=retry_request,
                                response=retry_response,
                                error=error,
                            )
                            logger.info(f"Going to retry the same request: {http_verb} {api_url}")
                            break

                    response = {
                        "data": data,
                        "headers": res.headers,
                        "status_code": res.status,
                    }
                    if retry_state.next_attempt_requested is False:
                        return response

            except Exception as e:
                last_error = e
                for handler in retry_handlers:
                    if await handler.can_retry_async(
                        state=retry_state,
                        request=retry_request,
                        response=retry_response,
                        error=e,
                    ):
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"A retry handler found: {type(handler).__name__} for {http_verb} {api_url} - {e}")
                        await handler.prepare_for_next_attempt_async(
                            state=retry_state,
                            request=retry_request,
                            response=retry_response,
                            error=e,
                        )
                        logger.info(f"Going to retry the same request: {http_verb} {api_url}")
                        break

                if retry_state.next_attempt_requested is False:
                    raise last_error

        if response is not None:
            return response
        raise last_error  # type: ignore[misc]

    finally:
        if not use_running_session:
            await session.close()  # type: ignore[union-attr]
