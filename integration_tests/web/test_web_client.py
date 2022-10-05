import asyncio
import logging
import os
import unittest

import pytest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_BOT_TOKEN,
    SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID,
)
from integration_tests.helpers import async_test, is_not_specified
from slack_sdk.web import WebClient
from slack_sdk.web.slack_response import SlackResponse
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.legacy_client import LegacyWebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API"""

    def setUp(self):
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(__name__)
            self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
            self.async_client: AsyncWebClient = AsyncWebClient(token=self.bot_token)
            self.sync_client: WebClient = WebClient(token=self.bot_token)
            self.channel_id = os.environ[SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID]

    def tearDown(self):
        pass

    # -------------------------
    # api.test

    def test_api_test(self):
        response: SlackResponse = self.sync_client.api_test(foo="bar")
        self.assertEqual(response["args"]["foo"], "bar")

    @async_test
    async def test_api_test_async(self):
        response: SlackResponse = await self.async_client.api_test(foo="bar")
        self.assertEqual(response["args"]["foo"], "bar")

    # -------------------------
    # auth.test

    def test_auth_test(self):
        response: SlackResponse = self.sync_client.auth_test()
        self.verify_auth_test_response(response)

    @async_test
    async def test_auth_test_async(self):
        response: SlackResponse = await self.async_client.auth_test()
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

    def test_metadata_retrieval(self):
        client = self.sync_client
        auth = client.auth_test()
        self.assertIsNotNone(auth)
        bot = client.bots_info(bot=auth["bot_id"])
        self.assertIsNotNone(bot)

    @async_test
    async def test_metadata_retrieval_async(self):
        client = self.async_client
        auth = await client.auth_test()
        self.assertIsNotNone(auth)
        bot = await client.bots_info(bot=auth["bot_id"])
        self.assertIsNotNone(bot)

    # -------------------------
    # basic chat operations

    def test_basic_chat_operations(self):
        client = self.sync_client

        auth = client.auth_test()
        self.assertIsNotNone(auth)
        url = auth["url"]

        channel = self.channel_id
        message = (
            "This message was posted by <https://slack.dev/python-slackclient/|python-slackclient>! "
            + "(integration_tests/test_web_client.py #test_chat_operations)"
        )
        new_message: SlackResponse = client.chat_postMessage(channel=channel, text=message)
        self.assertEqual(new_message["message"]["text"], message)
        ts = new_message["ts"]

        permalink = client.chat_getPermalink(channel=channel, message_ts=ts)
        self.assertIsNotNone(permalink)
        self.assertRegex(
            permalink["permalink"],
            f"{url}archives/{channel}/.+",
        )

        new_reaction = client.reactions_add(channel=channel, timestamp=ts, name="eyes")
        self.assertIsNotNone(new_reaction)

        reactions = client.reactions_get(channel=channel, timestamp=ts)
        self.assertIsNotNone(reactions)

        reaction_removal = client.reactions_remove(channel=channel, timestamp=ts, name="eyes")
        self.assertIsNotNone(reaction_removal)

        thread_reply = client.chat_postMessage(channel=channel, thread_ts=ts, text="threading...")
        self.assertIsNotNone(thread_reply)

        modification = client.chat_update(channel=channel, ts=ts, text="Is this intentional?")
        self.assertIsNotNone(modification)

        reply_deletion = client.chat_delete(channel=channel, ts=thread_reply["ts"])
        self.assertIsNotNone(reply_deletion)
        message_deletion = client.chat_delete(channel=channel, ts=ts)
        self.assertIsNotNone(message_deletion)

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
        new_message: SlackResponse = await client.chat_postMessage(channel=channel, text=message)
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

    def test_uploading_text_files(self):
        client = self.sync_client
        file, filename = __file__, os.path.basename(__file__)
        upload = client.files_upload(channels=self.channel_id, filename=filename, file=file)
        self.assertIsNotNone(upload)

        deletion = client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)

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

    def test_uploading_binary_files(self):
        client = self.sync_client
        current_dir = os.path.dirname(__file__)
        file = f"{current_dir}/../../tests/data/slack_logo.png"
        upload = client.files_upload(
            channels=self.channel_id,
            title="Good Old Slack Logo",
            filename="slack_logo.png",
            file=file,
        )
        self.assertIsNotNone(upload)

        deletion = client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)

    def test_uploading_binary_files_as_content(self):
        client = self.sync_client
        current_dir = os.path.dirname(__file__)
        file = f"{current_dir}/../../tests/data/slack_logo.png"
        with open(file, "rb") as f:
            content = f.read()
            upload = client.files_upload(
                channels=self.channel_id,
                title="Good Old Slack Logo",
                filename="slack_logo.png",
                content=content,
            )
            self.assertIsNotNone(upload)

            deletion = client.files_delete(file=upload["file"]["id"])
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

    def test_uploading_file_with_token_param(self):
        client = WebClient()
        current_dir = os.path.dirname(__file__)
        file = f"{current_dir}/../../tests/data/slack_logo.png"
        upload = client.files_upload(
            token=self.bot_token,
            channels=self.channel_id,
            title="Good Old Slack Logo",
            filename="slack_logo.png",
            file=file,
        )
        self.assertIsNotNone(upload)

        deletion = client.files_delete(
            token=self.bot_token,
            file=upload["file"]["id"],
        )
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

    def test_pagination_with_iterator(self):
        client = self.sync_client
        fetched_count = 0
        # SlackResponse is an iterator that fetches next if next_cursor is not ""
        for response in client.conversations_list(limit=1, exclude_archived=1, types="public_channel"):
            fetched_count += len(response["channels"])
            if fetched_count > 1:
                break

        self.assertGreater(fetched_count, 1)

    def test_pagination_with_iterator_use_sync_aiohttp(self):
        client: LegacyWebClient = LegacyWebClient(
            token=self.bot_token,
            run_async=False,
            use_sync_aiohttp=True,
            loop=asyncio.new_event_loop(),
        )
        fetched_count = 0
        # SlackResponse is an iterator that fetches next if next_cursor is not ""
        for response in client.conversations_list(limit=1, exclude_archived=1, types="public_channel"):
            fetched_count += len(response["channels"])
            if fetched_count > 1:
                break

        self.assertGreater(fetched_count, 1)

    @pytest.mark.skipif(condition=is_not_specified(), reason="still unfixed")
    @async_test
    async def test_pagination_with_iterator_async(self):
        client = self.async_client
        fetched_count = 0
        # SlackResponse is an iterator that fetches next if next_cursor is not ""
        for response in await client.conversations_list(limit=1, exclude_archived=1, types="public_channel"):
            fetched_count += len(response["channels"])
            if fetched_count > 1:
                break

        self.assertGreater(fetched_count, 1)

    # ====================================================================================================== FAILURES =======================================================================================================
    # __________________________________________________________________________________ TestWebClient.test_pagination_with_iterator_async __________________________________________________________________________________
    #
    # args = (<test_web_client.TestWebClient testMethod=test_pagination_with_iterator_async>,), kwargs = {}, current_loop = <_UnixSelectorEventLoop running=False closed=False debug=False>
    #
    #     def wrapper(*args, **kwargs):
    #         current_loop: AbstractEventLoop = asyncio.get_event_loop()
    # >       return current_loop.run_until_complete(coro(*args, **kwargs))
    #
    # integration_tests/helpers.py:11:
    # _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    # path-to-python/asyncio/base_events.py:616: in run_until_complete
    #     return future.result()
    # integration_tests/web/test_web_client.py:183: in test_pagination_with_iterator_async
    #     for response in await client.conversations_list(limit=1, exclude_archived=1, types="public_channel"):
    # slack/web/slack_response.py:135: in __next__
    #     response = asyncio.get_event_loop().run_until_complete(
    # path-to-python/asyncio/base_events.py:592: in run_until_complete
    #     self._check_running()
    # _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    #
    # self = <_UnixSelectorEventLoop running=False closed=False debug=False>
    #
    #     def _check_running(self):
    #         if self.is_running():
    # >           raise RuntimeError('This event loop is already running')
    # E           RuntimeError: This event loop is already running
    #
    # path-to-python/asyncio/base_events.py:552: RuntimeError
