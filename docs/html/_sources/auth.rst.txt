==============================================
Tokens & Authentication
==============================================
.. _handling-tokens:

Handling tokens and other sensitive data
----------------------------------------
⚠️ **Slack tokens are the keys to your—or your customers’—data.Keep them secret. Keep them safe.**

One way to do that is to never explicitly hardcode them.

Try to avoid this when possible:

.. code-block:: python

  token = 'xoxb-abc-1232'

⚠️ **Never share test tokens with other users or applications. Do not publish test tokens in public code repositories.**

We recommend you pass tokens in as environment variables, or persist them in a database that is accessed at runtime. You can add a token to the environment by starting your app as:

.. code-block:: python

  SLACK_BOT_TOKEN="xoxb-abc-1232" python myapp.py

Then retrieve the key with:

.. code-block:: python

  import os
  SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

You can use the same technique for other kinds of sensitive data that ne’er-do-wells could use in nefarious ways, including

- Incoming webhook URLs
- Slash command verification tokens
- App client ids and client secrets

For additional information, please see our `Safely Storing Credentials <https://api.slack.com/docs/oauth-safety>`_ page.

Single-Workspace Apps
-----------------------
If you're building an application for a single Slack workspace, there's no need to build out the entire OAuth flow.

Once you've setup your features, click on the **Install App to Team** button found on the **Install App** page.
If you add new permission scopes or Slack app features after an app has been installed, you must reinstall the app to
your workspace for changes to take effect.

For additional information, see the `Installing Apps <https://api.slack.com/slack-apps#installing_apps>`_ of our `Building Slack apps <https://api.slack.com/slack-apps#installing_apps>`_ page.

The OAuth flow
-------------------------
Authentication for Slack's APIs is done using OAuth, so you'll want to read up on `OAuth <https://api.slack.com/docs/oauth>`_.

In order to implement OAuth in your app, you will need to include a web server. In this example, we'll use `Flask <http://flask.pocoo.org/>`_.

As mentioned above, we're setting the app tokens and other configs in environment variables and pulling them into global variables.

Depending on what actions your app will need to perform, you'll need different OAuth permission scopes. Review the available scopes `here <https://api.slack.com/docs/oauth-scopes>`_.

.. code-block:: python

  import os
  from flask import Flask, request
  from slackclient import SlackClient

  client_id = os.environ["SLACK_CLIENT_ID"]
  client_secret = os.environ["SLACK_CLIENT_SECRET"]
  oauth_scope = os.environ["SLACK_BOT_SCOPE"]

  app = Flask(__name__)

**The OAuth initiation link:**

To begin the OAuth flow, you'll need to provide the user with a link to Slack's OAuth page.
This directs the user to Slack's OAuth acceptance page, where the user will review and accept
or refuse the permissions your app is requesting as defined by the requested scope(s).

For the best user experience, use the `Add to Slack button <https://api.slack.com/docs/slack-button>`_ to direct users to approve your application for access or `Sign in with Slack <https://api.slack.com/docs/sign-in-with-slack>`_ to log users in.

.. code-block:: python

  @app.route("/begin_auth", methods=["GET"])
  def pre_install():
    return '''
        <a href="https://slack.com/oauth/authorize?scope={0}&client_id={1}">
            Add to Slack
        </a>
    '''.format(oauth_scope, client_id)

**The OAuth completion page**

Once the user has agreed to the permissions you've requested on Slack's OAuth
page, Slack will redirect the user to your auth completion page. Included in this
redirect is a ``code`` query string param which you’ll use to request access
tokens from the ``oauth.access`` endpoint.

Generally, Web API requests require a valid OAuth token, but there are a few endpoints
which do not require a token. ``oauth.access`` is one example of this. Since this
is the endpoint you'll use to retrieve the tokens for later API requests,
an empty string ``""`` is acceptable for this request.

.. code-block:: python

  @app.route("/finish_auth", methods=["GET", "POST"])
  def post_install():

    # Retrieve the auth code from the request params
    auth_code = request.args['code']

    # An empty string is a valid token for this request
    sc = SlackClient("")

    # Request the auth tokens from Slack
    auth_response = sc.api_call(
      "oauth.access",
      client_id=client_id,
      client_secret=client_secret,
      code=auth_code
    )

A successful request to ``oauth.access`` will yield two tokens: A ``user``
token and a ``bot`` token. The ``user`` token ``auth_response['access_token']``
is used to make requests on behalf of the authorizing user and the ``bot``
token ``auth_response['bot']['bot_access_token']`` is for making requests
on behalf of your app's bot user.

If your Slack app includes a bot user, upon approval the JSON response will contain
an additional node containing an access token to be specifically used for your bot
user, within the context of the approving team.

When you use Web API methods on behalf of your bot user, you should use this bot
user access token instead of the top-level access token granted to your application.

.. code-block:: python

    # Save the bot token to an environmental variable or to your data store
    # for later use
    os.environ["SLACK_USER_TOKEN"] = auth_response['access_token']
    os.environ["SLACK_BOT_TOKEN"] = auth_response['bot']['bot_access_token']

    # Don't forget to let the user know that auth has succeeded!
    return "Auth complete!"

Once your user has completed the OAuth flow, you'll be able to use the provided
tokens to make a variety of Web API calls on behalf of the user and your app's bot user.

See the :ref:`Web API usage <web-api-examples>` section of this documentation for usage examples.

.. include:: metadata.rst
