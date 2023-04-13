# ---------------------
# Sanic App for Slack OAuth flow
# ---------------------
import html
import logging
import os
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.oauth import AuthorizeUrlGenerator, RedirectUriPageRenderer
from slack_sdk.oauth.installation_store import FileInstallationStore, Installation
from slack_sdk.oauth.state_store import FileOAuthStateStore

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
scopes = ["app_mentions:read", "chat:write"]
user_scopes = ["search:read"]

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

state_store = FileOAuthStateStore(expiration_seconds=300)
installation_store = FileInstallationStore()
authorization_url_generator = AuthorizeUrlGenerator(
    client_id=client_id,
    scopes=scopes,
    user_scopes=user_scopes,
)
redirect_page_renderer = RedirectUriPageRenderer(
    install_path="/slack/install",
    redirect_uri_path="/slack/oauth_redirect",
)

# https://sanicframework.org/
from sanic import Sanic
from sanic.response import json
from sanic.request import Request
from sanic.response import HTTPResponse

app = Sanic("my-awesome-slack-app")


@app.get("/slack/install")
async def oauth_start(req: Request):
    state = state_store.issue()
    url = authorization_url_generator.generate(state)
    return HTTPResponse(
        status=200,
        body=f'<a href="{html.escape(url)}">'
        f'<img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>',
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
            is_enterprise_install = oauth_response.get("is_enterprise_install")
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
                user_id=installer.get("id"),
                user_token=installer.get("access_token"),
                user_scopes=installer.get("scope"),  # comma-separated string
                incoming_webhook_url=incoming_webhook.get("url"),
                incoming_webhook_channel_id=incoming_webhook.get("channel_id"),
                incoming_webhook_configuration_url=incoming_webhook.get("configuration_url"),
                is_enterprise_install=is_enterprise_install,
                token_type=oauth_response.get("token_type"),
            )
            installation_store.save(installation)
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


# ---------------------
# Sanic App for Slack events
# ---------------------

import json
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

signing_secret = os.environ["SLACK_SIGNING_SECRET"]
signature_verifier = SignatureVerifier(signing_secret=signing_secret)


@app.post("/slack/events")
async def slack_app(req: Request):
    if not signature_verifier.is_valid(
        body=req.body.decode("utf-8"),
        timestamp=req.headers.get("X-Slack-Request-Timestamp"),
        signature=req.headers.get("X-Slack-Signature"),
    ):
        return HTTPResponse(status=403, body="invalid request")

    if "command" in req.form and req.form.get("command") == "/open-modal":
        try:
            enterprise_id = req.form.get("enterprise_id")
            team_id = req.form.get("team_id")
            bot = installation_store.find_bot(
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

    return HTTPResponse(status=404, body="Not found")


if __name__ == "__main__":
    # export SLACK_CLIENT_ID=123.123
    # export SLACK_CLIENT_SECRET=xxx
    # export SLACK_SIGNING_SECRET=***

    app.run(host="0.0.0.0", port=3000)
    # python3 integration_tests/samples/oauth/oauth_v2_async.py
    # ngrok http 3000
    # https://{yours}.ngrok.io/slack/install
