# Standard Imports
from unittest.mock import ANY, Mock

# ThirdParty Imports
import asyncio

# Internal Imports
from slack.web.slack_response import SlackResponse


def fake_req_args(headers=ANY, data=ANY, params=ANY, json=ANY):
    req_args = {
        "headers": headers,
        "data": data,
        "params": params,
        "json": json,
        "ssl": ANY,
        "proxy": ANY,
    }
    return req_args


def fake_send_req_args(headers=ANY, data=ANY, params=ANY, json=ANY):
    req_args = {
        "headers": headers,
        "data": data,
        "params": params,
        "json": json,
        "ssl": ANY,
        "proxy": ANY,
        "files": ANY,
    }
    return req_args


def mock_rtm_response():
    coro = Mock(name="RTMResponse")
    data = {
        "client": ANY,
        "http_verb": ANY,
        "api_url": ANY,
        "req_args": ANY,
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
        "headers": ANY,
        "status_code": 200,
    }
    coro.return_value = SlackResponse(**data)
    corofunc = Mock(name="mock_rtm_response", side_effect=asyncio.coroutine(coro))
    corofunc.coro = coro
    return corofunc


def async_test(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(coro(*args, **kwargs))

    return wrapper


def mock_request():
    response_mock = Mock(name="Response")
    data = {"data": {"ok": True}, "headers": ANY, "status_code": 200}
    response_mock.return_value = data

    send_request = Mock(name="Request", side_effect=asyncio.coroutine(response_mock))
    send_request.response = response_mock
    return send_request
