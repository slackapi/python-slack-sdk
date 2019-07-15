==============================================
Tokens & Authentication
==============================================
.. _handling-tokens:

Keeping tokens safe
-------------------

The OAuth token you use to call the Slack API has access to the data on the workspace where it is installed. Depending on the scopes granted to the token, it potentially has the ability to read and write data. Treat these tokens just as you would a password -- don't publish them, don't check them into source code, don't share them with others.

🚫Avoid this:

.. code-block:: python

  token = 'xoxb-abc-1232'

We recommend you pass tokens in as environment variables, or persist them in a database that is accessed at runtime. You can add a token to the environment by starting your app as:

.. code-block:: python

  SLACK_BOT_TOKEN="xoxb-abc-1232" python myapp.py

Then retrieve the key with:

.. code-block:: python

  import os
  SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

For additional information, please see our `Safely Storing Credentials <https://api.slack.com/docs/oauth-safety>`_ page.

Single Workspace Install
---------------------------------------
If you're building an application for a single Slack workspace, there's no need to build out the entire OAuth flow.

Once you've setup your features, click on the **Install App to Team** button found on the **Install App** page.
If you add new permission scopes or Slack app features after an app has been installed, you must reinstall the app to
your workspace for changes to take effect.

For additional information, see the `Installing Apps <https://api.slack.com/slack-apps#installing_apps>`_ of our `Building Slack apps <https://api.slack.com/slack-apps#installing_apps>`_ page.

Multiple Workspace Install
---------------------------------------------------
If you intend for an app to be installed on multiple Slack workspaces, you will need to handle this installation via the industry-standard OAuth protocoal. You can read more about `how Slack handles Oauth <https://api.slack.com/docs/oauth>`_.

(The OAuth exchange is facilitated via HTTP and requires a webserver; in this example, we'll use `Flask <http://flask.pocoo.org/>`_.)

To configure your app for OAuth, you'll need a client ID, a client secret, and a set of one or more scopes that will be applied to the token once it is granted. The client ID and client secret are available from your `app's configuration page <https://api.slack.com/apps>`_. The scopes are determined by the functionality of the app -- every method you wish to access has a corresponding scope and your app will need to request that scope in order to be able to access the method. Review Slack's `full list of OAuth scopes <https://api.slack.com/docs/oauth-scopes>`_.

.. code-block:: python

  import os
  import slack
  from flask import Flask, request

  client_id = os.environ["SLACK_CLIENT_ID"]
  client_secret = os.environ["SLACK_CLIENT_SECRET"]
  oauth_scope = os.environ["SLACK_BOT_SCOPE"]

  app = Flask(__name__)

**The OAuth initiation link**

To begin the OAuth flow that will install your app on a workspace, you'll need to provide the user with a link to Slack's OAuth page. This can be a simple link to https://slack.com/oauth/authorize with ``scope`` and ``client_id`` query parameters, or you can use our pre-built `Add to Slack button <https://api.slack.com/docs/slack-button>`_ to do all the work for you.

This link directs the user to Slack's OAuth acceptance page, where the user will review and accept or refuse the permissions your app is requesting as defined by the scope(s).

.. code-block:: python

  @app.route("/begin_auth", methods=["GET"])
  def pre_install():
    return f'<a href="https://slack.com/oauth/authorize?scope={ oauth_scope }&client_id={ client_id }">Add to Slack</a>'

**The OAuth completion page**

Once the user has agreed to the permissions you've requested, Slack will redirect the user to your auth completion page, which includes a ``code`` query string param. You'll use the ``code`` param to call the ``oauth.access`` `endpoint <https://api.slack.com/methods/oauth.access>`_ that will finally grant you the token.

.. code-block:: python

  @app.route("/finish_auth", methods=["GET", "POST"])
  def post_install():
    # Retrieve the auth code from the request params
      auth_code = request.args['code']

    # An empty string is a valid token for this request
      client = slack.WebClient(token="")

    # Request the auth tokens from Slack
      response = client.oauth_access(
          client_id=client_id,
          client_secret=client_secret,
          code=auth_code
      )

A successful request to ``oauth.access`` will yield a JSON payload with at least one token, a user token that begins with ``xoxp``. This ``user`` token is used to make requests on behalf of the user who installed the app.

If your Slack app includes a `bot user <https://api.slack.com/docs/bots>`_, the JSON response will contain an additional node containing an ``xoxb`` token to be used for on behalf of the bot user. When you intend to act on behalf of the bot user, be sure to use this token instead of the user (``xoxp``) token.

.. code-block:: python


  # Save the bot token to an environmental variable or to your data store
  # for later use
  os.environ["SLACK_USER_TOKEN"] = response['access_token']
  os.environ["SLACK_BOT_TOKEN"] = response['bot']['bot_access_token']

  # Don't forget to let the user know that auth has succeeded!
  return "Auth complete!"

Once your user has completed the OAuth flow, you'll be able to use the provided tokens to call any of Slack's API methods that require an access token.

See the :ref:`Web API usage <basic_usage>` section of this documentation for usage examples.

.. include:: metadata.rst
