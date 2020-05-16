# ------------------
# Only for running this script here
import asyncio
import logging
import sys
from os.path import dirname

sys.path.insert(1, f"{dirname(__file__)}/../../..")
logging.basicConfig(level=logging.DEBUG)
# ------------------

# ---------------------
# Flask App
# ---------------------

# pip3 install flask
from flask import Flask, make_response

app = Flask(__name__)
logger = logging.getLogger(__name__)

import os

from slack import WebClient
from slack.errors import SlackApiError

singleton_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"], run_async=False)

singleton_loop = asyncio.new_event_loop()
singleton_async_client = WebClient(
    token=os.environ["SLACK_BOT_TOKEN"],
    run_async=True,
    loop=singleton_loop
)


# Fixed in 2.6.0: This doesn't work
@app.route("/sync/singleton", methods=["GET"])
def singleton():
    try:
        # blocking here!!!
        # as described at https://github.com/slackapi/python-slackclient/issues/497
        # until this completion, other simultaneous requests get "RuntimeError: This event loop is already running"
        response = singleton_client.chat_postMessage(
            channel="#random",
            text="You used the singleton WebClient for posting this message!"
        )
        return str(response)
    except SlackApiError as e:
        return make_response(str(e), 400)


@app.route("/sync/per-request", methods=["GET"])
def per_request():
    try:
        client = WebClient(
            token=os.environ["SLACK_BOT_TOKEN"],
            run_async=False
        )
        response = client.chat_postMessage(
            channel="#random",
            text="You used a new WebClient for posting this message!"
        )
        return str(response)
    except SlackApiError as e:
        return make_response(str(e), 400)


# This doesn't work
@app.route("/async/singleton", methods=["GET"])
def singleton_async():
    try:
        future = singleton_async_client.chat_postMessage(
            channel="#random",
            text="You used the singleton WebClient for posting this message!"
        )
        # blocking here!!!
        # as described at https://github.com/slackapi/python-slackclient/issues/497
        # until this completion, other simultaneous requests get "RuntimeError: This event loop is already running"
        response = singleton_loop.run_until_complete(future)
        return str(response)
    except SlackApiError as e:
        return make_response(str(e), 400)


@app.route("/async/per-request", methods=["GET"])
def per_request_async():
    try:
        # This is not optimal and the host should have a large number of FD (File Descriptor)
        loop_for_this_request = asyncio.new_event_loop()

        async_client = WebClient(
            token=os.environ["SLACK_BOT_TOKEN"],
            run_async=True,
            loop=loop_for_this_request
        )
        future = async_client.chat_postMessage(
            channel="#random",
            text="You used the singleton WebClient for posting this message!"
        )
        response = loop_for_this_request.run_until_complete(future)
        return str(response)
    except SlackApiError as e:
        return make_response(str(e), 400)


if __name__ == "__main__":
    # export FLASK_ENV=development
    # python3 integration_tests/samples/issues/issue_497.py
    app.run(debug=True, host="localhost", port=3000)
