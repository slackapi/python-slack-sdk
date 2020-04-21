# ------------------
# Only for running this script here
import logging
import sys
from os.path import dirname

sys.path.insert(1, f"{dirname(__file__)}/../../..")
logging.basicConfig(level=logging.DEBUG)
# ------------------

# export SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN=xoxb-***
# python3 integration_tests/samples/issues/issue_522.py

import asyncio
import logging
import os

import slack

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

token = os.environ['SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN']


async def sleepy_count(name, sleep_for):
    for i in range(10):
        await asyncio.sleep(sleep_for)
        LOGGER.debug(f"{name} - slept {i + 1} times.")


async def slack_client_and_sleeps():
    # real-time-messaging Slack client
    client = slack.RTMClient(token=token, run_async=True)

    sleepy_count_task = asyncio.create_task(sleepy_count("first counter", 1))
    sleepy_count_task2 = asyncio.create_task(sleepy_count("second counter", 3))

    await asyncio.gather(client.start(), sleepy_count_task, sleepy_count_task2)


async def slack_client():
    # real-time-messaging Slack client
    client = slack.RTMClient(token=token, run_async=True)

    await asyncio.gather(client.start())


async def sleeps():
    sleepy_count_task = asyncio.create_task(sleepy_count("first counter", 1))
    sleepy_count_task2 = asyncio.create_task(sleepy_count("second counter", 3))

    await asyncio.gather(sleepy_count_task, sleepy_count_task2)


if __name__ == "__main__":
    LOGGER.info(f"Try: kill -2 {os.getpid()} or ctrl+c")
    if len(sys.argv) > 1:
        option = sys.argv[1]
        if option == "1":
            # sigint closes program correctly
            asyncio.run(slack_client())
        elif option == "2":
            # sigint closes program correctly
            asyncio.run(sleeps())
        elif option == "3":
            # sigint doesn't actually close properly
            asyncio.run(slack_client_and_sleeps())
    else:
        # sigint doesn't actually close properly
        asyncio.run(slack_client_and_sleeps())
