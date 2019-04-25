# Migrating to 2.x
**Import changes**: The goal of this project is to provide a set of tools that ease the creation of Python Slack apps. To better align with this goal we’re renaming the main module to `slack`. From `slack` developers can import various tools. 
```Python
# Before:
# import slackclient

# After:
from slack import WebClient
```
#### RTM Client API Changes:
The RTM client has been completely redesigned please refer above for the new API.

**We no longer store any team data.**: In the current 1.x version of the client we store some channel and user information internally on [`Server.py`](https://github.com/slackapi/python-slackclient/blob/master/slackclient/server.py) in `client`. This data will now be available in the open event for consumption. Developers are then free to store any information they choose. Here's an example:
```Python
# Retrieving the team domain.
# Before:
# team_domain = client.server.login_data["team"]["domain"]

# After:
def get_team_data(data):
    team_domain = data['team']['domain']
rtm_client.on(event='open', callback=get_team_data)
```

#### Web Client API Changes:
**Token refresh removed**: This feature originally shipped as a part of Workspace Tokens. Since we're [heading in a new direction](https://medium.com/slack-developer-blog/the-latest-with-app-tokens-fe878d44130c) it's safe to remove this, along with any related attributes stored on the client.
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

# Note: The SlackAPIMixin allows you to write it like this.
client.chat_postMessage(
    channel='C0123456',
    text='Hi!')
```

**SlackAPIMixin**: The Slack API mixin provides built-in methods for Slack's Web API. These methods act as helpers enabling you to focus less on how the request is constructed. Here are a few things that this mixin provides:
- Basic information about each method through the docstring.
- Easy File Uploads: You can now pass in the location of a file and the library will handle opening and retrieving the file object to be transmitted.
- Token type validation: This gives you better error messaging when you're attempting to consume an api method that your token doesn't have access to.
- Constructs requests using Slack's preferred HTTP methods and content-types.