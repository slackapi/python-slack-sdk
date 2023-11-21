import logging

logging.basicConfig(level=logging.DEBUG)

import asyncio
import os
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.aiohttp import SocketModeClient


async def main():
    client = SocketModeClient(
        app_token=os.environ.get("SLACK_SDK_TEST_SOCKET_MODE_APP_TOKEN"),
        web_client=AsyncWebClient(token=os.environ.get("SLACK_SDK_TEST_SOCKET_MODE_BOT_TOKEN")),
        trace_enabled=True,
    )

    async def process(client: SocketModeClient, req: SocketModeRequest):
        if req.type == "events_api":
            response = SocketModeResponse(envelope_id=req.envelope_id)
            await client.send_socket_mode_response(response)
            if req.payload["event"]["type"] == "message":
                await client.web_client.reactions_add(
                    name="eyes",
                    channel=req.payload["event"]["channel"],
                    timestamp=req.payload["event"]["ts"],
                )

    client.socket_mode_request_listeners.append(process)
    await client.connect()
    await asyncio.sleep(float("inf"))


asyncio.run(main())
