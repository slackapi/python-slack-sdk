# Migrating to 2.0

If you're migrating from v1.x of slackclient to v2.x, here's what you need to change to ensure your app continues working after updating.

**NOTE**: We have completely rewritten this library and you should only upgrade once you have fully tested it in your development environment. If you don't wish to upgrade yet, be sure to pin your module for the Python slackclient to `1.3.1`.

## Minimum Python versions
slackclient v2.x requires Python 3.6 (or higher). Support for Python 2.7 will maintained in the existing slackclient v1.x.

Client v1 Support Plan:
- Python 2 Timeline: Python 2.7 will continue to be supported in the 1.x version of the client until Dec 31st, 2019. After this time we will immediately end of life our support.
- New Slack features: We’ll continue to add support for any new Slack features that are released as they become available on the Platform. Support for Token Rotation is an example of a Slack feature.
- Client-specific features: We will NOT be adding any new client specific functionality to v1. Support for “asynchronous programming” is an example of of a client feature. Another example is storing additional data on the client.
- Bug and security fixes: We’ll be continuing to address bug fixes throughout the remaining lifetime of v1.
- Github Branching: `master` branch is used for v2 code. `v1` branch will be used for v1 code.

## Import changes
---
 The goal of this project is to provide a set of tools that ease the creation of Python Slack apps. To better align with this goal we’re renaming the main module to `slack`. From `slack` developers can import various tools. 
```Python
# Before:
# import slackclient

# After:
from slack import WebClient
```

## RTM API Changes:
---
An RTMClient allows apps to communicate with the Slack Platform's RTM API. This client allows you to simply link callbacks to their corresponding events. When an event occurs this client executes your callback while passing along any information it receives.

Example App in v1:
Here's a simple example app that replies "Hi <@userid>!" in a thread if you send it a message containing "Hello".
```Python
from slackclient import SlackClient

slack_token = os.environ["SLACK_API_TOKEN"]
client = SlackClient(slack_token)

def say_hello(data):
    if 'Hello' in data['text']:
        channel_id = data['channel']
        thread_ts = data['ts']
        user = data['user']

        client.api_call('chat.postMessage',
            channel=channel_id,
            text="Hi <@{}>!".format(user),
            thread_ts=thread_ts
        )

if client.rtm_connect():
    while client.server.connected is True:
        for data in client.rtm_read():
            if "type" in data and data["type"] == "message":
                say_hello(data)
else:
    print "Connection Failed"
```

Example App in v2:
Here's that same simple example app that replies "Hi <@userid>!" in a thread if you send it a message containing "Hello".
```Python
import slack

slack_token = os.environ["SLACK_API_TOKEN"]
rtmclient = slack.RTMClient(slack_token)

@slack.RTMClient.run_on(event='message')
def say_hello(**payload):
    data = payload['data']
    if 'Hello' in data['text']:
        channel_id = data['channel']
        thread_ts = data['ts']
        user = data['user']

        webclient = payload['web_client']
        webclient.chat_postMessage(
            channel=channel_id,
            text="Hi <@{}>!".format(user),
            thread_ts=thread_ts
        )

rtmclient.start()
```

**We no longer store any team data.**: In the current 1.x version of the client we store some channel and user information internally on [`Server.py`](https://github.com/slackapi/python-slackclient/blob/master/slackclient/server.py) in `client`. This data will now be available in the open event for consumption. Developers are then free to store any information they choose. Here's an example:
```Python
# Retrieving the team domain.
# Before:
# team_domain = client.server.login_data["team"]["domain"]

# After:
@slack.RTMClient.run_on(event='open')
def get_team_data(**payload):
    team_domain = payload['data']['team']['domain']
```

Since RTM usage has been completely redesigned please see the [README](#basic-usage-of-the-rtm-client) for a full breakdown of how to implement it.

## Web Client API Changes:
---
**Token refresh removed**: 

This feature originally shipped as a part of Workspace Tokens. Since we're [heading in a new direction](https://medium.com/slack-developer-blog/the-latest-with-app-tokens-fe878d44130c) it's safe to remove this, along with any related attributes stored on the client.
- ~refresh_token~
- ~token_update_callback~
- ~client_id~
- ~client_secret~

**`#api_call()`**:

- `timeout` param has been removed. Timeout is passed at the client level now.
- `kwargs` param has been removed. You must specify where the data you pass belongs in the request. e.g. 'data' vs 'params' vs 'files'...etc
```Python
# Before:
# from slackclient import SlackClient
#
# client = SlackClient(os.environ["SLACK_API_TOKEN"])
# client.api_call('chat.postMessage',
#     timeout=30,
#     channel='C0123456',
#     text="Hi!")

# After:

import slack

client = slack.WebClient(os.environ["SLACK_API_TOKEN"], timeout=30)
client.api_call('chat.postMessage', json={
    'channel': 'C0123456',
    'text': 'Hi!'})

# Note: That while the above is allowed, the more efficient way to call that API is like this:
client.chat_postMessage(
    channel='C0123456',
    text='Hi!')
```

The WebClient provides built-in methods for Slack's Web API. These methods act as helpers enabling you to focus less on how the request is constructed. Here are a few things that this mixin provides:
- Basic information about each method through the docstring.
- Easy File Uploads: You can now pass in the location of a file and the library will handle opening and retrieving the file object to be transmitted.
- Token type validation: This gives you better error messaging when you're attempting to consume an api method that your token doesn't have access to.
- Constructs requests using Slack's preferred HTTP methods and content-types.
