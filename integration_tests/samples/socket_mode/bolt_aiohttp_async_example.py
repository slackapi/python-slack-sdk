import logging

logging.basicConfig(level=logging.DEBUG)

import os
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.context.async_context import AsyncBoltContext

bot_token = os.environ.get("SLACK_SDK_TEST_SOCKET_MODE_BOT_TOKEN")
app = AsyncApp(signing_secret="will-be-removed-soon", token=bot_token)


@app.event("app_mention")
async def mention(context: AsyncBoltContext):
    await context.say(":wave: Hi there!")


@app.event("message")
async def message(context: AsyncBoltContext, event: dict):
    await context.client.reactions_add(
        channel=event["channel"],
        timestamp=event["ts"],
        name="eyes",
    )


@app.command("/hello-socket-mode")
async def hello_command(ack, body):
    user_id = body["user_id"]
    await ack(f"Hi <@{user_id}>!")


async def main():
    from bolt_adapter.aiohttp import AsyncSocketModeHandler

    app_token = os.environ.get("SLACK_SDK_TEST_SOCKET_MODE_APP_TOKEN")
    await AsyncSocketModeHandler(app, app_token).start_async()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

    # export SLACK_SDK_TEST_SOCKET_MODE_APP_TOKEN=
    # export SLACK_SDK_TEST_SOCKET_MODE_BOT_TOKEN=
    # pip install .[optional]
    # pip install slack_bolt
    # python integration_tests/samples/socket_mode/{this file name}.py
