import json
import logging

logging.basicConfig(level=logging.DEBUG)

# ---------------------
# Slack WebClient
# ---------------------

import os

from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
signature_verifier = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"])

# ---------------------
# Flask App
# ---------------------

# pip3 install flask
from flask import Flask, request, make_response, jsonify

app = Flask(__name__)


@app.route("/slack/events", methods=["POST"])
def slack_app():
    if not signature_verifier.is_valid_request(request.get_data(), request.headers):
        return make_response("invalid request", 403)

    if "payload" in request.form:
        payload = json.loads(request.form["payload"])

        if payload["type"] == "shortcut" and payload["callback_id"] == "test-shortcut":
            # Open a new modal by a global shortcut
            try:
                api_response = client.views_open(
                    trigger_id=payload["trigger_id"],
                    view={
                        "type": "modal",
                        "callback_id": "modal-id",
                        "title": {"type": "plain_text", "text": "Awesome Modal"},
                        "submit": {"type": "plain_text", "text": "Submit"},
                        "close": {"type": "plain_text", "text": "Cancel"},
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
                                },
                            }
                        ],
                    },
                )
                return make_response("", 200)
            except SlackApiError as e:
                code = e.response["error"]
                return make_response(f"Failed to open a modal due to {code}", 200)

        if payload["type"] == "view_submission" and payload["view"]["callback_id"] == "modal-id":
            # Handle a data submission request from the modal
            submitted_data = payload["view"]["state"]["values"]
            print(submitted_data)  # {'b-id': {'a-id': {'type': 'plain_text_input', 'value': 'your input'}}}
            return make_response(
                jsonify(
                    {
                        "response_action": "update",
                        "view": {
                            "type": "modal",
                            "title": {"type": "plain_text", "text": "Accepted"},
                            "close": {"type": "plain_text", "text": "Close"},
                            "blocks": [
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Thanks for submitting the data!",
                                    },
                                }
                            ],
                        },
                    }
                ),
                200,
            )

    return make_response("", 404)


if __name__ == "__main__":
    # export SLACK_SIGNING_SECRET=***
    # export SLACK_API_TOKEN=xoxb-***
    # export FLASK_ENV=development
    # python3 integration_tests/samples/basic_usage/views.py
    app.run("localhost", 3000)

# ngrok http 3000
