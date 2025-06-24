---
sidebar_label: Migrating from slackclient
---

# Migrating from v2.x to v3.x {#migrating}

You may still view the legacy `slackclient` v2 [documentation](/legacy/). However, the **slackclient** project is in maintenance mode and this **slack_sdk** project is the successor.

## From `slackclient` 2.x {#fromv2}

There are a few changes introduced in v3.0:

-   The PyPI project has been renamed from `slackclient` to `slack_sdk`.
-   Importing `slack_sdk.*` is recommended. You can still use `slack.*` with deprecation warnings.
-   `slack_sdk` has no required dependencies. This means `aiohttp` is no longer automatically resolved.
-   `WebClient` no longer has `run_async` and `aiohttp` specific options. If you still need the option or other `aiohttp` specific options, use `LegacyWebClient` (`slackclient` v2 compatible) or `AsyncWebClient`.

We're sorry for the inconvenience.

------------------------------------------------------------------------

**Change:** The PyPI project has been renamed from `slackclient` to `slack_sdk`.

**Action**: Remove `slackclient`, add `slack_sdk` in `requirements.txt`.

Since v3, the PyPI project name is [slack_sdk](https://pypi.org/project/slack_sdk/) (technically `slack-sdk` also works).

The biggest reason for the renaming is the feature coverage in v3 and newer. The SDK v3 provides not only API clients, but also other modules. As the first step, it starts supporting OAuth flow out-of-the-box. The secondary reason is to make the names more consistent. The renaming addresses the long-lived confusion between the PyPI project and package names.

------------------------------------------------------------------------

**Change:** Importing `slack_sdk.*` is recommended. You can still use `slack.*` with deprecation warnings.

**Action**: Replace `from slack import`, `import slack`, etc. in your source code.

Most imports can be simply replaced by `find your_app -name '*.py' | xargs sed -i '' 's/from slack /from slack_sdk /g'` or similar. If you use `slack.web.classes.*`, the conversion is not so simple that we recommend manually replacing imports for those.

That said, all existing code can be migrated to v3 without any code changes. If you don't have time for it, you can use the `slack` package with deprecation warnings saying `UserWarning: slack package is deprecated. Please use slack_sdk.web/webhook/rtm package instead. For more info, go to https://tools slack.dev/python-slack-sdk/v3-migration/` for a while.

------------------------------------------------------------------------

**Change:** `slack_sdk` has no required dependencies. This means `aiohttp` is no longer automatically resolved.

**Action**: Add `aiohttp` to `requirements.txt` if you use any of `AsyncWebClient`, `AsyncWebhookClient`, and `LegacyWebClient`.

If you use some modules that require `aiohttp`, your `requirements.txt` needs to explicitly list `aiohttp`. The `slack_sdk` dependency doesn't resolve it for you, unlike `slackclient` v2.

------------------------------------------------------------------------

**Change:** `WebClient` no longer has `run_async` and `aiohttp` specific options.

**Action:** If you still need the option or other `aiohttp` specific options, use `LegacyWebClient` (`slackclient` v2 compatible) or `AsyncWebClient`.

The new `slack_sdk.web.WebClient` doesn't rely on `aiohttp` internally at all. The class provides only the synchronous way to call Web APIs. If you need a v2 compatible one, you can use `LegacyWebClient`. Apart from the name, there is no breaking change in the class.

If you're using `run_async=True` option, we highly recommend switching to `AsyncWebClient`. `AsyncWebClient` is a straight-forward async HTTP client. You can expect the class properly works in the nature of `async/await` provided by the standard `asyncio` library.

---

## Migration from v1.x to v2.x {#fromv1}

If you're migrating from v1.x of `slackclient` to v2.x, here's what you need to change to ensure your app continues working after updating.

:::info[We have completely rewritten this library and you should only upgrade once you have fully tested it in your development environment.] 

If you don't wish to upgrade yet, be sure to pin your module for the Python `slackclient` to `1.3.1`.

:::

### Minimum Python versions {#minimum-versions}

`slackclient` v2.x requires Python 3.6 (or higher). Support for Python 2.7 is maintained in the existing `slackclient` v1.x.

Client v1 support:
- Python 2: Python 2.7 was supported in the 1.x version of the client up until Dec 31st, 2019.
- We’ll continue to add support for any new Slack features that are released as they become available on the platform. Support for token rotation is an example of a Slack feature.
- We will no longer be adding any new client-specific functionality to v1. Support for “asynchronous programming” is an example of a client feature. Another example is storing additional data on the client.
- We are no longer addressing bug or security fixes.
- Github branching: The `master` branch is used for v2 code. The `v1` branch is used for v1 code.

### Import changes {#import-changes}

 The goal of this project is to provide a set of tools that ease the creation of Python Slack apps. To better align with this goal, we’re renaming the main module to `slack`. From `slack`, developers can import various tools. 

```Python
# Before:
# import slackclient

# After:
from slack import WebClient
```

### RTM API changes {#RTM-changes}

An RTMClient allows apps to communicate with the Slack platform's Legacy RTM API. This client allows you to link callbacks to their corresponding events. When an event occurs, this client executes your callback while passing along any information it receives.

Example app in v1:

Here's a simple example app that replies "Hi \<@userid\>!" in a thread if you send it a message containing "Hello".

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

Here's that same example app that replies "Hi \<\@userid\>!" in a thread if you send it a message containing "Hello".

```Python
import slack

slack_token = os.environ["SLACK_API_TOKEN"]
rtmclient = slack.RTMClient(token=slack_token)

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

**We no longer store any team data.** In the current 1.x version of the client, we store some channel and user information internally on [`Server.py`](https://github.com/slackapi/python-slackclient/blob/master/slackclient/server.py) in `client`. This data will now be available in the open event for consumption. Developers are then free to store any information they choose. Here's an example:

```Python
# Retrieving the team domain.
# Before:
# team_domain = client.server.login_data["team"]["domain"]

# After:
@slack.RTMClient.run_on(event='open')
def get_team_data(**payload):
    team_domain = payload['data']['team']['domain']
```

RTM usage has been completely redesigned.

For new projects, we recommend using [Events API](https://docs.slack.dev/apis/events-api). This package `slackclient` v2 doesn't have any supports for Events API but you can try https://github.com/slackapi/python-slack-events-api that works as an enhancement of Flask web framework.

In the near future, we'll be providing better supports for Events API in the official SDK.

### Web Client API changes {#web-client-changes}

**Token refresh removed**: 

This feature originally shipped as a part of workspace tokens. Since we've [gone in a new direction](https://medium.com/slack-developer-blog/the-latest-with-app-tokens-fe878d44130c) it's safe to remove this along with any related attributes stored on the client.

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

The WebClient provides built-in methods for the Slack Web API. These methods act as helpers, enabling you to focus less on how the request is constructed. Here are a few things this provides:

- Basic information about each method through the docstring.
- Easy file uploads: You can pass in the location of a file and the library will handle opening and retrieving the file object to be transmitted.
- Token type validation: This gives you better error messaging when you're attempting to consume an API method your token doesn't have access to.
- Constructs requests using Slack preferred HTTP methods and content-types.

### Error handling changes {#error-handling-changes}

In version 1.x, a failed API call would return the error payload to you and expect you to handle the error. In version 2.x, a failed API call will throw an exception. To handle this in your code, you will have to wrap API calls with a `try except` block.
