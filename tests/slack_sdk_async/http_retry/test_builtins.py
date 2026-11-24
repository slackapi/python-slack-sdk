import unittest

from aiohttp import ClientError, ClientHttpProxyError, ClientResponseError, RequestInfo
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from slack_sdk.http_retry.builtin_async_handlers import AsyncConnectionErrorRetryHandler, async_default_handlers
from slack_sdk.http_retry.request import HttpRequest
from slack_sdk.http_retry.response import HttpResponse
from slack_sdk.http_retry.state import RetryState
from tests.slack_sdk_async.helpers import async_test


class TestBuiltins(unittest.TestCase):
    def test_default_ones(self):
        list = async_default_handlers()
        self.assertEqual(1, len(list))
        list.clear()
        self.assertEqual(0, len(list))
        list = async_default_handlers()
        self.assertEqual(1, len(list))

    @async_test
    async def test_connection_error_handler_skips_status_errors(self):
        url = URL("https://slack.com/api/auth.test")
        status_error = ClientResponseError(
            RequestInfo(url=url, method="POST", headers=CIMultiDictProxy(CIMultiDict()), real_url=url),
            (),
            status=500,
        )
        handler = AsyncConnectionErrorRetryHandler(error_types=[ClientError])

        can_retry = await handler.can_retry_async(
            state=RetryState(),
            request=HttpRequest(method="POST", url=str(url), headers={}),
            response=HttpResponse(status_code=500, headers={}),
            error=status_error,
        )

        self.assertFalse(can_retry)

    @async_test
    async def test_connection_error_handler_retries_errors_without_a_response(self):
        url = URL("https://slack.com/api/auth.test")
        proxy_error = ClientHttpProxyError(
            RequestInfo(url=url, method="POST", headers=CIMultiDictProxy(CIMultiDict()), real_url=url),
            (),
            status=407,
        )
        handler = AsyncConnectionErrorRetryHandler(error_types=[ClientError])

        can_retry = await handler.can_retry_async(
            state=RetryState(),
            request=HttpRequest(method="POST", url=str(url), headers={}),
            response=None,
            error=proxy_error,
        )

        self.assertTrue(can_retry)
