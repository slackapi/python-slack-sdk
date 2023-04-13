# ---------------------
# Flask App for Slack OAuth flow
# ---------------------

# pip3 install flask
from typing import Optional

from integration_tests.samples.token_rotation.util import (
    parse_body,
    extract_enterprise_id,
    extract_user_id,
    extract_team_id,
    extract_is_enterprise_install,
    extract_content_type,
)

import logging
import os

from slack_sdk.oauth.installation_store.sqlite3 import SQLite3InstallationStore
from slack_sdk.web import WebClient
from slack_sdk.oauth.token_rotation import TokenRotator
from slack_sdk.oauth import AuthorizeUrlGenerator, RedirectUriPageRenderer
from slack_sdk.oauth.installation_store import Installation
from slack_sdk.oauth.state_store.sqlite3 import SQLite3OAuthStateStore

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
scopes = ["app_mentions:read", "chat:write", "commands"]
user_scopes = ["search:read"]

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

import sqlalchemy
from sqlalchemy.engine import Engine

database_url = "sqlite:///slackapp.db"
# database_url = "postgresql://localhost/slackapp"  # pip install psycopg2
engine: Engine = sqlalchemy.create_engine(database_url)

installation_store = SQLite3InstallationStore(
    database="test.db",
    client_id=client_id,
    logger=logger,
)
installation_store.init()

token_rotator = TokenRotator(
    client_id=client_id,
    client_secret=client_secret,
)

state_store = SQLite3OAuthStateStore(
    database="test.db",
    logger=logger,
    expiration_seconds=300,
)
state_store.init()

# ---------------------
# Flask App for Slack events
# ---------------------

import json
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

signing_secret = os.environ["SLACK_SIGNING_SECRET"]
signature_verifier = SignatureVerifier(signing_secret=signing_secret)


def rotate_tokens(
    enterprise_id: Optional[str] = None,
    team_id: Optional[str] = None,
    user_id: Optional[str] = None,
    is_enterprise_install: Optional[bool] = None,
):
    installation = installation_store.find_installation(
        enterprise_id=enterprise_id,
        team_id=team_id,
        user_id=user_id,
        is_enterprise_install=is_enterprise_install,
    )
    if installation is not None:
        updated_installation = token_rotator.perform_token_rotation(
            installation=installation,
            minutes_before_expiration=60 * 24 * 365,  # one year for testing
        )
        if updated_installation is not None:
            installation_store.save(updated_installation)


from flask import Flask, request, make_response

app = Flask(__name__)
app.debug = True


@app.route("/slack/events", methods=["POST"])
def slack_app():
    if not signature_verifier.is_valid(
        body=request.get_data(),
        timestamp=request.headers.get("X-Slack-Request-Timestamp"),
        signature=request.headers.get("X-Slack-Signature"),
    ):
        return make_response("invalid request", 403)

    raw_body = request.data.decode("utf-8")
    body = parse_body(body=raw_body, content_type=extract_content_type(request.headers))
    rotate_tokens(
        enterprise_id=extract_enterprise_id(body),
        team_id=extract_team_id(body),
        user_id=extract_user_id(body),
        is_enterprise_install=extract_is_enterprise_install(body),
    )

    if "command" in request.form and request.form["command"] == "/token-rotation-modal":
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

    elif "payload" in request.form:
        payload = json.loads(request.form["payload"])
        if payload["type"] == "view_submission" and payload["view"]["callback_id"] == "modal-id":
            submitted_data = payload["view"]["state"]["values"]
            print(submitted_data)  # {'b-id': {'a-id': {'type': 'plain_text_input', 'value': 'your input'}}}
            return make_response("", 200)

    else:
        if raw_body.startswith("{"):
            event_payload = json.loads(raw_body)
            logger.info(f"Events API payload: {event_payload}")
            if event_payload.get("type") == "url_verification":
                return make_response(event_payload.get("challenge"), 200)
            return make_response("", 200)

    return make_response("", 404)


# ---------------------
# Flask App for Slack OAuth flow
# ---------------------

authorization_url_generator = AuthorizeUrlGenerator(
    client_id=client_id,
    scopes=scopes,
    user_scopes=user_scopes,
)
redirect_page_renderer = RedirectUriPageRenderer(
    install_path="/slack/install",
    redirect_uri_path="/slack/oauth_redirect",
)


@app.route("/slack/install", methods=["GET"])
def oauth_start():
    state = state_store.issue()
    url = authorization_url_generator.generate(state)
    return (
        '<html><head><link rel="icon" href="data:,"></head><body>'
        f'<a href="{url}">'
        f'<img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>'
        "</body></html>"
    )


@app.route("/slack/oauth_redirect", methods=["GET"])
def oauth_callback():
    # Retrieve the auth code and state from the request params
    if "code" in request.args:
        state = request.args["state"]
        if state_store.consume(state):
            code = request.args["code"]
            client = WebClient()  # no prepared token needed for this app
            oauth_response = client.oauth_v2_access(client_id=client_id, client_secret=client_secret, code=code)
            logger.info(f"oauth.v2.access response: {oauth_response}")

            installed_enterprise = oauth_response.get("enterprise", {})
            is_enterprise_install = oauth_response.get("is_enterprise_install")
            installed_team = oauth_response.get("team", {})
            installer = oauth_response.get("authed_user", {})
            incoming_webhook = oauth_response.get("incoming_webhook", {})

            bot_token = oauth_response.get("access_token")
            # NOTE: oauth.v2.access doesn't include bot_id in response
            bot_id = None
            enterprise_url = None
            if bot_token is not None:
                auth_test = client.auth_test(token=bot_token)
                bot_id = auth_test["bot_id"]
                if is_enterprise_install is True:
                    enterprise_url = auth_test.get("url")

            installation = Installation(
                app_id=oauth_response.get("app_id"),
                enterprise_id=installed_enterprise.get("id"),
                enterprise_name=installed_enterprise.get("name"),
                enterprise_url=enterprise_url,
                team_id=installed_team.get("id"),
                team_name=installed_team.get("name"),
                bot_token=bot_token,
                bot_id=bot_id,
                bot_user_id=oauth_response.get("bot_user_id"),
                bot_scopes=oauth_response.get("scope"),  # comma-separated string
                bot_refresh_token=oauth_response.get("refresh_token"),
                bot_token_expires_in=oauth_response.get("expires_in"),
                user_id=installer.get("id"),
                user_token=installer.get("access_token"),
                user_scopes=installer.get("scope"),  # comma-separated string
                user_refresh_token=installer.get("refresh_token"),
                user_token_expires_in=installer.get("expires_in"),
                incoming_webhook_url=incoming_webhook.get("url"),
                incoming_webhook_channel=incoming_webhook.get("channel"),
                incoming_webhook_channel_id=incoming_webhook.get("channel_id"),
                incoming_webhook_configuration_url=incoming_webhook.get("configuration_url"),
                is_enterprise_install=is_enterprise_install,
                token_type=oauth_response.get("token_type"),
            )
            installation_store.save(installation)
            return redirect_page_renderer.render_success_page(
                app_id=installation.app_id,
                team_id=installation.team_id,
                is_enterprise_install=installation.is_enterprise_install,
                enterprise_url=installation.enterprise_url,
            )
        else:
            return redirect_page_renderer.render_failure_page("the state value is already expired")

    error = request.args["error"] if "error" in request.args else ""
    return redirect_page_renderer.render_failure_page(error)


if __name__ == "__main__":
    # export SLACK_CLIENT_ID=123.123
    # export SLACK_CLIENT_SECRET=xxx
    # export SLACK_SIGNING_SECRET=***
    # export FLASK_ENV=development

    app.run("localhost", 3000)

    # python3 integration_tests/samples/token_rotation/oauth_sqlite3.py
    # ngrok http 3000
    # https://{yours}.ngrok.io/slack/oauth/start
