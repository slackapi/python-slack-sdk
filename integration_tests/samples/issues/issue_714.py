import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

import os
from slack_sdk.web import WebClient

# export HTTPS_PROXY=http://localhost:9000
client = WebClient(token=os.environ["SLACK_API_TOKEN"])
response = client.auth_test()
logger.info(f"HTTPS_PROXY response: {response}")

client = WebClient(token=os.environ["SLACK_API_TOKEN"], proxy="http://localhost:9000")
response = client.auth_test()
logger.info(f"sync response: {response}")

client = WebClient(token=os.environ["SLACK_API_TOKEN"], proxy="localhost:9000")
response = client.auth_test()
logger.info(f"sync response: {response}")


async def async_call():
    client = WebClient(
        token=os.environ["SLACK_API_TOKEN"],
        proxy="http://localhost:9000",
        run_async=True,
    )
    response = await client.auth_test()
    logger.info(f"async response: {response}")


asyncio.run(async_call())

# Terminal A:
# pip3 install proxy.py
# proxy --port 9000 --log-level d

# Terminal B:
# export SLACK_API_TOKEN=xoxb-***
# python3 integration_tests/samples/issues/issue_714.py
