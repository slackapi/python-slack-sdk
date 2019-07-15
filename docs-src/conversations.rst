.. _conversations_api:

==============================================
Conversations API
==============================================
The Slack Conversations API provides your app with a unified interface to work with all the channel-like things encountered in Slack; public channels, private channels, direct messages, group direct messages, and our newest channel type, Shared Channels.


See `Conversations API <https://api.slack.com/docs/conversations-api>`_ docs for more info.

--------

Direct messages
---------------------------------------------------------
The ``conversations_open`` method opens either a 1:1 direct message with a single user or a a multi-person direct message, depending on the number of users supplied to the ``users`` parameter.

*For public or private channels, use the  ``conversations_create`` method.*

Provide a ``users`` parameter as an array with 1 to 8 user IDs to open or resume a conversation. Providing only 1 ID will create a direct message. Providing more will create a new multi-party DM or resume an existing conversation.

Subsequent calls to ``conversations_open`` with the same set of users will return the already existing conversation.

.. code-block:: python

  import slack

  slack_token = os.environ["SLACK_API_TOKEN"]
  client = slack.WebClient(slack_token)

  client.conversations_open(users=["W123456789", "U987654321"])

See `conversations.open <https://api.slack.com/methods/conversations.open>`_ additional info.

--------

Creating channels
-------------------------------------
Creates a new channel, either public or private. The ``name`` parameter is required, may contain numbers, letters, hyphens, and underscores, and must contain fewer than 21 characters. To make the channel private, set the option ``is_private`` parameter to ``True``.

.. code-block:: python

  import slack

  slack_token = os.environ["SLACK_API_TOKEN"]
  client = slack.WebClient(slack_token)

  client.conversations_create(
    name="my-private-channel",
    is_private = True
  )

See `conversations.create <https://api.slack.com/methods/conversations.create>`_ additional info.

--------

Getting more information
-----------------------------------------
To retrieve a set of metadata about a channel (public, private, DM, or multi-party DM), use ``conversations_info``. The ``channel`` parameter is required and must be a valid channel ID. The optional ``include_locale`` boolean parameter will return locale data, which may be useful if you wish to return localized responses. The ``include_num_members`` boolean parameter will return the number of people in a channel.

.. code-block:: python

  import slack

  slack_token = os.environ["SLACK_API_TOKEN"]
  client = slack.WebClient(slack_token)

  client.conversations_info(
    channel="C031415926"
    include_num_members = True
  )

See `conversations.info <https://api.slack.com/methods/conversations.info>`_ for more info.


--------

Listing conversations
--------------------------------
To get a list of all the conversations in a workspace, use ``conversations_list``. By default, only public conversations are returned; use the ``types`` parameter specify which types of conversations you're interested in (Note: ``types`` is a string of comma-separated values)


.. code-block:: python

  import slack

  slack_token = os.environ["SLACK_API_TOKEN"]
  client = slack.WebClient(slack_token)

  client.conversations_list()

Use the ``types`` parameter to request additional channels, including ``public_channel``, ``private_channel``, ``mpim``, and ``im``. This parameter is a string of comma-separated values.

.. code-block:: python

  import slack

  slack_token = os.environ["SLACK_API_TOKEN"]
  client = slack.WebClient(slack_token)

  client.conversations_list(
    types="public_channels, private_channels"
  )

See `conversations.list <https://api.slack.com/methods/conversations.list>`_ for more info.


--------

Leaving a conversation
-----------------------
To leave a conversation, use ``conversations_leave`` with the required ``channel`` param containing the ID of the channel to leave.

.. code-block:: python

  import slack

  slack_token = os.environ["SLACK_API_TOKEN"]
  client = slack.WebClient(slack_token)

  client.conversations_leave(channel="C27182818")

See `conversations.leave <https://api.slack.com/methods/conversations.leave>`_ for more info.

--------

Getting members
------------------------------
To get a list of the members of a conversation, use ``conversations_members`` with the required ``channel`` parameter.

.. code-block:: python

  import slack

  slack_token = os.environ["SLACK_API_TOKEN"]
  client = slack.WebClient(slack_token)

  client.conversations_members(channel="C16180339")

See `conversations.members <https://api.slack.com/methods/conversations.members>`_ for more info.

.. include:: metadata.rst
