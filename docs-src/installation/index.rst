==============================================
Installation
==============================================
.. _handling-tokens:

Access Tokens
-------------------

**Keeping access tokens safe**

The OAuth token you use to call the Slack API has access to the data on the workspace where it is installed.

Depending on the scopes granted to the token, it potentially has the ability to read and write data. Treat these tokens just as you would a password -- don't publish them, don't check them into source code, don't share them with others.

🚫Avoid this:

.. code-block:: python

    token = 'xoxb-111-222-xxxxx'

We recommend you pass tokens in as environment variables, or persist them in a database that is accessed at runtime. You can add a token to the environment by starting your app as:

.. code-block:: python

    SLACK_BOT_TOKEN="xoxb-111-222-xxxxx" python myapp.py

Then retrieve the key with:

.. code-block:: python

    import os
    SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

For additional information, please see our `Safely Storing Credentials <https://api.slack.com/authentication/best-practices>`_ page.

Workspace Installations
---------------------------------------

**Single Workspace Install**

If you're building an application for a single Slack workspace, there's no need to build out the entire OAuth flow.

Once you've setup your features, click on the **Install App to Team** button found on the **Install App** page.
If you add new permission scopes or Slack app features after an app has been installed, you must reinstall the app to
your workspace for changes to take effect.

For additional information, see the `Installing Apps <https://api.slack.com/start/overview#installing_distributing>`_ of our `Building Slack apps <https://api.slack.com/start>`_ page.

**Multiple Workspace Install**

If you intend for an app to be installed on multiple Slack workspaces, you will need to handle this installation via the industry-standard OAuth protocol. You can read more about `how Slack handles Oauth <https://api.slack.com/authentication/oauth-v2>`_.

(The OAuth exchange is facilitated via HTTP and requires a webserver; in this example, we'll use `Flask <https://flask.palletsprojects.com/>`_.)

To configure your app for OAuth, you'll need a client ID, a client secret, and a set of one or more scopes that will be applied to the token once it is granted. The client ID and client secret are available from your `app's configuration page <https://api.slack.com/apps>`_. The scopes are determined by the functionality of the app -- every method you wish to access has a corresponding scope and your app will need to request that scope in order to be able to access the method. Review Slack's `full list of OAuth scopes <https://api.slack.com/scopes>`_.

.. code-block:: python

    import os
    from slack_sdk import WebClient
    from flask import Flask, request

    client_id = os.environ["SLACK_CLIENT_ID"]
    client_secret = os.environ["SLACK_CLIENT_SECRET"]
    oauth_scope = os.environ["SLACK_SCOPES"]

    app = Flask(__name__)

**The OAuth initiation link**

To begin the OAuth flow that will install your app on a workspace, you'll need to provide the user with a link to Slack's OAuth page. This can be a simple link to ``https://slack.com/oauth/v2/authorize`` with ``scope`` and ``client_id`` query parameters, or you can use our pre-built `Add to Slack button <https://api.slack.com/docs/slack-button>`_ to do all the work for you.

This link directs the user to Slack's OAuth acceptance page, where the user will review and accept or refuse the permissions your app is requesting as defined by the scope(s).

.. code-block:: python

    @app.route("/slack/install", methods=["GET"])
    def pre_install():
        state = "randomly-generated-one-time-value"
        return '<a href="https://slack.com/oauth/v2/authorize?' \
            f'scope={oauth_scope}&client_id={client_id}&state={state}">' \
            'Add to Slack</a>'

**The OAuth completion page**

Once the user has agreed to the permissions you've requested, Slack will redirect the user to your auth completion page, which includes a ``code`` query string param. You'll use the ``code`` param to call the ``oauth.v2.access`` `endpoint <https://api.slack.com/methods/oauth.v2.access>`_ that will finally grant you the token.

.. code-block:: python

    @app.route("/slack/oauth_redirect", methods=["GET"])
    def post_install():
        # Verify the "state" parameter

        # Retrieve the auth code from the request params
        code_param = request.args['code']

        # An empty string is a valid token for this request
        client = WebClient()

        # Request the auth tokens from Slack
        response = client.oauth_v2_access(
            client_id=client_id,
            client_secret=client_secret,
            code=code_param
        )

A successful request to ``oauth.v2.access`` will yield a JSON payload with at least one token, a bot token that begins with ``xoxb``.

.. code-block:: python

    @app.route("/slack/oauth_redirect", methods=["GET"])
    def post_install():
        # Verify the "state" parameter

        # Retrieve the auth code from the request params
        code_param = request.args['code']

        # An empty string is a valid token for this request
        client = WebClient()

        # Request the auth tokens from Slack
        response = client.oauth_v2_access(
            client_id=client_id,
            client_secret=client_secret,
            code=code_param
        )
        print(response)

        # Save the bot token to an environmental variable or to your data store
        # for later use
        os.environ["SLACK_BOT_TOKEN"] = response['access_token']

        # Don't forget to let the user know that OAuth has succeeded!
        return "Installation is completed!"

    if __name__ == "__main__":
        app.run("localhost", 3000)

Once your user has completed the OAuth flow, you'll be able to use the provided tokens to call any of Slack's API methods that require an access token.

See the `Basic Usage <../basic_usage.html>`_ section of this documentation for usage examples.

.. include:: ../metadata.rst
