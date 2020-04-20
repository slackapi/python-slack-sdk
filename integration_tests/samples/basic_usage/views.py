# ------------------
# Only for running this script here
import json
from os.path import dirname
import sys
import logging

sys.path.insert(1, f"{dirname(__file__)}/../../..")
logging.basicConfig(level=logging.DEBUG)
# ------------------

# ---------------------
# Slack Request Verification
# https://github.com/slackapi/python-slack-events-api
# ---------------------

import hmac
import hashlib
from time import time


def verify_request(
    signing_secret: str,
    request_body: str,
    timestamp: str,
    signature: str) -> bool:
    if abs(time() - int(timestamp)) > 60 * 5:
        return False

    if hasattr(hmac, "compare_digest"):
        req = str.encode('v0:' + str(timestamp) + ':') + request_body
        request_hash = 'v0=' + hmac.new(
            str.encode(signing_secret),
            req, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(request_hash, signature)
    else:
        # So, we'll compare the signatures explicitly
        req = str.encode('v0:' + str(timestamp) + ':') + request_body
        request_hash = 'v0=' + hmac.new(
            str.encode(signing_secret),
            req, hashlib.sha256
        ).hexdigest()

        if len(request_hash) != len(signature):
            return False
        result = 0
        if isinstance(request_hash, bytes) and isinstance(signature, bytes):
            for x, y in zip(request_hash, signature):
                result |= x ^ y
        else:
            for x, y in zip(request_hash, signature):
                result |= ord(x) ^ ord(y)
        return result == 0


# ---------------------
# Slack WebClient
# ---------------------

import os

from slack import WebClient
from slack.errors import SlackApiError

client = WebClient(token=os.environ["SLACK_API_TOKEN"])

# ---------------------
# Flask App
# ---------------------

# pip3 install flask
from flask import Flask, request, make_response

app = Flask(__name__)
signing_secret = os.environ["SLACK_SIGNING_SECRET"]


@app.route("/slack/events", methods=["POST"])
def slack_app():
    if not verify_request(
        signing_secret=signing_secret,
        request_body=request.get_data(),
        timestamp=request.headers.get("X-Slack-Request-Timestamp"),
        signature=request.headers.get("X-Slack-Signature")):
        return make_response("invalid request", 403)

    if "command" in request.form \
        and request.form["command"] == "/open-modal":
        trigger_id = request.form["trigger_id"]
        try:
            response = client.views_open(
                trigger_id=trigger_id,
                view={
                    "type": "modal",
                    "callback_id": "modal-id",
                    "title": {
                        "type": "plain_text",
                        "text": "Awesome Modal"
                    },
                    "submit": {
                        "type": "plain_text",
                        "text": "Submit"
                    },
                    "close": {
                        "type": "plain_text",
                        "text": "Cancel"
                    },
                    "blocks": [
                        {
                            "type": "input",
                            "block_id": "b-id",
                            "label": {
                                "type": "plain_text",
                                "text": "Input label",
                            },
                            "element": {
                                "action_id": "a-id",
                                "type": "plain_text_input",
                            }
                        }
                    ]
                }
            )
            return make_response("", 200)
        except SlackApiError as e:
            code = e.response["error"]
            return make_response(f"Failed to open a modal due to {code}", 200)

    elif "payload" in request.form:
        payload = json.loads(request.form["payload"])
        if payload["type"] == "view_submission" \
            and payload["view"]["callback_id"] == "modal-id":
            submitted_data = payload["view"]["state"]["values"]
            print(submitted_data)  # {'b-id': {'a-id': {'type': 'plain_text_input', 'value': 'your input'}}}
            return make_response("", 200)

    return make_response("", 404)


if __name__ == "__main__":
    # export SLACK_SIGNING_SECRET=***
    # export SLACK_API_TOKEN=xoxb-***
    # export FLASK_ENV=development
    # python3 integration_tests/samples/basic_usage/views.py
    app.run("localhost", 3000)

# ngrok http 3000
