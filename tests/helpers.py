# Standard Imports
from unittest import mock

# ThirdParty Imports
import asyncio

# Internal Imports
import slack
from slack.web.slack_response import SlackResponse


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
    data = {
        "client": mock.ANY,
        "http_verb": mock.ANY,
        "api_url": mock.ANY,
        "req_args": mock.ANY,
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
        "headers": mock.ANY,
        "status_code": 200,
    }
    coro.return_value = SlackResponse(**data)
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
    data = {
        "client": mock.ANY,
        "http_verb": mock.ANY,
        "api_url": mock.ANY,
        "req_args": mock.ANY,
        "data": {"ok": True},
        "headers": mock.ANY,
        "status_code": 200,
    }
    response_mock.return_value = SlackResponse(**data)

    send_request = mock.Mock(
        name="Request", side_effect=asyncio.coroutine(response_mock)
    )
    send_request.response = response_mock
    return send_request
