import logging
import os
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_BOT_TOKEN,
    SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID,
)
from integration_tests.helpers import async_test
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.async_base_client import AsyncSlackResponse


class TestAsyncWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API"""

    def setUp(self):
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(__name__)
            self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
            self.async_client: AsyncWebClient = AsyncWebClient(token=self.bot_token)
            self.channel_id = os.environ[SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID]

    def tearDown(self):
        pass

    # -------------------------
    # api.test

    @async_test
    async def test_api_test_async(self):
        response: AsyncSlackResponse = await self.async_client.api_test(foo="bar")
        self.assertEqual(response["args"]["foo"], "bar")

    # -------------------------
    # auth.test

    @async_test
    async def test_auth_test_async(self):
        response: AsyncSlackResponse = await self.async_client.auth_test()
        self.verify_auth_test_response(response)

    def verify_auth_test_response(self, response):
        self.assertIsNotNone(response["url"])
        self.assertIsNotNone(response["user"])
        self.assertIsNotNone(response["user_id"])
        self.assertIsNotNone(response["team"])
        self.assertIsNotNone(response["team_id"])
        self.assertIsNotNone(response["bot_id"])

    # -------------------------
    # basic metadata retrieval

    @async_test
    async def test_metadata_retrieval_async(self):
        client = self.async_client
        auth = await client.auth_test()
        self.assertIsNotNone(auth)
        bot = await client.bots_info(bot=auth["bot_id"])
        self.assertIsNotNone(bot)

    # -------------------------
    # basic chat operations

    @async_test
    async def test_basic_chat_operations_async(self):
        client = self.async_client

        auth = await client.auth_test()
        self.assertIsNotNone(auth)
        url = auth["url"]

        channel = self.channel_id
        message = (
            "This message was posted by <https://slack.dev/python-slackclient/|python-slackclient>! "
            + "(integration_tests/test_web_client.py #test_chat_operations)"
        )
        new_message: AsyncSlackResponse = await client.chat_postMessage(channel=channel, text=message)
        self.assertEqual(new_message["message"]["text"], message)
        ts = new_message["ts"]

        permalink = await client.chat_getPermalink(channel=channel, message_ts=ts)
        self.assertIsNotNone(permalink)
        self.assertRegex(
            permalink["permalink"],
            f"{url}archives/{channel}/.+",
        )

        new_reaction = await client.reactions_add(channel=channel, timestamp=ts, name="eyes")
        self.assertIsNotNone(new_reaction)

        reactions = await client.reactions_get(channel=channel, timestamp=ts)
        self.assertIsNotNone(reactions)

        reaction_removal = await client.reactions_remove(channel=channel, timestamp=ts, name="eyes")
        self.assertIsNotNone(reaction_removal)

        thread_reply = await client.chat_postMessage(channel=channel, thread_ts=ts, text="threading...")
        self.assertIsNotNone(thread_reply)

        modification = await client.chat_update(channel=channel, ts=ts, text="Is this intentional?")
        self.assertIsNotNone(modification)

        reply_deletion = await client.chat_delete(channel=channel, ts=thread_reply["ts"])
        self.assertIsNotNone(reply_deletion)
        message_deletion = await client.chat_delete(channel=channel, ts=ts)
        self.assertIsNotNone(message_deletion)

    # -------------------------
    # file operations

    @async_test
    async def test_uploading_text_files_async(self):
        client = self.async_client
        file, filename = __file__, os.path.basename(__file__)
        upload = await client.files_upload(
            channels=self.channel_id,
            title="Good Old Slack Logo",
            filename=filename,
            file=file,
        )
        self.assertIsNotNone(upload)

        deletion = await client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)

    @async_test
    async def test_uploading_binary_files_async(self):
        client = self.async_client
        current_dir = os.path.dirname(__file__)
        file = f"{current_dir}/../../tests/data/slack_logo.png"
        upload = await client.files_upload(
            channels=self.channel_id,
            title="Good Old Slack Logo",
            filename="slack_logo.png",
            file=file,
        )
        self.assertIsNotNone(upload)

        deletion = await client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)

    @async_test
    async def test_uploading_file_with_token_param_async(self):
        client = AsyncWebClient()
        current_dir = os.path.dirname(__file__)
        file = f"{current_dir}/../../tests/data/slack_logo.png"
        upload = await client.files_upload(
            token=self.bot_token,
            channels=self.channel_id,
            title="Good Old Slack Logo",
            filename="slack_logo.png",
            file=file,
        )
        self.assertIsNotNone(upload)

        deletion = await client.files_delete(
            token=self.bot_token,
            file=upload["file"]["id"],
        )
        self.assertIsNotNone(deletion)

    # -------------------------
    # pagination

    @async_test
    async def test_pagination_with_iterator_async(self):
        client = self.async_client
        fetched_count = 0
        # AsyncSlackResponse is an iterator that fetches next if next_cursor is not ""
        async for response in await client.conversations_list(limit=1, exclude_archived=1, types="public_channel"):
            fetched_count += len(response["channels"])
            if fetched_count > 1:
                break

        self.assertGreater(fetched_count, 1)
