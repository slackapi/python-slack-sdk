import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(filename)s (%(lineno)s): %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

import os
from slack_sdk.rtm.v2 import RTMClient
from integration_tests.env_variable_names import SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN

if __name__ == "__main__":
    rtm = RTMClient(
        token=os.environ.get(SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN),
        trace_enabled=True,
        all_message_trace_enabled=True,
    )

    @rtm.on("message")
    def handle(client: RTMClient, event: dict):
        client.web_client.reactions_add(
            channel=event["channel"],
            timestamp=event["ts"],
            name="eyes",
        )

    @rtm.on("*")
    def handle(client: RTMClient, event: dict):
        logger.info(event)

    rtm.start()
