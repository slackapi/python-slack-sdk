from copy import deepcopy
import unittest
from unittest.mock import patch

from slack_sdk import WebClient
from slack_sdk.models.blocks import ActionsBlock, ButtonElement, SectionBlock
from slack_sdk.models.views import View


class TestViewsPublishAgentPrompt(unittest.TestCase):
    def test_models_send_the_same_button_fields_as_raw_json(self):
        button = {
            "type": "button",
            "text": {"type": "plain_text", "text": "Summarize with Slackbot"},
            "action_id": "summarize_incident",
            "style": "primary",
            "agent_prompt": "Summarize this incident and suggest next steps.",
            "agent_prompt_display": "Summarize this incident",
            "visible_to_user_ids": ["U123456"],
        }
        blocks = (
            {"type": "actions", "elements": [button]},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Incident details"},
                "accessory": button,
            },
        )
        client = WebClient(token="xoxb-api_test")
        for block in blocks:
            block_class = ActionsBlock if block["type"] == "actions" else SectionBlock
            raw_view = {"type": "home", "blocks": [block]}
            explicit_button_block = deepcopy(block)
            if block["type"] == "actions":
                explicit_button_block["elements"] = [ButtonElement(**deepcopy(button))]
            else:
                explicit_button_block["accessory"] = ButtonElement(**deepcopy(button))
            views = {
                "raw_json": deepcopy(raw_view),
                "button_model": View(type="home", blocks=[block_class(**explicit_button_block)]),
                "raw_button_in_block_model": View(type="home", blocks=[block_class(**deepcopy(block))]),
                "raw_blocks_in_view_model": View(**deepcopy(raw_view)),
            }
            for representation, view in views.items():
                with self.subTest(placement=block["type"], representation=representation):
                    # Keep the SDK's serialization intact; intercept only the HTTP transport.
                    with patch.object(client, "_sync_send", return_value={"ok": True}) as transport:
                        client.views_publish(user_id="U123456", view=view)
                    transport.assert_called_once()
                    request = transport.call_args[1]["req_args"]["json"]
                    self.assertDictEqual({"user_id": "U123456", "view": raw_view}, request)
