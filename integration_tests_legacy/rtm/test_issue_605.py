import collections
import logging
import os
import threading
import time
import unittest

import pytest

from integration_tests.env_variable_names import \
    SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN, \
    SLACK_SDK_TEST_RTM_TEST_CHANNEL_ID
from integration_tests.helpers import is_not_specified
from slack import RTMClient, WebClient


class TestRTMClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slackclient/issues/605
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.bot_token = os.environ[SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN]
        self.channel_id = os.environ[SLACK_SDK_TEST_RTM_TEST_CHANNEL_ID]
        self.rtm_client = RTMClient(token=self.bot_token, run_async=False)

    def tearDown(self):
        # Reset the decorators by @RTMClient.run_on
        RTMClient._callbacks = collections.defaultdict(list)

    @pytest.mark.skipif(condition=is_not_specified(), reason="To avoid rate_limited errors")
    def test_issue_605(self):
        self.text = "This message was sent to verify issue #605"
        self.called = False

        @RTMClient.run_on(event="message")
        def process_messages(**payload):
            self.logger.info(payload)
            self.called = True

        def connect():
            self.logger.debug("Starting RTM Client...")
            self.rtm_client.start()

        t = threading.Thread(target=connect)
        t.setDaemon(True)
        try:
            t.start()
            self.assertFalse(self.called)

            time.sleep(3)

            self.web_client = WebClient(
                token=self.bot_token,
                run_async=False,
            )
            new_message = self.web_client.chat_postMessage(channel=self.channel_id, text=self.text)
            self.assertFalse("error" in new_message)

            time.sleep(5)
            self.assertTrue(self.called)
        finally:
            t.join(.3)

    # --- a/slack/rtm/client.py
    # +++ b/slack/rtm/client.py
    # @@ -10,7 +10,6 @@ import inspect
    #  import signal
    #  from typing import Optional, Callable, DefaultDict
    #  from ssl import SSLContext
    # -from threading import current_thread, main_thread
    #
    #  # ThirdParty Imports
    #  import asyncio
    # @@ -186,7 +185,8 @@ class RTMClient(object):
    #              SlackApiError: Unable to retrieve RTM URL from Slack.
    #          """
    #          # TODO: Add Windows support for graceful shutdowns.
    # -        if os.name != "nt" and current_thread() == main_thread():
    # +        # if os.name != "nt" and current_thread() == main_thread():
    # +        if os.name != "nt":
    #              signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    #              for s in signals:
    #                  self._event_loop.add_signal_handler(s, self.stop)

    # Exception in thread Thread-1:
    # Traceback (most recent call last):
    #   File "/path-to-python/asyncio/unix_events.py", line 95, in add_signal_handler
    #     signal.set_wakeup_fd(self._csock.fileno())
    # ValueError: set_wakeup_fd only works in main thread
    #
    # During handling of the above exception, another exception occurred:
    #
    # Traceback (most recent call last):
    #   File "/path-to-python/threading.py", line 932, in _bootstrap_inner
    #     self.run()
    #   File "/path-to-python/threading.py", line 870, in run
    #     self._target(*self._args, **self._kwargs)
    #   File "/path-to-project/python-slackclient/integration_tests/rtm/test_issue_605.py", line 29, in connect
    #     self.rtm_client.start()
    #   File "/path-to-project/python-slackclient/slack/rtm/client.py", line 192, in start
    #     self._event_loop.add_signal_handler(s, self.stop)
    #   File "/path-to-python/asyncio/unix_events.py", line 97, in add_signal_handler
    #     raise RuntimeError(str(exc))
    # RuntimeError: set_wakeup_fd only works in main thread
