import logging
import unittest

from slack_sdk.aiohttp_version_checker import validate_aiohttp_version


class TestAiohttpVersionChecker(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        pass

    def test_not_recommended_versions(self):
        state = {"counter": 0}

        def print(message: str):
            state["counter"] = state["counter"] + 1

        validate_aiohttp_version("2.1.3", print)
        self.assertEqual(state["counter"], 1)
        validate_aiohttp_version("3.6.3", print)
        self.assertEqual(state["counter"], 2)
        validate_aiohttp_version("3.7.0", print)
        self.assertEqual(state["counter"], 3)

    def test_recommended_versions(self):
        state = {"counter": 0}

        def print(message: str):
            state["counter"] = state["counter"] + 1

        validate_aiohttp_version("3.7.1", print)
        self.assertEqual(state["counter"], 0)
        validate_aiohttp_version("3.7.3", print)
        self.assertEqual(state["counter"], 0)
        validate_aiohttp_version("3.8.0", print)
        self.assertEqual(state["counter"], 0)
        validate_aiohttp_version("4.0.0", print)
        self.assertEqual(state["counter"], 0)
        validate_aiohttp_version("4.0.0rc1", print)
        self.assertEqual(state["counter"], 0)
