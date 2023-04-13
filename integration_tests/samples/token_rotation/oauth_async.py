# ---------------------
# Sanic App for Slack OAuth flow
# ---------------------

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
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.oauth.token_rotation.async_rotator import AsyncTokenRotator
from slack_sdk.oauth import AuthorizeUrlGenerator, RedirectUriPageRenderer
from slack_sdk.oauth.installation_store import FileInstallationStore, Installation
from slack_sdk.oauth.state_store import FileOAuthStateStore

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
scopes = ["app_mentions:read", "chat:write", "commands"]
user_scopes = ["search:read"]

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

state_store = FileOAuthStateStore(expiration_seconds=300)
installation_store = FileInstallationStore()
token_rotator = AsyncTokenRotator(
    client_id=client_id,
    client_secret=client_secret,
)

# ---------------------
# Sanic App for Slack events
# ---------------------

import json
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

signing_secret = os.environ["SLACK_SIGNING_SECRET"]
signature_verifier = SignatureVerifier(signing_secret=signing_secret)


async def rotate_tokens(
    enterprise_id: Optional[str] = None,
    team_id: Optional[str] = None,
    user_id: Optional[str] = None,
    is_enterprise_install: Optional[bool] = None,
):
    installation = await installation_store.async_find_installation(
        enterprise_id=enterprise_id,
        team_id=team_id,
        user_id=user_id,
        is_enterprise_install=is_enterprise_install,
    )
    if installation is not None:
        updated_installation = await token_rotator.perform_token_rotation(
            installation=installation,
            minutes_before_expiration=60 * 24 * 365,  # one year for testing
        )
        if updated_installation is not None:
            await installation_store.async_save(updated_installation)


# https://sanicframework.org/
from sanic import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse

app = Sanic("my-awesome-slack-app")


@app.post("/slack/events")
async def slack_app(req: Request):
    if not signature_verifier.is_valid(
        body=req.body.decode("utf-8"),
        timestamp=req.headers.get("X-Slack-Request-Timestamp"),
        signature=req.headers.get("X-Slack-Signature"),
    ):
        return HTTPResponse(status=403, body="invalid request")

    raw_body = req.body.decode("utf-8")
    body = parse_body(body=raw_body, content_type=extract_content_type(req.headers))
    await rotate_tokens(
        enterprise_id=extract_enterprise_id(body),
        team_id=extract_team_id(body),
        user_id=extract_user_id(body),
        is_enterprise_install=extract_is_enterprise_install(body),
    )

    if "command" in req.form and req.form.get("command") == "/token-rotation-modal":
        try:
            enterprise_id = req.form.get("enterprise_id")
            team_id = req.form.get("team_id")
            bot = await installation_store.async_find_bot(
                enterprise_id=enterprise_id,
                team_id=team_id,
            )
            bot_token = bot.bot_token if bot else None
            if not bot_token:
                return HTTPResponse(status=200, body="Please install this app first!")

            client = AsyncWebClient(token=bot_token)
            await client.views_open(
                trigger_id=req.form.get("trigger_id"),
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
            return HTTPResponse(status=200, body="")
        except SlackApiError as e:
            code = e.response["error"]
            return HTTPResponse(status=200, body=f"Failed to open a modal due to {code}")

    elif "payload" in req.form:
        payload = json.loads(req.form.get("payload"))
        if payload.get("type") == "view_submission" and payload.get("view").get("callback_id") == "modal-id":
            submitted_data = payload.get("view").get("state").get("values")
            print(submitted_data)  # {'b-id': {'a-id': {'type': 'plain_text_input', 'value': 'your input'}}}
            return HTTPResponse(status=200, body="")

    else:
        if raw_body.startswith("{"):
            event_payload = json.loads(raw_body)
            if event_payload.get("type") == "url_verification":
                return HTTPResponse(status=200, body=event_payload.get("challenge"))
            return HTTPResponse(status=200, body="")

    return HTTPResponse(status=404, body="Not found")


# ---------------------
# Sanic App for Slack OAuth flow
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


@app.get("/slack/install")
async def oauth_start(req: Request):
    state = state_store.issue()
    url = authorization_url_generator.generate(state)
    response_body = (
        '<html><head><link rel="icon" href="data:,"></head><body>'
        f'<a href="{url}">'
        f'<img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>'
        "</body></html>"
    )
    return HTTPResponse(
        status=200,
        body=response_body,
    )


@app.get("/slack/oauth_redirect")
async def oauth_callback(req: Request):
    # Retrieve the auth code and state from the request params
    if "code" in req.args:
        state = req.args.get("state")
        if state_store.consume(state):
            code = req.args.get("code")
            client = AsyncWebClient()  # no prepared token needed for this app
            oauth_response = await client.oauth_v2_access(client_id=client_id, client_secret=client_secret, code=code)
            logger.info(f"oauth.v2.access response: {oauth_response}")

            installed_enterprise = oauth_response.get("enterprise") or {}
            installed_team = oauth_response.get("team") or {}
            installer = oauth_response.get("authed_user") or {}
            incoming_webhook = oauth_response.get("incoming_webhook") or {}
            bot_token = oauth_response.get("access_token")
            # NOTE: oauth.v2.access doesn't include bot_id in response
            bot_id = None
            if bot_token is not None:
                auth_test = await client.auth_test(token=bot_token)
                bot_id = auth_test["bot_id"]

            installation = Installation(
                app_id=oauth_response.get("app_id"),
                enterprise_id=installed_enterprise.get("id"),
                team_id=installed_team.get("id"),
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
                incoming_webhook_channel_id=incoming_webhook.get("channel_id"),
                incoming_webhook_configuration_url=incoming_webhook.get("configuration_url"),
            )
            await installation_store.async_save(installation)
            html = redirect_page_renderer.render_success_page(
                app_id=installation.app_id,
                team_id=installation.team_id,
                is_enterprise_install=installation.is_enterprise_install,
                enterprise_url=installation.enterprise_url,
            )
            return HTTPResponse(
                status=200,
                headers={
                    "Content-Type": "text/html; charset=utf-8",
                },
                body=html,
            )
        else:
            html = redirect_page_renderer.render_failure_page("the state value is already expired")
            return HTTPResponse(
                status=400,
                headers={
                    "Content-Type": "text/html; charset=utf-8",
                },
                body=html,
            )

    error = req.args.get("error") if "error" in req.args else ""
    return HTTPResponse(
        status=400,
        headers={"Content-Type": "text/html; charset=utf-8"},
        body=redirect_page_renderer.render_failure_page(error),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
    # python3 integration_tests/samples/token_rotation/oauth_async.py
    # ngrok http 3000
    # https://{yours}.ngrok.io/slack/install
