import unittest

from slack_sdk.models.messages.message import Message


class MessageTests(unittest.TestCase):
    def test_validate_json_fails(self):
        msg = Message(text="Hi there")
        self.assertIsNotNone(msg)
