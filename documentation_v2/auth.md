# Tokens & Authentication

Slack Tokens are the keys to access data in Slack for both you and your customers' workspaces. These should be kept secret and never exposed publically. We recommend never to explicitly hardcode these and never to publish test or live tokens in your repositories.

> **Note**: Please avoid situations like this in your code:

```python
token = 'xoxb-abc-123'
```

Our recommendation is to pass tokens in as environment variables or keep them in a datastore that is accessed at Runtime. You can also add a token at runtime by starting your app similar to the below:

```bash
SLACK_BOT_TOKEN="xoxb-abc-123" python app.py
```

Inside your `app.py` file, you could then reference this by using something similar to the following:

```python
import os
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
```

You should also use this technique for all other kinds of sensitive data such as:

* Incoming webhook URLs
* Slash command verification tokens
* App client ids and client secrets

For additional information, please see our [Safely Storing Credentials][safely-store-credentials] page.

</br>

## Single-Workspace Apps
--- 
If you’re building an application for a single Slack workspace, there’s no need to build out the entire OAuth flow.

Once you’ve setup your features, click on the **Install App to Team** button found on the **Install App** page. If you add new permission scopes or Slack app features after an app has been installed, you must reinstall the app to your workspace for changes to take effect.

For additional information, see the [Installing Apps][installing-apps] of our [Building Slack apps page][building-slack-apps].

</br>

## The OAuth flow
---
Authentication for Slack’s APIs is done using OAuth, so you’ll want to read up on [OAuth][oauth].

In order to implement OAuth in your app, you will need to include a web server. In this example, we’ll use [Flask][flask] however most webservers should work.

As mentioned above, we’re setting the app tokens and other configs in environment variables and pulling them into global variables.

Depending on what actions your app will need to perform, you’ll need different OAuth permission scopes. Review the available scopes [here][scopes].


```python
import os
from flask import Flask, request
import slack

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
oauth_scope = os.environ["SLACK_BOT_SCOPE"]

app = Flask(__name__)
```

### The OAuth initiation link:

To begin the OAuth flow, you’ll need to provide the user with a link to Slack’s OAuth page. This directs the user to Slack’s OAuth acceptance page, where the user will review and accept or refuse the permissions your app is requesting as defined by the requested scope(s).

For the best user experience, use the [Add to Slack][add-to-slack] button to direct users to approve your application for access or [Sign in with Slack][sign-in-with-slack] to log users in.

```python
@app.route("/begin_auth", methods=["GET"])
def pre_install():
  return f'<a href="https://slack.com/oauth/authorize?scope={ oauth_scope }&client_id={ client_id }">Add to Slack</a>'
```
### The OAuth completion page

Once the user has agreed to the permissions you’ve requested on Slack’s OAuth page, Slack will redirect the user to your auth completion page. Included in this redirect is a `code` query string param which you’ll use to request access tokens from the [`oauth.access`][oauth.access] endpoint.

Generally, Web API requests require a valid OAuth token, but there are a few endpoints which do not require a token. oauth.access is one example of this. Since this is the endpoint you’ll use to retrieve the tokens for later API requests, an empty string `""` is acceptable for this request.

```python
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
```

A successful request to `oauth.access` will yield two tokens: A user token and a bot token. The `user` token `response['access_token']` is used to make requests on behalf of the authorizing user and the bot token `response['bot']['bot_access_token']` is for making requests on behalf of your app’s bot user.

If your Slack app includes a bot user, upon approval the JSON response will contain an additional node containing an `access token` to be specifically used for your bot user, within the context of the approving team.

When you use Web API methods on behalf of your bot user, you should use this bot user access token instead of the top-level access token granted to your application.

```python
# Save the bot token to an environmental variable or to your data store
# for later use
os.environ["SLACK_USER_TOKEN"] = response['access_token']
os.environ["SLACK_BOT_TOKEN"] = response['bot']['bot_access_token']

# Don't forget to let the user know that auth has succeeded!
return "Auth complete!"
```

Once your user has completed the OAuth flow, you’ll be able to use the provided tokens to make a variety of Web API calls on behalf of the user and your app’s bot user.





[safely-store-credentials]: https://api.slack.com/docs/oauth-safety
[installing-apps]: https://api.slack.com/slack-apps#installing_apps
[building-slack-apps]: https://api.slack.com/slack-apps#installing_apps
[oauth]: https://api.slack.com/docs/oauth
[flask]: http://flask.pocoo.org/
[scopes]: https://api.slack.com/docs/oauth-scopes
[add-to-slack]: https://api.slack.com/docs/slack-button
[sign-in-with-slack]: https://api.slack.com/docs/sign-in-with-slack
[oauth.access]: https://api.slack.com/methods/oauth.access