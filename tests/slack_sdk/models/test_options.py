import unittest

from slack_sdk.models.blocks import (
    StaticSelectElement,
    Option,
)


class TestOptions(unittest.TestCase):
    def test_with_static_select_element(self):
        self.maxDiff = None

        elem = StaticSelectElement(
            action_id="action-id",
            initial_option=Option(value="option-1", text="Option 1"),
            options=[
                Option(value="option-1", text="Option 1"),
                Option(value="option-2", text="Option 2"),
                Option(value="option-3", text="Option 3"),
            ],
        )
        expected = {
            "action_id": "action-id",
            "initial_option": {
                "text": {"emoji": True, "text": "Option 1", "type": "plain_text"},
                "value": "option-1",
            },
            "options": [
                {
                    "text": {"emoji": True, "text": "Option 1", "type": "plain_text"},
                    "value": "option-1",
                },
                {
                    "text": {"emoji": True, "text": "Option 2", "type": "plain_text"},
                    "value": "option-2",
                },
                {
                    "text": {"emoji": True, "text": "Option 3", "type": "plain_text"},
                    "value": "option-3",
                },
            ],
            "type": "static_select",
        }
        self.assertDictEqual(expected, elem.to_dict())
