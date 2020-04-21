# ------------------
# Only for running this script here
import logging
import sys
from os.path import dirname

sys.path.insert(1, f"{dirname(__file__)}/../../..")
logging.basicConfig(level=logging.DEBUG)
# ------------------

# export SLACK_API_TOKEN=xoxb-***
# pip3 install sanic
# python3 integration_tests/samples/readme/async_function_in_framework.py

import os
from slack import WebClient
from slack.errors import SlackApiError

client = WebClient(
    token=os.environ['SLACK_API_TOKEN'],
    run_async=True  # turn async mode on
)


# Define this as an async function
async def send_to_slack(channel, text):
    try:
        # Don't forget to have await as the client returns asyncio.Future
        response = await client.chat_postMessage(
            channel=channel,
            text=text
        )
        assert response["message"]["text"] == text
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        raise e


# https://sanicframework.org/
from sanic import Sanic
from sanic.response import json

app = Sanic()


# e.g., http://localhost:3000/?text=foo&text=bar
@app.route('/')
async def test(request):
    text = 'Hello World!'
    if 'text' in request.args:
        text = "\t".join(request.args['text'])
    try:
        await send_to_slack(channel="#random", text=text)
        return json({'message': 'Done!'})
    except SlackApiError as e:
        return json({'message': f"Failed due to {e.response['error']}"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
