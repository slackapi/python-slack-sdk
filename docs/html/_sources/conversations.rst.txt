.. _conversations_api:

==============================================
Conversations API
==============================================
The Slack Conversations API provides your app with a unified interface to work with all the
channel-like things encountered in Slack; public channels, private channels, direct messages, group
direct messages, and our newest channel type, Shared Channels.


See `Conversations API <https://api.slack.com/docs/conversations-api>`_ docs for more info.

--------

Creating a direct message or multi-person direct message
---------------------------------------------------------
This Conversations API method opens a multi-person direct message or just a 1:1 direct message.

*Use conversations.create for public or private channels.*

Provide 1 to 8 user IDs in the ``user`` parameter to open or resume a conversation. Providing only
1 ID will create a direct message. Providing more will create an ``mpim``.

If there are no conversations already in progress including that exact set of members, a new
multi-person direct message conversation begins.

Subsequent calls to ``conversations.open`` with the same set of users will return the already
existing conversation.


.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "conversations.open",
    users=["W1234567890","U2345678901","U3456789012"]
  )

See `conversations.open <https://api.slack.com/methods/conversations.open>`_ additional info.

--------

Creating a public or private channel
-------------------------------------
Initiates a public or private channel-based conversation

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "conversations.create",
    name="myprivatechannel",
    is_private=True
  )

See `conversations.create <https://api.slack.com/methods/conversations.create>`_ additional info.

--------

Getting information about a conversation
-----------------------------------------
This Conversations API method returns information about a workspace conversation.

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "conversations.info",
    channel="C0XXXXXX",
  )

See `conversations.info <https://api.slack.com/methods/conversations.info>`_ for more info.


--------

Getting a list of conversations
--------------------------------
This Conversations API method returns a list of all channel-like conversations in a workspace.
The "channels" returned depend on what the calling token has access to and the directives placed
in the ``types`` parameter.


.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call("conversations.list")

Only public conversations are included by default. You may include additional conversations types
by passing ``types`` (as a string) into your list request. Additional conversation types include
``public_channel`` and ``private_channel``.


.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  # Note that `types` is a string
  sc.api_call(
    "conversations.list",
    types="public_channel, private_channel"
  )

See `conversations.list <https://api.slack.com/methods/conversations.list>`_ for more info.


--------

Leaving a conversation
-----------------------
Maybe you've finished up all the business you had in a conversation, or maybe you
joined one by accident. This is how you leave a conversation.

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "conversations.leave",
    channel="C0XXXXXXX"
  )

See `conversations.leave <https://api.slack.com/methods/conversations.leave>`_ for more info.

--------

Get conversation members
------------------------------
Get a list fo the members of a conversation

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call("conversations.members",
    channel="C0XXXXXXX"
  )

See `users.list <https://api.slack.com/methods/conversations.members>`_ for more info.

.. include:: metadata.rst
