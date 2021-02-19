import asyncio
import logging
import os

from slack_sdk.socket_mode.aiohttp import SocketModeClient

logging.basicConfig(level=logging.DEBUG)


async def main():
    client = SocketModeClient(app_token=os.environ["SLACK_APP_TOKEN"])
    await client.connect()
    await asyncio.sleep(3)
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())

# The issue:
# ERROR:asyncio:Unclosed client session
# client_session: <aiohttp.client.ClientSession object at 0x10e1085e0>
# INFO:slack_sdk.socket_mode.aiohttp:The session has been abandoned
