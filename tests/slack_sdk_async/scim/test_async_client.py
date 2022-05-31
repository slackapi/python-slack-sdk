import time
import unittest

from slack_sdk.scim import User, Group
from slack_sdk.scim.v1.async_client import AsyncSCIMClient
from slack_sdk.scim.v1.group import GroupMember
from slack_sdk.scim.v1.user import UserName, UserEmail
from tests.helpers import async_test
from tests.slack_sdk.scim.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestSCIMClient(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    @async_test
    async def test_users(self):
        client = AsyncSCIMClient(base_url="http://localhost:8888/", token="xoxp-valid")
        await client.search_users(start_index=0, count=1)
        await client.read_user("U111")

        now = str(time.time())[:10]
        user = User(
            user_name=f"user_{now}",
            name=UserName(given_name="Kaz", family_name="Sera"),
            emails=[UserEmail(value=f"seratch+{now}@example.com")],
            schemas=["urn:scim:schemas:core:1.0"],
        )
        await client.create_user(user)
        # The mock server does not work for PATH requests
        try:
            await client.patch_user("U111", partial_user=User(user_name="foo"))
        except:
            pass
        user.id = "U111"
        user.user_name = "updated"
        try:
            await client.update_user(user)
        except:
            pass
        try:
            await client.delete_user("U111")
        except:
            pass

    @async_test
    async def test_groups(self):
        client = AsyncSCIMClient(base_url="http://localhost:8888/", token="xoxp-valid")
        await client.search_groups(start_index=0, count=1)
        await client.read_group("S111")

        now = str(time.time())[:10]
        group = Group(
            display_name=f"TestGroup_{now}",
            members=[GroupMember(value="U111")],
        )
        await client.create_group(group)
        # The mock server does not work for PATH requests
        try:
            await client.patch_group("S111", partial_group=Group(display_name=f"TestGroup_{now}_2"))
        except:
            pass
        group.id = "S111"
        group.display_name = "updated"
        try:
            await client.update_group(group)
        except:
            pass
        try:
            await client.delete_group("S111")
        except:
            pass
