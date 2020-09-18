# ------------------
# Only for running this script here
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
from slack_sdk.web import WebClient
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.installation_store import FileInstallationStore, Installation
from slack_sdk.oauth.state_store import FileOAuthStateStore

client_id = os.environ["SLACK_TEST_CLIENT_ID"]
client_secret = os.environ["SLACK_TEST_CLIENT_SECRET"]
redirect_uri = os.environ["SLACK_TEST_REDIRECT_URI"]
scopes = ["app_mentions:read","chat:write"]
user_scopes = ["search:read"]

logger = logging.getLogger(__name__)


state_store = FileOAuthStateStore(expiration_seconds=300)
installation_store = FileInstallationStore()
authorization_url_generator = AuthorizeUrlGenerator(
    client_id=client_id,
    scopes=scopes,
    user_scopes=user_scopes,
)

@app.route("/slack/oauth/start", methods=["GET"])
def oauth_start():
    state = state_store.issue()
    url = authorization_url_generator.generate(state)
    return f'<a href="{url}">' \
           f'<img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>'


@app.route("/slack/oauth/callback", methods=["GET"])
def oauth_callback():
    # Retrieve the auth code and state from the request params
    if "code" in request.args:
        state = request.args["state"]
        if state_store.consume(state):
            code = request.args["code"]
            client = WebClient()  # no prepared token needed for this app
            oauth_response = client.oauth_v2_access(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                code=code
            )
            logger.info(f"oauth.v2.access response: {oauth_response}")

            installed_enterprise = oauth_response.get("enterprise") or {}
            installed_team = oauth_response.get("team") or {}
            installer = oauth_response.get("authed_user") or {}
            incoming_webhook = oauth_response.get("incoming_webhook") or {}
            bot_token = oauth_response.get("access_token")
            # NOTE: oauth.v2.access doesn't include bot_id in response
            bot_id = None
            if bot_token is not None:
                auth_test = client.auth_test(token=bot_token)
                bot_id = auth_test["bot_id"]

            installation = Installation(
                app_id=oauth_response.get("app_id"),
                enterprise_id=installed_enterprise.get("id"),
                team_id=installed_team.get("id"),
                bot_token=bot_token,
                bot_id=bot_id,
                bot_user_id=oauth_response.get("bot_user_id"),
                bot_scopes=oauth_response.get("scope"),  # comma-separated string
                user_id=installer.get("id"),
                user_token=installer.get("access_token"),
                user_scopes=installer.get("scope"),  # comma-separated string
                incoming_webhook_url=incoming_webhook.get("url"),
                incoming_webhook_channel_id=incoming_webhook.get("channel_id"),
                incoming_webhook_configuration_url=incoming_webhook.get("configuration_url"),
            )
            installation_store.save(installation)
            return "Thanks for installing this app!"
        else:
            return make_response(f"Try the installation again (the state value is already expired)", 400)

    error = request.args["error"] if "error" in request.args else ""
    return make_response(f"Something is wrong with the installation (error: {error})", 400)


# ---------------------
# Flask App for Slack events
# ---------------------

import json
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

signing_secret = os.environ["SLACK_SIGNING_SECRET"]
signature_verifier = SignatureVerifier(signing_secret=signing_secret)

@app.route("/slack/events", methods=["POST"])
def slack_app():
    if not signature_verifier.is_valid(
        body=request.get_data(),
        timestamp=request.headers.get("X-Slack-Request-Timestamp"),
        signature=request.headers.get("X-Slack-Signature")):
        return make_response("invalid request", 403)

    if "command" in request.form \
        and request.form["command"] == "/open-modal":
        try:
            enterprise_id = request.form.get("enterprise_id")
            team_id = request.form["team_id"]
            bot = installation_store.find_bot(
                enterprise_id=enterprise_id,
                team_id=team_id,
            )
            bot_token = bot.bot_token if bot else None
            if not bot_token:
                return make_response("Please install this app first!", 200)

            client = WebClient(token=bot_token)
            trigger_id = request.form["trigger_id"]
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
