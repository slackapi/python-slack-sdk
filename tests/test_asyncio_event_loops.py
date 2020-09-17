import logging
import unittest
import asyncio

import pytest

from slack import WebClient, RTMClient


class TestAsyncioEventLoops(unittest.TestCase):
    """This test was added to verify the behavior of asyncio.new_event_loop().

    Also, the tests here ensure WebClient and RTMClient don't generate a large number of event loops
    even when a lot of those instances are created.
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        pass

    @pytest.mark.skip("The result of this test depends on the environment")
    def test_the_cost_of_event_loop_creation(self):
        # create 100 event loops
        loops = []
        try:
            upper_limit = 0
            for i in range(1000):
                try:
                    loops.append(asyncio.new_event_loop())
                except OSError as e:
                    self.logger.info(f"Got an OSError when creating {i} event loops")
                    self.assertEqual(e.errno, 24)
                    self.assertEqual(e.strerror, "Too many open files")
                    upper_limit = i
                    break
            self.assertTrue(upper_limit > 0)
        finally:
            for loop in loops:
                loop.close()

    def test_web_client_never_generate_huge_number_of_event_loops(self):
        num = 1000
        clients = []
        for i in range(num):
            clients.append(WebClient(token="xoxb-test", run_async=False))
        self.assertEqual(len(clients), num)

    def test_rtm_client_never_generate_huge_number_of_event_loops(self):
        num = 1000
        clients = []
        for i in range(num):
            clients.append(RTMClient(token="xoxb-test", run_async=False))
        self.assertEqual(len(clients), num)
