import json
import logging
import os
import jwt

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
redirect_uri = os.environ["SLACK_REDIRECT_URI"]
scopes = ["openid", "email", "profile"]

from slack_sdk.web import WebClient
from slack_sdk.oauth import OpenIDConnectAuthorizeUrlGenerator, RedirectUriPageRenderer
from slack_sdk.oauth.state_store import FileOAuthStateStore

state_store = FileOAuthStateStore(expiration_seconds=300)

authorization_url_generator = OpenIDConnectAuthorizeUrlGenerator(
    client_id=client_id,
    scopes=scopes,
    redirect_uri=redirect_uri,
)
redirect_page_renderer = RedirectUriPageRenderer(
    install_path="/slack/install",
    redirect_uri_path="/slack/oauth_redirect",
)


from flask import Flask, request, make_response

app = Flask(__name__)
app.debug = True


@app.route("/slack/install", methods=["GET"])
def oauth_start():
    state = state_store.issue()
    url = authorization_url_generator.generate(state=state)
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
            try:
                token_response = WebClient().openid_connect_token(
                    client_id=client_id, client_secret=client_secret, code=code
                )
                logger.info(f"openid.connect.token response: {token_response}")
                id_token = token_response.get("id_token")
                claims = jwt.decode(
                    id_token, options={"verify_signature": False}, algorithms=["RS256"]
                )
                logger.info(f"claims (decoded id_token): {claims}")

                user_token = token_response.get("access_token")
                user_info_response = WebClient(
                    token=user_token
                ).openid_connect_userInfo()
                logger.info(f"openid.connect.userInfo response: {user_info_response}")
                return f"""
            <html>
            <head>
            <style>
            body h2 {{
              padding: 10px 15px;
              font-family: verdana;
              text-align: center;
            }}
            </style>
            </head>
            <body>
            <h2>OpenID Connect Claims</h2>
            <pre>{json.dumps(claims, indent=2)}</pre>
            <h2>openid.connect.userInfo response</h2>
            <pre>{json.dumps(user_info_response.data, indent=2)}</pre>
            </body>
            </html>
            """

            except Exception:
                logger.exception("Failed to perform openid.connect.token API call")
                return redirect_page_renderer.render_failure_page(
                    "Failed to perform openid.connect.token API call"
                )
        else:
            return redirect_page_renderer.render_failure_page(
                "The state value is already expired"
            )

    error = request.args["error"] if "error" in request.args else ""
    return make_response(
        f"Something is wrong with the installation (error: {error})", 400
    )


if __name__ == "__main__":
    # export SLACK_CLIENT_ID=111.222
    # export SLACK_CLIENT_SECRET=xxx
    # export FLASK_ENV=development
    # export SLACK_REDIRECT_URI=https://{your-domain}/slack/oauth_redirect
    # python3 integration_tests/samples/openid_connect/flask_example.py

    app.run("localhost", 3000)

    # ngrok http 3000
    # https://{yours}.ngrok.io/slack/install
