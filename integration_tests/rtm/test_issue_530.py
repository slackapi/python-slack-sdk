import asyncio
import collections
import logging
import unittest

from integration_tests.helpers import async_test
from slack_sdk.rtm import RTMClient


class TestRTMClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slack-sdk/issues/530
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        # Reset the decorators by @RTMClient.run_on
        RTMClient._callbacks = collections.defaultdict(list)

    def test_issue_530(self):
        try:
            rtm_client = RTMClient(token="I am not a token", run_async=False, loop=asyncio.new_event_loop())
            rtm_client.start()
            self.fail("Raising an error here was expected")
        except Exception as e:
            self.assertEqual(
                "The request to the Slack API failed.\n" "The server responded with: {'ok': False, 'error': 'invalid_auth'}",
                str(e),
            )
        finally:
            if not rtm_client._stopped:
                rtm_client.stop()

    @async_test
    async def test_issue_530_async(self):
        try:
            rtm_client = RTMClient(token="I am not a token", run_async=True)
            await rtm_client.start()
            self.fail("Raising an error here was expected")
        except Exception as e:
            self.assertEqual(
                "The request to the Slack API failed.\n" "The server responded with: {'ok': False, 'error': 'invalid_auth'}",
                str(e),
            )
        finally:
            if not rtm_client._stopped:
                rtm_client.stop()

    # =============================================================================================== short test summary info ===============================================================================================
    # FAILED integration_tests/rtm/test_issue_530.py::TestRTMClient::test_issue_530 - AssertionError: "'NoneType' object is not subscriptable" != "The server responded with: {'ok': False, 'error': 'invalid_auth'}"
    # FAILED integration_tests/rtm/test_issue_530.py::TestRTMClient::test_issue_530_async - AssertionError: "'NoneType' object is not subscriptable" != "The server responded with: {'ok': False, 'error': 'invalid_auth'}"
    # ====================================================================================== 2 failed, 1 skipped, 5 warnings in 1.54s =======================================================================================
