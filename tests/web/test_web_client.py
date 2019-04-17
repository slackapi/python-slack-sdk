# Standard Imports
import unittest
import asyncio
from unittest import mock

# import collections
# import signal

# ThirdParty Imports

# Internal Imports
import slack

# import slack.errors as e


def async_test(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))

    return wrapper


def SendMock():
    coro = mock.Mock(name="SendResult")
    coro.return_value = {"data": {"ok": True}, "status_code": 200}
    corofunc = mock.Mock(name="_send", side_effect=asyncio.coroutine(coro))
    corofunc.coro = coro
    return corofunc


@mock.patch("slack.WebClient._send", new_callable=SendMock)
class TestWebClient(unittest.TestCase):
    def setUp(self):
        self.client = slack.WebClient()

    def tearDown(self):
        pass

    def test_api_test(self, mock_send):
        resp = self.client.api_test()
        self.assertTrue(resp["ok"])

    @async_test
    async def test_api_test_async_again(self, mock_send):
        self.client.run_async = True
        resp = await self.client.api_test()
        self.assertTrue(resp["ok"])
