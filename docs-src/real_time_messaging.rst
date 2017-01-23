.. _real-time-messaging:

==============================================
Real Time Messaging
==============================================
The `Real Time Messaging API`_ is a WebSocket-based API that allows you to
receive events from Slack in real time and send messages as users.

If you prefer events to be pushed to you instead, we recommend using the
HTTP-based `Events API <https://api.slack.com/events-api>`_ instead.
Most event types supported by the RTM API are also available
in `the Events API <https://api.slack.com/events/api>`_.

See :ref:`Tokens & Authentication <handling-tokens>` for API token handling best practices.

Connecting to the Real Time Messaging API
------------------------------------------
::

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  if sc.rtm_connect():
      while True:
          print sc.rtm_read()
          time.sleep(1)
  else:
      print "Connection Failed, invalid token?"

If you connect successfully the first event received will be a hello:
::

  {
    u'type': u'hello'
  }

If there was a problem connecting an error will be returned, including a descriptive error message:
::

  {
    u'type': u'error',
      u'error': {
      u'code': 1,
      u'msg': u'Socket URL has expired'
    }
  }

RTM Events
-------------
::

  {
    u'type': u'message',
    u'ts': u'1358878749.000002',
    u'user': u'U023BECGF',
    u'text': u'Hello'
  }

See `RTM Events <https://api.slack.com/rtm#events>`_ for a complete list of events.

Sending messages via the RTM API
---------------------------------
You can send a message to Slack by sending JSON over the websocket connection.

::

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.rtm_send_message("welcome-test", "test")

You can send a message to a private group or direct message channel in the same
way, but using a Group ID (``C024BE91L``) or DM channel ID (``D024BE91L``).

You can send a message in reply to a thread using the ``thread`` argument, and
optionally broadcast that message back to the channel by setting
``reply_broadcast`` to ``True``.

::

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.rtm_send_message("welcome-test", "test", "1482960137.003543", True)

See `Threading messages <https://api.slack.com/docs/message-threading#threads_party>`_
for more details on using threads.

The RTM API only supports posting messages with `basic formatting <https://api.slack.com/docs/message-formatting>`_.
It does not support attachments or other message formatting modes.

 To post a more complex message as a user, see :ref:`Web API usage <web-api-examples>`.

.. include:: metadata.rst
