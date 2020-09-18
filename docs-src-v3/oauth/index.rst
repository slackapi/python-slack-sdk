==============================================
OAuth Modules
==============================================

This section explains the details about how to handle Slack's OAuth flow.

If you're looking for a much easier way to do the same, check `Bolt for Python <https://github.com/slackapi/bolt-python>`_, which is a full-stack Slack App framework. With Bolt, you don't need to implement most of the following code on your own.

App Installation Flow
*************************************************

OAuth lets a user in any Slack workspace install your app. At the end of OAuth, your app gains an access token. Refer to `Installing with OAuth <https://api.slack.com/authentication/oauth-v2>`_ for details.

Python Slack SDK provides the necessary modules for building the OAuth flow.

**Starting an OAuth flow**

The first step of Slack OAuth flow is to redirect a Slack user to https://slack.com/oauth/v2/authorize with a valida ``state`` parameter. To implement this process, you can use the following modules.

+---------------------------+-----------------------------------------------------------------------------+---------------------------+
| Module                    | What its for                                                                | Default Implementation    |
+---------------------------+-----------------------------------------------------------------------------+---------------------------+
| ``InstallationStore``     | Persist installation data and lookup it by IDs.                             | ``FileInstallationStore`` |
+---------------------------+-----------------------------------------------------------------------------+---------------------------+
| ``OAuthStateStore``       | Issue and consume ``state`` parameter value on the server-side.             | ``FileOAuthStateStore``   |
+---------------------------+-----------------------------------------------------------------------------+---------------------------+
| ``AuthorizeUrlGenerator`` | Build https://slack.com/oauth/v2/authorize with sufficient query parameters | (same)                    |
+---------------------------+-----------------------------------------------------------------------------+---------------------------+

The code snippet below demonstrates how to build it using `Flask <https://flask.palletsprojects.com/>`_.

.. code-block:: python

    import os
    from slack_sdk.oauth import AuthorizeUrlGenerator
    from slack_sdk.oauth.installation_store import FileInstallationStore, Installation
    from slack_sdk.oauth.state_store import FileOAuthStateStore

    # Issue and consume state parameter value on the server-side.
    state_store = FileOAuthStateStore(expiration_seconds=300, base_dir="./data")
    # Persist installation data and lookup it by IDs.
    installation_store = FileInstallationStore(base_dir="./data")

    # Build https://slack.com/oauth/v2/authorize with sufficient query parameters
    authorization_url_generator = AuthorizeUrlGenerator(
        client_id=os.environ["SLACK_CLIENT_ID"],
        scopes=["app_mentions:read", "chat:write"],
        user_scopes=["search:read"],
    )

    from flask import Flask, request, make_response
    app = Flask(__name__)

    @app.route("/slack/install", methods=["GET"])
    def oauth_start():
        # Generate a random value and store it on the server-side
        state = state_store.issue()
        # https://slack.com/oauth/v2/authorize?state=(generated value)&client_id={client_id}&scope=app_mentions:read,chat:write&user_scope=search:read
        url = authorization_url_generator.generate(state)
        return f'<a href="{url}">' \
               f'<img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>'

When accessing ``https://(your domain)/slack/install``, you will see "Add to Slack" button in the webpage. You can start the app's installation flow by clicking the button.

**Handling a callback request from Slack**

If all's well, a user goes through the Slack app installation UI and okays your app with all the scopes that it requests. After that happens, Slack redirects the user back to your specified Redirect URL.

The redirection gives you a ``code`` parameter. You can exchange the value for an access token by calling `oauth.v2.access <https://api.slack.com/methods/oauth.v2.access>`_ API method.

.. code-block:: python

    from slack_sdk.web import WebClient
    client_secret = os.environ["SLACK_CLIENT_SECRET"]

    # Redirect URL
    @app.route("/slack/oauth/callback", methods=["GET"])
    def oauth_callback():
        # Retrieve the auth code and state from the request params
        if "code" in request.args:
            # Verify the state parameter
            if state_store.consume(request.args["state"]):
                client = WebClient()  # no prepared token needed for this
                # Complete the installation by calling oauth.v2.access API method
                oauth_response = client.oauth_v2_access(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    code=request.args["code"]
                )

                installed_enterprise = oauth_response.get("enterprise") or {}
                installed_team = oauth_response.get("team") or {}
                installer = oauth_response.get("authed_user") or {}
                incoming_webhook = oauth_response.get("incoming_webhook") or {}
                bot_token = oauth_response.get("access_token")
                # NOTE: As oauth.v2.access doesn't include bot_id in response,
                # we call bots.info for storing the installation data along with bot_id.
                bot_id = None
                if bot_token is not None:
                    auth_test = client.auth_test(token=bot_token)
                    bot_id = auth_test["bot_id"]

                # Build an installation data
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
                # Store the installation
                installation_store.save(installation)

                return "Thanks for installing this app!"
            else:
                return make_response(f"Try the installation again (the state value is already expired)", 400)

        error = request.args["error"] if "error" in request.args else ""
        return make_response(f"Something is wrong with the installation (error: {error})", 400)

Token Lookup
*************************************************

Now that your Flask app can choose the right access token for incoming event requests, let's add the Slack event handler endpoint.

You can use the same ``InstallationStore`` in the Slack event handler.

.. code-block:: python

    import json
    from slack_sdk.errors import SlackApiError

    from slack_sdk.signature import SignatureVerifier
    signing_secret = os.environ["SLACK_SIGNING_SECRET"]
    signature_verifier = SignatureVerifier(signing_secret=signing_secret)

    @app.route("/slack/events", methods=["POST"])
    def slack_app():
        # Verify incoming requests from Slack
        # https://api.slack.com/authentication/verifying-requests-from-slack
        if not signature_verifier.is_valid(
            body=request.get_data(),
            timestamp=request.headers.get("X-Slack-Request-Timestamp"),
            signature=request.headers.get("X-Slack-Signature")):
            return make_response("invalid request", 403)

        # Handle a slash command invocation
        if "command" in request.form \
            and request.form["command"] == "/open-modal":
            try:
                # in the case where this app gets a request from an Enterprise Grid workspace
                enterprise_id = request.form.get("enterprise_id")
                # The workspace's ID
                team_id = request.form["team_id"]
                # Lookup the stored bot token for this workspace
                bot = installation_store.find_bot(
                    enterprise_id=enterprise_id,
                    team_id=team_id,
                )
                bot_token = bot.bot_token if bot else None
                if not bot_token:
                    # The app may be uninstalled or be used in a shared channel
                    return make_response("Please install this app first!", 200)

                # Open a modal using the valid bot token
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
            # Data submission from the modal
            payload = json.loads(request.form["payload"])
            if payload["type"] == "view_submission" \
                and payload["view"]["callback_id"] == "modal-id":
                submitted_data = payload["view"]["state"]["values"]
                print(submitted_data)  # {'b-id': {'a-id': {'type': 'plain_text_input', 'value': 'your input'}}}
                # You can use WebClient with a valid token here too
                return make_response("", 200)

        # Indicate unsupported request patterns
        return make_response("", 404)


Again, if you're looking for an easier solution, take a look at `Bolt for Python <https://github.com/slackapi/bolt-python>`_. With Bolt, you don't need to implement most of the above code on your own.


.. include:: ../metadata.rst