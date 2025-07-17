# Tokens & installation

:::danger[The [`slackclient`](https://pypi.org/project/slackclient/) PyPI project is in maintenance mode and the [slack-sdk](https://pypi.org/project/slack-sdk/) project is its successor.] 

The v3 SDK provides additional features such as Socket Mode, OAuth flow, SCIM API, Audit Logs API, better asyncio support, retry handlers, and more.

:::

## Access tokens {#handling-tokens}

**Always keep your access tokens safe.**

The OAuth token you use to call the Slack Web API has access to the data on the workspace where it is installed. Depending on the scopes granted to the token, it potentially has the ability to read and write data. Treat these tokens just as you would a password — don't publish them, don't check them into source code, and don't share them with others.

Never do the following:

``` python
token = 'xoxb-111-222-xxxxx'
```

We recommend you pass tokens in as environment variables, or store them in a database that is accessed at runtime. You can add a token to the environment by starting your app as follows:

``` python
SLACK_BOT_TOKEN="xoxb-111-222-xxxxx" python myapp.py
```

Then, retrieve the key as follows:

``` python
import os
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
```

Refer to our [best practices for security](/authentication/best-practices-for-security) page for more information.

## Installing on a single workspace {#single-workspace}

If you're building an application for a single Slack workspace, there's no need to build out the entire OAuth flow. Once you've set up your features, click the **Install App to Team** button on the **Install App** page. If you add new permission scopes or Slack app features after an app has been installed, you must reinstall the app to your workspace for the changes to take effect.

Refer to the [quickstart](/quickstart) guide for more details.

## Installing on multiple workspaces {#multi-workspace}

If you intend for an app to be installed on multiple Slack workspaces, you will need to handle this installation via the industry-standard OAuth protocol. Read more about [installing with OAuth](/authentication/installing-with-oauth).

The OAuth exchange is facilitated via HTTP and requires a webserver; in this example, we'll use [Flask](https://flask.palletsprojects.com/).

To configure your app for OAuth, you'll need a client ID, a client secret, and a set of one or more scopes that will be applied to the token once it is granted. The client ID and client secret are available from the [app page](https://api.slack.com/apps). The scopes are determined by the functionality of the app — every method you wish to access has a corresponding scope, and your app will need to request that scope in order to be able to access the method. Review the full list of [OAuth scopes](/reference/scopes).

``` python
import os
from slack import WebClient
from flask import Flask, request

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
oauth_scope = os.environ["SLACK_SCOPES"]

app = Flask(__name__)
```

### The OAuth initiation link {#oauth-link}

To begin the OAuth flow that will install your app on a workspace, you'll need to provide the user with a link to the Slack OAuth page. This can be a simple link to `https://slack.com/oauth/v2/authorize` with the
`scope` and `client_id` query parameters.

This link directs the user to the OAuth acceptance page, where the user will review and accept or decline the permissions your app is requesting as defined by the scope(s).

``` python
@app.route("/slack/install", methods=["GET"])
def pre_install():
  state = "randomly-generated-one-time-value"
  return '<a href="https://slack.com/oauth/v2/authorize?' \
    f'scope={oauth_scope}&client_id={client_id}&state={state}">' \
    'Add to Slack</a>'
```

### The OAuth completion page {#oauth-completion}

Once the user has agreed to the permissions you've requested, Slack will redirect the user to your auth completion page, which includes a `code` query string parameter. You'll use the `code` parameter to call the [`oauth.v2.access`](/reference/methods/oauth.v2.access) API method that will grant you the token.

``` python
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
```

A successful request to the `oauth.v2.access` API method will yield a JSON payload with at least one token: a bot token that begins with `xoxb`.

``` python
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
```

Once your user has completed the OAuth flow, you'll be able to use the provided tokens to call any of the Slack Web API methods that require an access token.

Refer to the [basic usage](https://tools.slack.dev/python-slack-sdk/legacy/basic_usage) page for more examples.
