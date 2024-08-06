# Installation

This package supports Python 3.6 and higher. We recommend using
[PyPI](https://pypi.python.org/pypi) to install. Run the following command:

``` bash
pip install slack_sdk
```

Alternatively, you can always pull the source code directly into your
project:

``` bash
git clone https://github.com/slackapi/python-slack-sdk.git
cd python-slack-sdk
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .  # install the SDK project into the virtual env
```

Create a `./test.py` file with the following:

``` python  title="test.py"
# test.py
import sys
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
# Verify it works
from slack_sdk import WebClient
client = WebClient()
api_response = client.api_test()
```

Then, run the script:

``` bash
python test.py
```

It's also good to try on the Python REPL.

## Access Tokens {#handling-tokens}

**Always keep your access tokens safe.**

The OAuth token you use to call the Slack API has access to the data on
the workspace where it is installed.

Depending on the scopes granted to the token, it potentially has the
ability to read and write data. Treat these tokens just as you would a
password — don't publish them, don't check them into source code, and
don't share them with others.


:::danger

Never do the following:

``` python
token = 'xoxb-111-222-xxxxx'
```

:::

We recommend you pass tokens in as environment variables, or persist
them in a database that is accessed at runtime. You can add a token to
the environment by starting your app as:

``` python
SLACK_BOT_TOKEN="xoxb-111-222-xxxxx" python myapp.py
```

Then retrieve the key with:

``` python
import os
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
```

For additional information, please see the [Safely Storing
Credentials](https://api.slack.com/authentication/best-practices) page within the Slack API docs.

## Workspace Installations

### Single Workspace Install

If you're building an application for a single Slack workspace,
there's no need to build out the entire OAuth flow.

Once you've setup your features, click on the **Install App to Team**
button found on the **Install App** page. If you add new permission
scopes or Slack app features after an app has been installed, you must
reinstall the app to your workspace for changes to take effect.

## Multiple Workspace Install

If you intend for an app to be installed on multiple Slack workspaces,
you will need to handle this installation via the industry-standard
OAuth protocol. You can read more about [how Slack handles
Oauth](https://api.slack.com/authentication/oauth-v2).

(The OAuth exchange is facilitated via HTTP and requires a webserver; in
this example, we'll use [Flask](https://flask.palletsprojects.com/).)

To configure your app for OAuth, you'll need a client ID, a client
secret, and a set of one or more scopes that will be applied to the
token once it is granted. The client ID and client secret are available
from your [app's configuration page](https://api.slack.com/apps). The
scopes are determined by the functionality of the app — every method
you wish to access has a corresponding scope and your app will need to
request that scope in order to be able to access the method. Review the [full list of Slack OAuth scopes](https://api.slack.com/scopes).

``` python
import os
from slack_sdk import WebClient
from flask import Flask, request

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
oauth_scope = os.environ["SLACK_SCOPES"]

app = Flask(__name__)
```

### The OAuth initiation link

To begin the OAuth flow that will install your app on a workspace,
you'll need to provide the user with a link to the Slack OAuth page.
This can be a simple link to `https://slack.com/oauth/v2/authorize` with
`scope` and `client_id` query parameters, or you can use our pre-built
[Add to Slack button](https://api.slack.com/docs/slack-button) to do all
the work for you.

This link directs the user to the Slack OAuth acceptance page, where the
user will review and accept or refuse the permissions your app is
requesting as defined by the scope(s).

``` python
@app.route("/slack/install", methods=["GET"])
def pre_install():
    state = "randomly-generated-one-time-value"
    return '<a href="https://slack.com/oauth/v2/authorize?' \
        f'scope={oauth_scope}&client_id={client_id}&state={state}">' \
        'Add to Slack</a>'
```

### The OAuth completion page

Once the user has agreed to the permissions you've requested, Slack
will redirect the user to your auth completion page, which includes a
`code` query string param. You'll use the `code` param to call the
`oauth.v2.access`
[endpoint](https://api.slack.com/methods/oauth.v2.access) that will
finally grant you the token.

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

A successful request to `oauth.v2.access` will yield a JSON payload with
at least one token, a bot token that begins with `xoxb`.

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

Once your user has completed the OAuth flow, you'll be able to use the
provided tokens to call any of the Slack API methods that require an
access token.

## Installation Troubleshooting

We recommend using [virtualenv
(venv)](https://docs.python.org/3/tutorial/venv.html) to set up your
Python runtime.

``` bash
# Create a dedicated virtual env for running your Python scripts
python -m venv .venv

# Run .venv\Scripts\activate on Windows OS
source .venv/bin/activate

# Install slack_sdk PyPI package
pip install "slack_sdk>=3.0"

# Set your token as an env variable (`set` command for Windows OS)
export SLACK_BOT_TOKEN=xoxb-***
```

Then, verify the following code works on the Python REPL (you can start
it by just `python`).

``` python
import os
import logging
from slack_sdk import WebClient
logging.basicConfig(level=logging.DEBUG)
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
res = client.api_test()
```

As the `slack` package is deprecated, we recommend switching to `slack_sdk`
package. That being said, the code you're working on may be still using
the old package. If you encounter an error saying
`AttributeError: module 'slack' has no attribute 'WebClient'`, run
`pip list`. If you find both `slack_sdk` and `slack` in the output, try
removing `slack` by `pip uninstall slack` and reinstalling `slack_sdk`.