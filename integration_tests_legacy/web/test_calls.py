import logging
import os
import unittest
import uuid

from integration_tests.env_variable_names import SLACK_SDK_TEST_BOT_TOKEN
from integration_tests.helpers import async_test
from slack import WebClient
from slack.web.classes.blocks import CallBlock

class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API"""

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        self.sync_client: WebClient = WebClient(token=self.bot_token)
        self.async_client: WebClient = WebClient(token=self.bot_token, run_async=True)

    def tearDown(self):
        pass

    def test_sync(self):
        client = self.sync_client
        user_id = list(filter(
            lambda u: not u["deleted"] and "bot_id" not in u,
            client.users_list(limit=50)["members"]
        ))[0]["id"]

        new_call = client.calls_add(
            external_unique_id=str(uuid.uuid4()),
            join_url="https://www.example.com/calls/12345",
            users=[
                {
                    "slack_id": user_id
                },
                {
                    "external_id": "anon-111",
                    "avatar_url": "https://assets.brandfolder.com/pmix53-32t4so-a6439g/original/slackbot.png",
                    "display_name": "anonymous user 1",
                }
            ]
        )
        self.assertIsNotNone(new_call)
        call_id = new_call["call"]["id"]

        channel_message = client.chat_postMessage(channel="#random", blocks=[
            {
                "type": "call",
                "call_id": call_id,
            }
        ])
        self.assertIsNotNone(channel_message)

        channel_message = client.chat_postMessage(channel="#random", blocks=[
            CallBlock(call_id=call_id)
        ])
        self.assertIsNotNone(channel_message)

        call_info = client.calls_info(id = call_id)
        self.assertIsNotNone(call_info)

        new_participants = client.calls_participants_add(id=call_id, users=[
            {
                "external_id": "anon-222",
                "avatar_url": "https://assets.brandfolder.com/pmix53-32t4so-a6439g/original/slackbot.png",
                "display_name": "anonymous user 2",
            }
        ])
        self.assertIsNotNone(new_participants)

        participants_removal = client.calls_participants_remove(id=call_id, users=[
            {
                "external_id": "anon-222",
                "avatar_url": "https://assets.brandfolder.com/pmix53-32t4so-a6439g/original/slackbot.png",
                "display_name": "anonymous user 2",
            }
        ])
        self.assertIsNotNone(participants_removal)

        modified_call = client.calls_update(id=call_id, join_url="https://www.example.com/calls/99999")
        self.assertIsNotNone(modified_call)

        ended_call = client.calls_end(id=call_id)
        self.assertIsNotNone(ended_call)

    @async_test
    async def test_async(self):
        client = self.async_client
        users = await client.users_list(limit=50)
        user_id = list(filter(
            lambda u: not u["deleted"] and "bot_id" not in u,
            users["members"]
        ))[0]["id"]

        new_call = await client.calls_add(
            external_unique_id=str(uuid.uuid4()),
            join_url="https://www.example.com/calls/12345",
            users=[
                {
                    "slack_id": user_id
                },
                {
                    "external_id": "anon-111",
                    "avatar_url": "https://assets.brandfolder.com/pmix53-32t4so-a6439g/original/slackbot.png",
                    "display_name": "anonymous user 1",
                }
            ]
        )
        self.assertIsNotNone(new_call)
        call_id = new_call["call"]["id"]

        channel_message = await client.chat_postMessage(channel="#random", blocks=[
            {
                "type": "call",
                "call_id": call_id,
            }
        ])
        self.assertIsNotNone(channel_message)

        call_info = await client.calls_info(id = call_id)
        self.assertIsNotNone(call_info)

        new_participants = await client.calls_participants_add(id=call_id, users=[
            {
                "external_id": "anon-222",
                "avatar_url": "https://assets.brandfolder.com/pmix53-32t4so-a6439g/original/slackbot.png",
                "display_name": "anonymous user 2",
            }
        ])
        self.assertIsNotNone(new_participants)

        modified_call = await client.calls_update(id=call_id, join_url="https://www.example.com/calls/99999")
        self.assertIsNotNone(modified_call)

        ended_call = await client.calls_end(id=call_id)
        self.assertIsNotNone(ended_call)
