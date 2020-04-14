import sys
import logging

sys.path.insert(1, f"{__file__}/../../..")
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# export SLACK_API_TOKEN=xoxb-***
# python3 tests/samples/readme/async_script.py

import asyncio
import os
from slack import WebClient
from slack.errors import SlackApiError

client = WebClient(
    token=os.environ['SLACK_API_TOKEN'],
    run_async=True
)
future = client.chat_postMessage(
    channel='#random',
    text="Hello world!"
)

loop = asyncio.get_event_loop()
try:
    # run_until_complete returns the Future's result, or raise its exception.
    response = loop.run_until_complete(future)
    assert response["message"]["text"] == "Hello world!"
except SlackApiError as e:
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")
finally:
    loop.close()