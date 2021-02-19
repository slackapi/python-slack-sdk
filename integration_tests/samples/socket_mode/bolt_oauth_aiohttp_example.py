import logging

logging.basicConfig(level=logging.DEBUG)

import os

from slack_bolt.app import App
from slack_bolt.context import BoltContext
from slack_bolt.oauth.oauth_settings import OAuthSettings

app = App(
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    oauth_settings=OAuthSettings(
        client_id=os.environ["SLACK_CLIENT_ID"],
        client_secret=os.environ["SLACK_CLIENT_SECRET"],
        scopes=os.environ["SLACK_SCOPES"].split(","),
    ),
)


@app.event("app_mention")
def mention(context: BoltContext):
    context.say(":wave: Hi there!")


@app.event("message")
def message(context: BoltContext, event: dict):
    context.client.reactions_add(
        channel=event["channel"],
        timestamp=event["ts"],
        name="eyes",
    )


@app.command("/hello-socket-mode")
def hello_command(ack, body):
    user_id = body["user_id"]
    ack(f"Hi <@{user_id}>!")


if __name__ == "__main__":

    def run_socket_mode_app():
        import asyncio
        from bolt_adapter.aiohttp import AsyncSocketModeHandler

        async def socket_mode_app():
            app_token = os.environ.get("SLACK_APP_TOKEN")
            await AsyncSocketModeHandler(app, app_token).connect_async()
            await asyncio.sleep(float("inf"))

        asyncio.run(socket_mode_app())

    from concurrent.futures.thread import ThreadPoolExecutor

    socket_mode_thread = ThreadPoolExecutor(1)
    socket_mode_thread.submit(run_socket_mode_app)

    app.start()

    # export SLACK_APP_TOKEN=
    # export SLACK_SIGNING_SECRET=
    # export SLACK_CLIENT_ID=
    # export SLACK_CLIENT_SECRET=
    # export SLACK_SCOPES=
    # pip install .[optional]
    # pip install slack_bolt
    # python integration_tests/samples/socket_mode/{this file name}.py
