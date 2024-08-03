
.. _real-time-messaging:

==============================================
RTM Client
==============================================

Real Time Messaging (RTM)
---------------------------------------

.. parsed-literal ::
   **rtm.start method has been deprecated for apps created after Nov 30th, 2021.** See details `here <https://api.slack.com/changelog/2021-10-rtm-start-to-stop>`_

The `Real Time Messaging (RTM) API`_ is a WebSocket-based API that allows you to receive events from Slack in real time and send messages as users.

If you prefer events to be pushed to your app, we recommend using the HTTP-based `Events API <https://api.slack.com/events-api>`_ along with `Socket Mode <https://api.slack.com/socket-mode>`_ instead. The Events API contains some events that aren't supported in the RTM API (like `app_home_opened event <https://api.slack.com/events/app_home_opened>`_), and it supports most of the event types in the RTM API. If you'd like to use the Events API, you can use the `Python Slack Events Adaptor <https://github.com/slackapi/python-slack-events-api>`_.

The RTMClient allows apps to communicate with the Slack Platform's RTM API.

The event-driven architecture of this client allows you to simply link callbacks to their corresponding events. When an event occurs this client executes your callback while passing along any information it receives. We also give you the ability to call our web client from inside your callbacks.

In our example below, we watch for a `message event <https://api.slack.com/events/message>`_ that contains "Hello" and if its received, we call the ``say_hello()`` function. We then issue a call to the web client to post back to the channel saying "Hi" to the user.

**Configuring the RTM API**

Events using the RTM API **must** use a classic Slack app (with a plain ``bot`` scope).

If you already have a classic Slack app, you can use those credentials. If you don't and need to use the RTM API, you can `create a classic Slack app <https://api.slack.com/apps?new_classic_app=1>`_. You can learn more in the `API documentation <https://api.slack.com/authentication/basics#soon>`_.

Also, even if the Slack app configuration pages encourage you to upgrade to the newer permission model, don't upgrade it and keep using the "classic" bot permission.

**Connecting to the RTM API**

Note that the import here is not ``from slack_sdk.rtm import RTMClient`` but ``from slack_sdk.rtm_v2 import RTMClient`` (``_v2`` is added in the latter one). If you would like to use the legacy version of the client, go to the next section.

.. code-block:: python

    import os
    from slack_sdk.rtm_v2 import RTMClient

    rtm = RTMClient(token=os.environ["SLACK_BOT_TOKEN"])

    @rtm.on("message")
    def handle(client: RTMClient, event: dict):
        if 'Hello' in event['text']:
            channel_id = event['channel']
            thread_ts = event['ts']
            user = event['user'] # This is not username but user ID (the format is either U*** or W***)

            client.web_client.chat_postMessage(
                channel=channel_id,
                text=f"Hi <@{user}>!",
                thread_ts=thread_ts
            )

    rtm.start()


**Connecting to the RTM API (v1 client)**

Below is a code snippet that uses the legacy version of ``RTMClient``. For new app development, we **do not recommend** using it as it contains issues that have been resolved in v2. Please refer to the `list of these issues <https://github.com/slackapi/python-slack-sdk/issues?q=is%3Aissue+is%3Aclosed+milestone%3A3.3.0+label%3Artm-client>`_ for more details.

.. code-block:: python

    import os
    from slack_sdk.rtm import RTMClient

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

    slack_token = os.environ["SLACK_BOT_TOKEN"]
    rtm_client = RTMClient(token=slack_token)
    rtm_client.start()

**rtm.start vs rtm.connect (v1 client)**

.. parsed-literal ::
   **rtm.start method has been deprecated for apps created after Nov 30th, 2021.** See details `here <https://api.slack.com/changelog/2021-10-rtm-start-to-stop>`_

By default, the RTM client uses ``rtm.connect`` to establish a WebSocket connection with Slack. The response contains basic information about the team and WebSocket url.

Read the `rtm.connect docs <https://api.slack.com/methods/rtm.connect>`_ and the `rtm.start docs <https://api.slack.com/methods/rtm.start>`_ for more details. Also, note that ``slack.rtm_v2.RTMClient`` does not support ``rtm.start``.

**RTM Events**

.. code-block:: javascript

    {
        'type': 'message',
        'ts': '1358878749.000002',
        'user': 'U023BECGF',
        'text': 'Hello'
    }

See `RTM Events <https://api.slack.com/rtm#events>`_ for a complete list of events.

.. include:: metadata.rst
