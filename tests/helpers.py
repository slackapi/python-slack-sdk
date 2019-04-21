# Standard Imports
from unittest import mock

# ThirdParty Imports
import asyncio

# Internal Imports
import slack


def mock_req_args(data=mock.ANY, params=mock.ANY, json=mock.ANY):

    req_args = {
        "headers": {
            "User-Agent": slack.WebClient._get_user_agent(),
            "Authorization": "Bearer None",
        },
        "data": data,
        "params": params,
        "json": json,
        "ssl": mock.ANY,
        "proxy": mock.ANY,
    }
    return req_args


def mock_rtm_response():
    coro = mock.Mock(name="RTMResponse")
    coro.return_value = {
        "headers": {},
        "data": {
            "ok": True,
            "url": "ws://localhost:8765",
            "self": {"id": "U01234ABC", "name": "robotoverlord"},
            "team": {
                "domain": "exampledomain",
                "id": "T123450FP",
                "name": "ExampleName",
            },
        },
        "status_code": 200,
    }
    corofunc = mock.Mock(name="mock_rtm_response", side_effect=asyncio.coroutine(coro))
    corofunc.coro = coro
    return corofunc


def async_test(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))

    return wrapper


def mock_api_response():
    coro = mock.Mock(name="SendResult")
    coro.return_value = {"data": {"ok": True}, "status_code": 200}
    corofunc = mock.Mock(name="_send", side_effect=asyncio.coroutine(coro))
    corofunc.coro = coro
    return corofunc
