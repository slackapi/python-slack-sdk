import logging
import os
import time
from typing import Optional
import unittest

from slack_sdk.web.slack_response import SlackResponse
from slack_sdk.errors import SlackApiError
from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_CONNECT_INVITE_SENDER_BOT_TOKEN,
    SLACK_SDK_TEST_CONNECT_INVITE_RECEIVER_BOT_TOKEN,
    SLACK_SDK_TEST_CONNECT_INVITE_RECEIVER_BOT_USER_ID,
)
from integration_tests.helpers import async_test
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with Slack API for conversations.* endpoints
    To run, we use two workspace-level bot tokens,
    one for the inviting workspace(list and send invites) another for the recipient
    workspace (accept and approve) sent invites. Before being able to run this test suite,
    we also need to have manually created a slack connect shared channel and added
    these two bots as members first. See: https://docs.slack.dev/apis/slack-connect/

    In addition to conversations.connect:* scopes, your sender bot token should have channels:manage scopes.
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.sender_bot_token = os.environ[SLACK_SDK_TEST_CONNECT_INVITE_SENDER_BOT_TOKEN]
        self.receiver_bot_token = os.environ[SLACK_SDK_TEST_CONNECT_INVITE_RECEIVER_BOT_TOKEN]
        self.sender_sync_client: WebClient = WebClient(token=self.sender_bot_token)
        self.sender_async_client: AsyncWebClient = AsyncWebClient(token=self.sender_bot_token)
        self.receiver_sync_client: WebClient = WebClient(token=self.receiver_bot_token)
        self.receiver_async_client: AsyncWebClient = AsyncWebClient(token=self.receiver_bot_token)

    def tearDown(self):
        pass

    def test_sync(self):
        sender = self.sender_sync_client
        receiver = self.receiver_sync_client
        channel_id: Optional[str] = None

        try:
            auth_test: SlackResponse = receiver.auth_test()
            self.assertIsNotNone(auth_test["team_id"])
            connect_team_id = auth_test["team_id"]

            # list senders pending connect invites
            connect_invites: SlackResponse = sender.conversations_listConnectInvites()
            self.assertIsNotNone(connect_invites["invites"])

            # creates channel in sender workspace to share
            unique_channel_name = str(int(time.time())) + "-shared"
            new_channel: SlackResponse = sender.conversations_create(name=unique_channel_name)
            self.assertIsNotNone(new_channel["channel"])
            self.assertIsNotNone(new_channel["channel"]["id"])
            channel_id = new_channel["channel"]["id"]

            # send an invite for sender's intended shared channel to receiver's bot user id
            invite: SlackResponse = sender.conversations_inviteShared(
                channel=new_channel["channel"]["id"],
                user_ids=os.environ[SLACK_SDK_TEST_CONNECT_INVITE_RECEIVER_BOT_USER_ID],
            )
            self.assertIsNotNone(invite["invite_id"])

            # receiver accept conversations invite via invite id
            accepted: SlackResponse = receiver.conversations_acceptSharedInvite(
                channel_name=unique_channel_name,
                invite_id=invite["invite_id"],
            )
            self.assertIsNone(accepted["error"])

            # receiver attempt to approve invite already accepted by an admin level token should fail
            self.assertRaises(
                SlackApiError,
                receiver.conversations_approveSharedInvite,
                invite_id=invite["invite_id"],
            )

            sender_approval = sender.conversations_approveSharedInvite(
                invite_id=invite["invite_id"], team_id=connect_team_id
            )
            self.assertIsNone(sender_approval["error"])

            downgrade = sender.conversations_externalInvitePermissions_set(
                channel=channel_id, target_team=connect_team_id, action="downgrade"
            )
            self.assertIsNone(downgrade["error"])

            upgrade = sender.conversations_externalInvitePermissions_set(
                channel=channel_id, target_team=connect_team_id, action="upgrade"
            )
            self.assertIsNone(upgrade["error"])
        finally:
            if channel_id is not None:
                # clean up created channel
                delete_channel: SlackResponse = sender.conversations_archive(channel=new_channel["channel"]["id"])
                self.assertIsNotNone(delete_channel)

    @async_test
    async def test_async(self):
        sender = self.sender_async_client
        receiver = self.receiver_async_client
        channel_id: Optional[str] = None

        try:
            auth_test: SlackResponse = await receiver.auth_test()
            self.assertIsNotNone(auth_test["team_id"])
            connect_team_id = auth_test["team_id"]

            # list senders pending connect invites
            connect_invites: SlackResponse = await sender.conversations_listConnectInvites()
            self.assertIsNotNone(connect_invites["invites"])

            # creates channel in sender workspace to share
            unique_channel_name = str(int(time.time())) + "-shared"
            new_channel: SlackResponse = await sender.conversations_create(name=unique_channel_name)
            self.assertIsNotNone(new_channel["channel"])
            self.assertIsNotNone(new_channel["channel"]["id"])
            channel_id = new_channel["channel"]["id"]

            # send an invite for sender's intended shared channel to receiver's bot user id
            invite: SlackResponse = await sender.conversations_inviteShared(
                channel=new_channel["channel"]["id"],
                user_ids=os.environ[SLACK_SDK_TEST_CONNECT_INVITE_RECEIVER_BOT_USER_ID],
            )
            self.assertIsNotNone(invite["invite_id"])

            # receiver accept conversations invite via invite id
            accepted: SlackResponse = await receiver.conversations_acceptSharedInvite(
                channel_name=unique_channel_name,
                invite_id=invite["invite_id"],
            )
            self.assertIsNone(accepted["error"])

            # receiver attempt to approve invite already accepted by an admin level token should fail
            with self.assertRaises(SlackApiError):
                await receiver.conversations_approveSharedInvite(invite_id=invite["invite_id"])

            sender_approval = await sender.conversations_approveSharedInvite(
                invite_id=invite["invite_id"], team_id=connect_team_id
            )
            self.assertIsNone(sender_approval["error"])

            downgrade = await sender.conversations_externalInvitePermissions_set(
                channel=channel_id, target_team=connect_team_id, action="downgrade"
            )
            self.assertIsNone(downgrade["error"])

            upgrade = await sender.conversations_externalInvitePermissions_set(
                channel=channel_id, target_team=connect_team_id, action="upgrade"
            )
            self.assertIsNone(upgrade["error"])
        finally:
            if channel_id is not None:
                # clean up created channel
                delete_channel: SlackResponse = await sender.conversations_archive(channel=new_channel["channel"]["id"])
                self.assertIsNotNone(delete_channel)
