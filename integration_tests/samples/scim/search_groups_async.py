import logging

logging.basicConfig(level=logging.DEBUG)

import asyncio
import os
from slack_sdk.scim.async_client import AsyncSCIMClient

client = AsyncSCIMClient(token=os.environ["SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN"])


async def main():
    response = await client.search_groups(start_index=1, count=2)
    print("-----------------------")
    print(response.groups)


asyncio.run(main())
