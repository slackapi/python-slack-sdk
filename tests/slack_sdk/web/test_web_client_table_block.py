import unittest
from unittest.mock import Mock, patch

from slack_sdk import WebClient
from slack_sdk.models.blocks import TableBlock, RawTextObject


class TestWebClientTableBlock(unittest.TestCase):
    """Tests to verify the correct approach for sending table blocks"""

    def setUp(self):
        self.client = WebClient(token="xoxb-test-token", base_url="http://localhost:8888")

        # Create a sample table block
        self.table = TableBlock(
            rows=[
                [{"type": "raw_text", "text": "Product"}, {"type": "raw_text", "text": "Price"}],
                [{"type": "raw_text", "text": "Widget"}, {"type": "raw_text", "text": "$10"}],
                [{"type": "raw_text", "text": "Gadget"}, {"type": "raw_text", "text": "$20"}],
            ],
            column_settings=[{"is_wrapped": True}, {"align": "right"}],
        )

    @patch("slack_sdk.web.client.WebClient.api_call")
    def test_table_in_attachments_blocks(self, mock_api_call):
        """Test sending table block in attachments.blocks (documented approach)"""
        mock_api_call.return_value = {"ok": True, "channel": "C123", "ts": "1234567890.123456"}

        # Method 1: Table in attachments
        response = self.client.chat_postMessage(
            channel="C123456789",
            text="Here's a table:",
            attachments=[{"blocks": [self.table.to_dict()]}],
        )

        # Verify the call was made
        self.assertTrue(mock_api_call.called)
        call_args = mock_api_call.call_args

        # Check that attachments were passed correctly (WebClient wraps in 'json' key)
        self.assertIn("json", call_args[1])
        json_data = call_args[1]["json"]
        self.assertIn("attachments", json_data)
        attachments = json_data["attachments"]
        self.assertEqual(len(attachments), 1)
        self.assertIn("blocks", attachments[0])
        self.assertEqual(attachments[0]["blocks"][0]["type"], "table")

    @patch("slack_sdk.web.client.WebClient.api_call")
    def test_table_in_top_level_blocks(self, mock_api_call):
        """Test sending table block in top-level blocks array (alternative approach)"""
        mock_api_call.return_value = {"ok": True, "channel": "C123", "ts": "1234567890.123456"}

        # Method 2: Table in top-level blocks
        response = self.client.chat_postMessage(
            channel="C123456789",
            text="Here's a table:",
            blocks=[self.table.to_dict()],
        )

        # Verify the call was made
        self.assertTrue(mock_api_call.called)
        call_args = mock_api_call.call_args

        # Check that blocks were passed correctly (WebClient wraps in 'json' key)
        self.assertIn("json", call_args[1])
        json_data = call_args[1]["json"]
        self.assertIn("blocks", json_data)
        blocks = json_data["blocks"]
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["type"], "table")

    @patch("slack_sdk.web.client.WebClient.api_call")
    def test_table_with_raw_text_object_helper(self, mock_api_call):
        """Test creating table using RawTextObject helper"""
        mock_api_call.return_value = {"ok": True, "channel": "C123", "ts": "1234567890.123456"}

        # Create table using RawTextObject helper
        table_with_helper = TableBlock(
            rows=[
                [RawTextObject(text="Name").to_dict(), RawTextObject(text="Age").to_dict()],
                [RawTextObject(text="Alice").to_dict(), RawTextObject(text="30").to_dict()],
            ]
        )

        response = self.client.chat_postMessage(
            channel="C123456789",
            text="Table with helpers:",
            attachments=[{"blocks": [table_with_helper.to_dict()]}],
        )

        # Verify the call was made and table structure is correct
        self.assertTrue(mock_api_call.called)
        call_args = mock_api_call.call_args
        json_data = call_args[1]["json"]
        attachments = json_data["attachments"]
        table_dict = attachments[0]["blocks"][0]

        self.assertEqual(table_dict["type"], "table")
        self.assertEqual(table_dict["rows"][0][0]["type"], "raw_text")
        self.assertEqual(table_dict["rows"][0][0]["text"], "Name")

    def test_table_to_dict_serialization(self):
        """Test that TableBlock.to_dict() produces correct structure"""
        table_dict = self.table.to_dict()

        # Verify structure
        self.assertEqual(table_dict["type"], "table")
        self.assertIn("rows", table_dict)
        self.assertIn("column_settings", table_dict)

        # Verify rows structure
        self.assertEqual(len(table_dict["rows"]), 3)
        self.assertEqual(table_dict["rows"][0][0]["type"], "raw_text")
        self.assertEqual(table_dict["rows"][0][0]["text"], "Product")

        # Verify column settings
        self.assertEqual(len(table_dict["column_settings"]), 2)
        self.assertEqual(table_dict["column_settings"][0]["is_wrapped"], True)
        self.assertEqual(table_dict["column_settings"][1]["align"], "right")

    @patch("slack_sdk.web.client.WebClient.api_call")
    def test_multiple_tables_not_allowed(self, mock_api_call):
        """Test that only one table per message is allowed (per Slack documentation)"""
        mock_api_call.return_value = {"ok": True, "channel": "C123", "ts": "1234567890.123456"}

        table2 = TableBlock(rows=[[{"type": "raw_text", "text": "Another table"}]])

        # According to docs, this should only send one table
        # The SDK doesn't enforce this, but Slack API will return error
        response = self.client.chat_postMessage(
            channel="C123456789",
            text="Multiple tables:",
            attachments=[
                {"blocks": [self.table.to_dict()]},
                {"blocks": [table2.to_dict()]},
            ],
        )

        # Verify both tables were sent (SDK allows it, but Slack API will reject)
        self.assertTrue(mock_api_call.called)
        call_args = mock_api_call.call_args
        json_data = call_args[1]["json"]
        attachments = json_data["attachments"]
        self.assertEqual(len(attachments), 2)

    def test_table_with_rich_text_cells(self):
        """Test table with rich_text cells (links, formatting)"""
        table_with_rich_text = TableBlock(
            rows=[
                [{"type": "raw_text", "text": "Header A"}, {"type": "raw_text", "text": "Header B"}],
                [
                    {"type": "raw_text", "text": "Data 1A"},
                    {
                        "type": "rich_text",
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [{"text": "Data 1B", "type": "link", "url": "https://slack.com"}],
                            }
                        ],
                    },
                ],
            ]
        )

        table_dict = table_with_rich_text.to_dict()

        # Verify mixed cell types
        self.assertEqual(table_dict["rows"][0][0]["type"], "raw_text")
        self.assertEqual(table_dict["rows"][1][1]["type"], "rich_text")
        self.assertIn("elements", table_dict["rows"][1][1])


if __name__ == "__main__":
    unittest.main()
