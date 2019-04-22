# Standard Imports
from unittest import mock

# ThirdParty Imports
import asyncio

# Internal Imports
import slack


def fake_req_args(token=mock.ANY, data=mock.ANY, params=mock.ANY, json=mock.ANY):

    req_args = {
        "headers": {
            "User-Agent": slack.WebClient._get_user_agent(),
            "Authorization": token,
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
        return asyncio.get_event_loop().run_until_complete(coro(*args, **kwargs))

    return wrapper


def mock_send():
    response_mock = mock.Mock(name="Response")
    response_mock.return_value = {"data": {"ok": True}, "status_code": 200}
    send_request = mock.Mock(
        name="Request", side_effect=asyncio.coroutine(response_mock)
    )
    send_request.response = response_mock
    return send_request
