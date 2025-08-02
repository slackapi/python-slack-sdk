# Real Time Messaging (RTM)

:::danger[The [`slackclient`](https://pypi.org/project/slackclient/) PyPI project is in maintenance mode and the [slack-sdk](https://pypi.org/project/slack-sdk/) project is its successor.] 

The v3 SDK provides additional features such as Socket Mode, OAuth flow, SCIM API, Audit Logs API, better async support, retry handlers, and more.

:::

The [Legacy Real Time Messaging (RTM) API](/legacy/legacy-rtm-api) is a WebSocket-based API that allows you to receive events from Slack in real time and to send messages as users. 

If you prefer events to be pushed to your app, we recommend using the HTTP-based [Events API](/apis/events-api) instead. The Events API contains some events that aren't supported in the Legacy RTM API (such as the [app_home_opened event](/reference/events/app_home_opened)), and it supports most of the event types in the Legacy RTM API. If you'd like to use the Events API, you can use the [Python Slack Events Adaptor](https://github.com/slackapi/python-slack-events-api).

The RTMClient allows apps to communicate with the Legacy RTM API.

The event-driven architecture of this client allows you to simply link callbacks to their corresponding events. When an event occurs, this client executes your callback while passing along any information it receives. We also give you the ability to call our web client from inside your callbacks.

In our example below, we watch for a [message event](/reference/events/message) that contains \"Hello\" and if it's received, we call the `say_hello()` function. We then issue a call to the web client to post back to the channel saying \"Hi\" to the user.

## Configuring the RTM API {#configuration}

Events using the Legacy RTM API **must** use a Slack app with a plain `bot` scope.

If you already have a Slack app with a plain `bot` scope, you can use those credentials. If you don't and need to use the Legacy RTM API, you can create a Slack app [here](https://api.slack.com/apps?new_classic_app=1). Even if the Slack app configuration pages encourage you to upgrade to a newer permission model, don't upgrade it and continue using the \"classic\" bot permission.

## Connecting to the RTM API {#connecting}

``` python
import os
from slack import RTMClient

@RTMClient.run_on(event="message")
def say_hello(**payload):
  data = payload['data']
  web_client = payload['web_client']

  if 'Hello' in data['text']:
    channel_id = data['channel']
    thread_ts = data['ts']
    user = data['user'] # This is not username but user ID (the format is either U*** or W***)

    web_client.chat_postMessage(
      channel=channel_id,
      text=f"Hi <@{user}>!",
      thread_ts=thread_ts
    )

slack_token = os.environ["SLACK_API_TOKEN"]
rtm_client = RTMClient(token=slack_token)
rtm_client.start()
```

## The `rtm.start` vs. `rtm.connect` API methods {#rtm-methods}

By default, the RTM client uses the [`rtm.connect`](/reference/methods/rtm.connect) API method to establish a WebSocket connection with Slack. The response contains basic information about the team and WebSocket URL.

If you'd rather use the [`rtm.start`](/reference/methods/rtm.start) API method to establish the connection, which provides more information about the conversations and users on the team, you can set the `connect_method` option to `rtm.start` when instantiating the RTM Client. Note that on larger teams, use of `rtm.start` can be slow and unreliable.

``` python
import os
from slack import RTMClient

@RTMClient.run_on(event="message")
def say_hello(**payload):
  data = payload['data']
  web_client = payload['web_client']
  if 'text' in data and 'Hello' in data['text']:
    channel_id = data['channel']
    thread_ts = data['ts']
    user = data['user'] # This is not username but user ID (the format is either U*** or W***)

    web_client.chat_postMessage(
      channel=channel_id,
      text=f"Hi <@{user}>!",
      thread_ts=thread_ts
    )

slack_token = os.environ["SLACK_API_TOKEN"]
rtm_client = RTMClient(
  token=slack_token,
  connect_method='rtm.start'
)
rtm_client.start()
```

See the [`rtm.connect`](/reference/methods/rtm.connect) and [`rtm.start`](/reference/methods/rtm.start) API methods for more details.

## RTM events {#rtm-events}

``` javascript
{
  'type': 'message',
  'ts': '1358878749.000002',
  'user': 'U023BECGF',
  'text': 'Hello'
}
```

Refer to the [Legacy RTM API](/legacy/legacy-rtm-api) page for more information.
