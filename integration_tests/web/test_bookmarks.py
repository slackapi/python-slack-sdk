import logging
import os
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_BOT_TOKEN,
    SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID,
)
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient


class TestBookmarks(unittest.TestCase):
    """Runs integration tests with real Slack API testing the bookmarks.* APIs"""

    def setUp(self):
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(__name__)
            self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
            self.async_client: AsyncWebClient = AsyncWebClient(token=self.bot_token)
            self.sync_client: WebClient = WebClient(token=self.bot_token)
            self.channel_id = os.environ[SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID]

    def tearDown(self):
        pass

    def test_adding_listing_editing_removing_bookmark(self):
        client = self.sync_client
        # create a new bookmark
        bookmark = client.bookmarks_add(
            channel_id=self.channel_id,
            title="slack!",
            type="link",
            link="https://slack.com",
        )
        self.assertIsNotNone(bookmark)
        bookmark_id = bookmark["bookmark"]["id"]
        # make sure we find the bookmark we just added
        all_bookmarks = client.bookmarks_list(channel_id=self.channel_id)
        self.assertIsNotNone(all_bookmarks)
        self.assertIsNotNone(next((b for b in all_bookmarks["bookmarks"] if b["id"] == bookmark_id), None))
        # edit the bookmark
        bookmark = client.bookmarks_edit(
            bookmark_id=bookmark_id,
            channel_id=self.channel_id,
            title="slack api!",
            type="link",
            link="https://api.slack.com",
        )
        self.assertIsNotNone(bookmark)
        # make sure we find the edited bookmark we just added
        all_bookmarks = client.bookmarks_list(channel_id=self.channel_id)
        self.assertIsNotNone(all_bookmarks)
        edited_bookmark = next((b for b in all_bookmarks["bookmarks"] if b["id"] == bookmark_id), None)
        self.assertIsNotNone(edited_bookmark)
        self.assertEqual(edited_bookmark["title"], "slack api!")
        # remove the bookmark
        removed_bookmark = client.bookmarks_remove(bookmark_id=bookmark_id, channel_id=self.channel_id)
        self.assertIsNotNone(removed_bookmark)
        # make sure we cannot find the bookmark we just removed
        all_bookmarks = client.bookmarks_list(channel_id=self.channel_id)
        self.assertIsNotNone(all_bookmarks)
        self.assertIsNone(next((b for b in all_bookmarks if b["id"] == bookmark_id), None))
