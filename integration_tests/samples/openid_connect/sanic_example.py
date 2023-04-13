import json
import jwt
import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
redirect_uri = os.environ["SLACK_REDIRECT_URI"]
scopes = ["openid", "email", "profile"]

from slack_sdk.web.async_client import AsyncWebClient
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


# https://sanicframework.org/
from sanic import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse

app = Sanic("my-awesome-slack-app")


@app.get("/slack/install")
async def oauth_start(req: Request):
    state = state_store.issue()
    url = authorization_url_generator.generate(state)
    response_body = (
        '<html><head><link rel="icon" href="data:,"></head><body>'
        f'<a href="{url}" style="align-items:center;color:#000;background-color:#fff;border:1px solid #ddd;border-radius:4px;display:inline-flex;font-family:Lato, sans-serif;font-size:16px;font-weight:600;height:48px;justify-content:center;text-decoration:none;width:256px"><svg xmlns="http://www.w3.org/2000/svg" style="height:20px;width:20px;margin-right:12px" viewBox="0 0 122.8 122.8"><path d="M25.8 77.6c0 7.1-5.8 12.9-12.9 12.9S0 84.7 0 77.6s5.8-12.9 12.9-12.9h12.9v12.9zm6.5 0c0-7.1 5.8-12.9 12.9-12.9s12.9 5.8 12.9 12.9v32.3c0 7.1-5.8 12.9-12.9 12.9s-12.9-5.8-12.9-12.9V77.6z" fill="#e01e5a"></path><path d="M45.2 25.8c-7.1 0-12.9-5.8-12.9-12.9S38.1 0 45.2 0s12.9 5.8 12.9 12.9v12.9H45.2zm0 6.5c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9H12.9C5.8 58.1 0 52.3 0 45.2s5.8-12.9 12.9-12.9h32.3z" fill="#36c5f0"></path><path d="M97 45.2c0-7.1 5.8-12.9 12.9-12.9s12.9 5.8 12.9 12.9-5.8 12.9-12.9 12.9H97V45.2zm-6.5 0c0 7.1-5.8 12.9-12.9 12.9s-12.9-5.8-12.9-12.9V12.9C64.7 5.8 70.5 0 77.6 0s12.9 5.8 12.9 12.9v32.3z" fill="#2eb67d"></path><path d="M77.6 97c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9-12.9-5.8-12.9-12.9V97h12.9zm0-6.5c-7.1 0-12.9-5.8-12.9-12.9s5.8-12.9 12.9-12.9h32.3c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9H77.6z" fill="#ecb22e"></path></svg>Sign in with Slack</a>'
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
            try:
                token_response = await AsyncWebClient().openid_connect_token(
                    client_id=client_id, client_secret=client_secret, code=code
                )
                logger.info(f"openid.connect.token response: {token_response}")
                id_token = token_response.get("id_token")
                claims = jwt.decode(id_token, options={"verify_signature": False}, algorithms=["RS256"])
                logger.info(f"claims (decoded id_token): {claims}")

                user_token = token_response.get("access_token")
                user_info_response = await AsyncWebClient(token=user_token).openid_connect_userInfo()
                logger.info(f"openid.connect.userInfo response: {user_info_response}")
                html = f"""
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
                return HTTPResponse(
                    status=200,
                    headers={
                        "Content-Type": "text/html; charset=utf-8",
                    },
                    body=html,
                )

            except Exception:
                logger.exception("Failed to perform openid.connect.token API call")
                html = redirect_page_renderer.render_failure_page("Failed to perform openid.connect.token API call")
                return HTTPResponse(
                    status=400,
                    headers={"Content-Type": "text/html; charset=utf-8"},
                    body=html,
                )

        else:
            html = redirect_page_renderer.render_failure_page("The state value is already expired")
            return HTTPResponse(
                status=400,
                headers={"Content-Type": "text/html; charset=utf-8"},
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
    # python3 integration_tests/samples/openid_connect/sanic_example.py
    # ngrok http 3000
    # https://{yours}.ngrok.io/slack/install
