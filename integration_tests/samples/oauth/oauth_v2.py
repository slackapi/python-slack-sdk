# ------------------
# Only for running this script here
import json
import logging
import sys
from os.path import dirname

sys.path.insert(1, f"{dirname(__file__)}/../../..")
logging.basicConfig(level=logging.DEBUG)
# ------------------

# ---------------------
# Flask App for Slack OAuth flow
# ---------------------

# pip3 install flask
from flask import Flask, request, make_response

app = Flask(__name__)
app.debug = True

import os
from uuid import uuid4
from slack import WebClient

client_id = os.environ["SLACK_TEST_CLIENT_ID"]
client_secret = os.environ["SLACK_TEST_CLIENT_SECRET"]
redirect_uri = os.environ["SLACK_TEST_REDIRECT_URI"]
scopes = "app_mentions:read,chat:write"
user_scopes = "search:read"

logger = logging.getLogger(__name__)


class StateService:
    def __init__(self):
        # no expiration implemented
        self.state_values = []

    def generate(self):
        new_value = str(uuid4())
        self.state_values.append(new_value)
        return new_value

    def consume(self, state) -> bool:
        is_valid = state in self.state_values
        if is_valid:
            self.state_values.remove(state)
        return is_valid


class Database:
    def __init__(self):
        self.tokens = {}

    def save(self, oauth_v2_response):
        team_id = oauth_v2_response["team"]["id"]
        installer = oauth_v2_response["authed_user"]
        self.tokens[team_id] = {
            "bot_token": oauth_v2_response["access_token"],
            "bot_user_id": oauth_v2_response["bot_user_id"],
            "user_id": installer["id"],
            "user_token": installer["access_token"] if "access_token" in installer else None,
        }
        logger.debug(f"all rows: {list(self.tokens.keys())}")

    def find_bot_token(self, team_id: str) -> str:
        logger.debug(f"all rows: {list(self.tokens.keys())}, team_id: {team_id}")
        installation = self.tokens[team_id] if team_id in self.tokens else None
        if installation:
            return installation["bot_token"]
        else:
            return None


state_service = StateService()
database = Database()


@app.route("/slack/oauth/start", methods=["GET"])
def oauth_start():
    state = state_service.generate()
    return f'<a href="https://slack.com/oauth/v2/authorize?' \
           f'scope={scopes}&' \
           f'user_scope={user_scopes}&' \
           f'client_id={client_id}&' \
           f'redirect_uri={redirect_uri}&' \
           f'state={state}' \
           f'">' \
           f'<img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>'


@app.route("/slack/oauth/callback", methods=["GET"])
def oauth_callback():
    # Retrieve the auth code and state from the request params
    if "code" in request.args:
        state = request.args["state"]
        if state_service.consume(state):
            code = request.args["code"]
            client = WebClient()  # no prepared token needed for this app
            response = client.oauth_v2_access(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                code=code
            )
            logger.info(f"oauth.v2.access response: {response}")
            database.save(response)
            return "Thanks for installing this app!"
        else:
            return make_response(f"Try the installation again (the state value is already expired)", 400)

    error = request.args["error"] if "error" in request.args else ""
    return make_response(f"Something is wrong with the installation (error: {error})", 400)


# ---------------------
# Flask App for Slack events
# ---------------------

import hmac
import hashlib
from time import time


def verify_slack_request(
    signing_secret: str,
    request_body: str,
    timestamp: str,
    signature: str) -> bool:
    """Slack Request Verification

    For more information: https://github.com/slackapi/python-slack-events-api
    """

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


from slack.errors import SlackApiError

signing_secret = os.environ["SLACK_SIGNING_SECRET"]


@app.route("/slack/events", methods=["POST"])
def slack_app():
    if not verify_slack_request(
        signing_secret=signing_secret,
        request_body=request.get_data(),
        timestamp=request.headers.get("X-Slack-Request-Timestamp"),
        signature=request.headers.get("X-Slack-Signature")):
        return make_response("invalid request", 403)

    if "command" in request.form \
        and request.form["command"] == "/do-something":
        trigger_id = request.form["trigger_id"]
        try:
            team_id = request.form["team_id"]
            bot_token = database.find_bot_token(team_id)
            logger.debug(f"token: {bot_token}")
            if not bot_token:
                return make_response("Please install this app first!", 200)

            client = WebClient(token=bot_token)
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
    # export SLACK_TEST_CLIENT_ID=123.123
    # export SLACK_TEST_CLIENT_SECRET=xxx
    # export SLACK_TEST_REDIRECT_URI=https://{yours}.ngrok.io/slack/oauth/callback
    # export SLACK_SIGNING_SECRET=***
    # export FLASK_ENV=development

    app.run("localhost", 3000)

    # python3 integration_tests/samples/oauth/oauth_v2.py
    # ngrok http 3000
    # https://{yours}.ngrok.io/slack/oauth/start
