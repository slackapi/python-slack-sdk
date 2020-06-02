# ------------------
# Only for running this script here
import logging
import sys
from os.path import dirname

sys.path.insert(1, f"{dirname(__file__)}/../../..")
logging.basicConfig(level=logging.DEBUG)
# ------------------

# export SLACK_API_TOKEN=xoxb-***
# python3 integration_tests/samples/issues/issue_506.py

import os
from slack import RTMClient

logger = logging.getLogger(__name__)
global_state = {}


@RTMClient.run_on(event="open")
def open(**payload):
    web_client = payload["web_client"]
    auth_result = web_client.auth_test()
    global_state.update({"bot_id": auth_result["bot_id"]})
    logger.info(f"cached: {global_state}")


@RTMClient.run_on(event="message")
def message(**payload):
    data = payload["data"]
    if data.get("bot_id", None) == global_state["bot_id"]:
        logger.debug("Skipped as it's me")
        return
    # do something here
    web_client = payload["web_client"]
    message = web_client.chat_postMessage(channel=data["channel"], text="What's up?")
    logger.info(f"message: {message['ts']}")


rtm_client = RTMClient(token=os.environ["SLACK_API_TOKEN"])
rtm_client.start()
