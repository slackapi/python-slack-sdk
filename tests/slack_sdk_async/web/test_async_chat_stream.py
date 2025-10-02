import json
import unittest
from urllib.parse import parse_qs, urlparse

from slack_sdk.errors import SlackRequestError
from slack_sdk.models.blocks.basic_components import FeedbackButtonObject
from slack_sdk.models.blocks.block_elements import FeedbackButtonsElement, IconButtonElement
from slack_sdk.models.blocks.blocks import ContextActionsBlock
from slack_sdk.web.async_client import AsyncWebClient
from tests.mock_web_api_server import cleanup_mock_web_api_server, setup_mock_web_api_server
from tests.slack_sdk.web.mock_web_api_handler import MockHandler
from tests.slack_sdk_async.helpers import async_test


class ChatStreamMockHandler(MockHandler):
    """Extended mock handler that captures request bodies for chat stream methods"""

    def _handle(self):
        try:
            # put_nowait is common between Queue & asyncio.Queue, it does not need to be awaited
            self.server.queue.put_nowait(self.path)

            # Standard auth and validation from parent
            if self.is_valid_token() and self.is_valid_user_agent():
                token = self.headers["authorization"].split(" ")[1]
                parsed_path = urlparse(self.path)
                len_header = self.headers.get("Content-Length") or 0
                content_len = int(len_header)
                post_body = self.rfile.read(content_len)
                request_body = None
                if post_body:
                    try:
                        post_body = post_body.decode("utf-8")
                        if post_body.startswith("{"):
                            request_body = json.loads(post_body)
                        else:
                            request_body = {k: v[0] for k, v in parse_qs(post_body).items()}
                    except UnicodeDecodeError:
                        pass
                else:
                    if parsed_path and parsed_path.query:
                        request_body = {k: v[0] for k, v in parse_qs(parsed_path.query).items()}

                # Store request body for chat stream endpoints
                if self.path in ["/chat.startStream", "/chat.appendStream", "/chat.stopStream"] and request_body:
                    if not hasattr(self.server, "chat_stream_requests"):
                        self.server.chat_stream_requests = {}
                    self.server.chat_stream_requests[self.path] = {
                        "token": token,
                        **request_body,
                    }

                # Load response file
                pattern = str(token).split("xoxb-", 1)[1]
                with open(f"tests/slack_sdk_fixture/web_response_{pattern}.json") as file:
                    body = json.load(file)

            else:
                body = self.invalid_auth

            if not body:
                body = self.not_found

            self.send_response(200)
            self.set_common_headers()
            self.wfile.write(json.dumps(body).encode("utf-8"))
            self.wfile.close()

        except Exception as e:
            self.logger.error(str(e), exc_info=True)
            raise


class TestAsyncChatStream(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self, ChatStreamMockHandler)
        self.client = AsyncWebClient(
            token="xoxb-chat_stream_test",
            base_url="http://localhost:8888",
        )

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    @async_test
    async def test_streams_a_short_message(self):
        streamer = await self.client.chat_stream(
            channel="C0123456789",
            thread_ts="123.000",
            recipient_team_id="T0123456789",
            recipient_user_id="U0123456789",
        )
        await streamer.append(markdown_text="nice!")
        await streamer.stop()

        self.assertEqual(self.received_requests.get("/chat.startStream", 0), 1)
        self.assertEqual(self.received_requests.get("/chat.appendStream", 0), 0)
        self.assertEqual(self.received_requests.get("/chat.stopStream", 0), 1)

        if hasattr(self.thread.server, "chat_stream_requests"):
            start_request = self.thread.server.chat_stream_requests.get("/chat.startStream", {})
            self.assertEqual(start_request.get("channel"), "C0123456789")
            self.assertEqual(start_request.get("thread_ts"), "123.000")
            self.assertEqual(start_request.get("recipient_team_id"), "T0123456789")
            self.assertEqual(start_request.get("recipient_user_id"), "U0123456789")

            stop_request = self.thread.server.chat_stream_requests.get("/chat.stopStream", {})
            self.assertEqual(stop_request.get("channel"), "C0123456789")
            self.assertEqual(stop_request.get("ts"), "123.123")
            self.assertEqual(stop_request.get("markdown_text"), "nice!")

    @async_test
    async def test_streams_a_long_message(self):
        streamer = await self.client.chat_stream(
            buffer_size=5,
            channel="C0123456789",
            recipient_team_id="T0123456789",
            recipient_user_id="U0123456789",
            thread_ts="123.000",
        )
        await streamer.append(markdown_text="**this messag")
        await streamer.append(markdown_text="e is", token="xoxb-chat_stream_test_token1")
        await streamer.append(markdown_text=" bold!")
        await streamer.append(markdown_text="*")
        await streamer.stop(
            blocks=[
                ContextActionsBlock(
                    elements=[
                        FeedbackButtonsElement(
                            positive_button=FeedbackButtonObject(text="good", value="+1"),
                            negative_button=FeedbackButtonObject(text="bad", value="-1"),
                        ),
                        IconButtonElement(
                            icon="trash",
                            text="delete",
                        ),
                    ],
                )
            ],
            markdown_text="*",
            token="xoxb-chat_stream_test_token2",
        )

        self.assertEqual(self.received_requests.get("/chat.startStream", 0), 1)
        self.assertEqual(self.received_requests.get("/chat.appendStream", 0), 1)
        self.assertEqual(self.received_requests.get("/chat.stopStream", 0), 1)

        if hasattr(self.thread.server, "chat_stream_requests"):
            start_request = self.thread.server.chat_stream_requests.get("/chat.startStream", {})
            self.assertEqual(start_request.get("channel"), "C0123456789")
            self.assertEqual(start_request.get("thread_ts"), "123.000")
            self.assertEqual(start_request.get("markdown_text"), "**this messag")
            self.assertEqual(start_request.get("recipient_team_id"), "T0123456789")
            self.assertEqual(start_request.get("recipient_user_id"), "U0123456789")

            append_request = self.thread.server.chat_stream_requests.get("/chat.appendStream", {})
            self.assertEqual(append_request.get("channel"), "C0123456789")
            self.assertEqual(append_request.get("markdown_text"), "e is bold!")
            self.assertEqual(append_request.get("token"), "xoxb-chat_stream_test_token1")
            self.assertEqual(append_request.get("ts"), "123.123")

            stop_request = self.thread.server.chat_stream_requests.get("/chat.stopStream", {})
            self.assertEqual(
                json.dumps(stop_request.get("blocks")),
                '[{"elements": [{"negative_button": {"text": {"emoji": true, "text": "bad", "type": "plain_text"}, "value": "-1"}, "positive_button": {"text": {"emoji": true, "text": "good", "type": "plain_text"}, "value": "+1"}, "type": "feedback_buttons"}, {"icon": "trash", "text": {"emoji": true, "text": "delete", "type": "plain_text"}, "type": "icon_button"}], "type": "context_actions"}]',
            )
            self.assertEqual(stop_request.get("channel"), "C0123456789")
            self.assertEqual(stop_request.get("markdown_text"), "**")
            self.assertEqual(stop_request.get("token"), "xoxb-chat_stream_test_token2")
            self.assertEqual(stop_request.get("ts"), "123.123")

    @async_test
    async def test_streams_errors_when_appending_to_an_unstarted_stream(self):
        streamer = await self.client.chat_stream(
            channel="C0123456789",
            thread_ts="123.000",
            token="xoxb-chat_stream_test_missing_ts",
        )
        with self.assertRaisesRegex(SlackRequestError, r"^Failed to stop stream: stream not started$"):
            await streamer.stop()

    @async_test
    async def test_streams_errors_when_appending_to_a_completed_stream(self):
        streamer = await self.client.chat_stream(
            channel="C0123456789",
            thread_ts="123.000",
        )
        await streamer.append(markdown_text="nice!")
        await streamer.stop()
        with self.assertRaisesRegex(SlackRequestError, r"^Cannot append to stream: stream state is completed$"):
            await streamer.append(markdown_text="more...")
        with self.assertRaisesRegex(SlackRequestError, r"^Cannot stop stream: stream state is completed$"):
            await streamer.stop()
