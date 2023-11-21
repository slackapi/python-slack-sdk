import logging

logging.basicConfig(level=logging.DEBUG)

import os

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.context.async_context import AsyncBoltContext
from slack_bolt.oauth.async_oauth_settings import AsyncOAuthSettings

app = AsyncApp(
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    oauth_settings=AsyncOAuthSettings(
        client_id=os.environ["SLACK_CLIENT_ID"],
        client_secret=os.environ["SLACK_CLIENT_SECRET"],
        scopes=os.environ["SLACK_SCOPES"].split(","),
    ),
)


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


if __name__ == "__main__":
    import asyncio
    from asyncio import Future

    async def socket_mode_runner():
        from bolt_adapter.aiohttp import AsyncSocketModeHandler

        app_token = os.environ.get("SLACK_APP_TOKEN")
        await AsyncSocketModeHandler(app, app_token).connect_async()
        await asyncio.sleep(float("inf"))

    _: Future = asyncio.ensure_future(socket_mode_runner())
    app.start()

    # export SLACK_APP_TOKEN=
    # export SLACK_SIGNING_SECRET=
    # export SLACK_CLIENT_ID=
    # export SLACK_CLIENT_SECRET=
    # export SLACK_SCOPES=
    # pip install .[optional]
    # pip install slack_bolt
    # python integration_tests/samples/socket_mode/{this file name}.py
