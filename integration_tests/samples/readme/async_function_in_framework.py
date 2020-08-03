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
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

client = AsyncWebClient(token=os.environ["SLACK_API_TOKEN"])


# Define this as an async function
async def send_to_slack(channel, text):
    try:
        # Don't forget to have await as the client returns asyncio.Future
        response = await client.chat_postMessage(channel=channel, text=text)
        assert response["message"]["text"] == text
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        raise e


from aiohttp import web


async def handle_requests(request: web.Request) -> web.Response:
    text = "Hello World!"
    if "text" in request.query:
        text = "\t".join(request.query.getall("text"))
    try:
        await send_to_slack(channel="#random", text=text)
        return web.json_response(data={"message": "Done!"})
    except SlackApiError as e:
        return web.json_response(
            data={"message": f"Failed due to {e.response['error']}"}
        )


if __name__ == "__main__":
    app = web.Application()
    app.add_routes([web.get("/", handle_requests)])
    # e.g., http://localhost:3000/?text=foo&text=bar
    web.run_app(app, host="0.0.0.0", port=3000)
