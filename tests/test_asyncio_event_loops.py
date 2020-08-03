import logging
import unittest

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
