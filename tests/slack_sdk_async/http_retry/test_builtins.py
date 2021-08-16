import unittest

from slack_sdk.http_retry.builtin_async_handlers import async_default_handlers


class TestBuiltins(unittest.TestCase):
    def test_default_ones(self):
        list = async_default_handlers()
        self.assertEqual(1, len(list))
        list.clear()
        self.assertEqual(0, len(list))
        list = async_default_handlers()
        self.assertEqual(1, len(list))
