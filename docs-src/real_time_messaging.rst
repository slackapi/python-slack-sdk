.. _real-time-messaging:

==============================================
Real Time Messaging (RTM)
==============================================
The `Real Time Messaging (RTM) API`_ is a WebSocket-based API that allows you to receive events from Slack in real time and send messages as users.

If you prefer events to be pushed to your app, we recommend using the HTTP-based `Events API <https://api.slack.com/events-api>`_ instead. 
The Events API contains some events that aren't supported in the RTM API (like `app_home_opened event <https://api.slack.com/events/app_home_opened>`_),
and it supports most of the event types in the RTM API. If you'd like to use the Events API, you can use the `Python Slack Events Adaptor <https://github.com/slackapi/python-slack-events-api>`_.

The RTMClient allows apps to communicate with the Slack Platform's RTM API.

The event-driven architecture of this client allows you to simply link callbacks to their corresponding events. When an event occurs this client executes your callback while passing along any information it receives. We also give you the ability to call our web client from inside your callbacks.

In our example below, we watch for a `message event <https://api.slack.com/events/message>`_ that contains "Hello" and if its received, we call the ``say_hello()`` function. We then issue a call to the web client to post back to the channel saying "Hi" to the user.

Configuring the RTM API
------------------------------------------

Events using the RTM API **must** use a classic Slack app (with a plain ``bot`` scope).

If you already have a classic Slack app, you can use those credentials. If you don't and need to use the RTM API, you can `create a classic Slack app <https://api.slack.com/apps?new_classic_app=1>`_. You can learn more in the `API documentation <https://api.slack.com/authentication/basics#soon>`_.

Also, even if the Slack app configuration pages encourage you to upgrade to the newer permission model, don't upgrade it and keep using the "classic" bot permission.

Connecting to the RTM API
------------------------------------------

.. code-block:: python

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

rtm.start vs rtm.connect
---------------------------

By default, the RTM client uses ``rtm.connect`` to establish a WebSocket connection with Slack. The response contains basic information about the team and WebSocket url.

If you'd rather use ``rtm.start`` to establish the connection, which provides more information about the conversations and users on the team, you can set the ``connect_method`` option to ``rtm.start`` when instantiating the RTM Client. Note that on larger teams, use of ``rtm.start`` can be slow and unreliable.

.. code-block:: python

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

Read the `rtm.connect docs <https://api.slack.com/methods/rtm.connect>`_ and the `rtm.start docs <https://api.slack.com/methods/rtm.start>`_ for more details.


RTM Events
-------------
.. code-block:: javascript

  {
    'type': 'message',
    'ts': '1358878749.000002',
    'user': 'U023BECGF',
    'text': 'Hello'
  }

See `RTM Events <https://api.slack.com/rtm#events>`_ for a complete list of events.

.. include:: metadata.rst
