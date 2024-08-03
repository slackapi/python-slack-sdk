==============================================
Socket Mode Client
==============================================

Socket Mode is a method of connecting your app to Slack’s APIs using WebSockets instead of HTTP. You can use  ``slack_sdk.socket_mode.SocketModeClient`` for managing `Socket Mode <https://api.slack.com/apis/connections/socket>`_ connections and performing interactions with Slack.

The Python document for this module is available at https://slack.dev/python-slack-sdk/api-docs/slack_sdk/

SocketModeClient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First off, let's start with enabling Socket Mode. Visit `the Slack App configuration page <http://api.slack.com/apps>`_, choose the app you're working on, and go to **Settings** on the left pane. There are a few things to do on the page.

* Go to **Settings** > **Basic Information**, then add a new **App-Level Token** with the `connections:write` scope
* Go to **Settings** > **Socket Mode**, then turn on **Enable Socket Mode**
* Go to **Features** > **App Home**, look under **Show Tabs** > **Messages Tab** then turn on **Allow users to send Slash commands and messages from the messages tab**
* Go to **Features** > **Event Subscriptions**, then turn on **Enable Events**

    * On the same page expand **Subscribe to bot events** click **Add Bot User Event** and select **message.im**

        * This will allow the bot to get events for messages that are sent in 1:1 direct messages with itself
* Go to **Features** > **Interactivity and Shortcuts**, look under *Shortcuts** click **Create a New Shortcut** then create a new Global shortcut with the following details

    * **Name**: Hello
    * **Short Description**: Receive a Greeting
    * **Callback ID**: hello-shortcut
* Go to **Features** > **OAuth & Permissions** under **Scopes** > **Bot Token Scopes** click **Add an OAuth Scope** and select **reactions:write**

    * This will allow the bot to add emoji reactions (Reacji's) to messages
* Go to **Features** > **Oauth & Permissions** under **OAuth Tokens for Your Workspace** click **Install to Workspace**

You will be using the app-level token that starts with ``xapp-`` prefix. Note that the token here is not the ones starting with either ``xoxb-`` or ``xoxp-``.

.. code-block:: python

    import os
    from slack_sdk.web import WebClient
    from slack_sdk.socket_mode import SocketModeClient

    # Initialize SocketModeClient with an app-level token + WebClient
    client = SocketModeClient(
        # This app-level token will be used only for establishing a connection
        app_token=os.environ.get("SLACK_APP_TOKEN"),  # xapp-A111-222-xyz
        # You will be using this WebClient for performing Web API calls in listeners
        web_client=WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))  # xoxb-111-222-xyz
    )

    from slack_sdk.socket_mode.response import SocketModeResponse
    from slack_sdk.socket_mode.request import SocketModeRequest

    def process(client: SocketModeClient, req: SocketModeRequest):
        if req.type == "events_api":
            # Acknowledge the request anyway
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)

            # Add a reaction to the message if it's a new message
            if req.payload["event"]["type"] == "message" \
                and req.payload["event"].get("subtype") is None:
                client.web_client.reactions_add(
                    name="eyes",
                    channel=req.payload["event"]["channel"],
                    timestamp=req.payload["event"]["ts"],
                )
        if req.type == "interactive" \
            and req.payload.get("type") == "shortcut":
            if req.payload["callback_id"] == "hello-shortcut":
                # Acknowledge the request
                response = SocketModeResponse(envelope_id=req.envelope_id)
                client.send_socket_mode_response(response)
                # Open a welcome modal
                client.web_client.views_open(
                    trigger_id=req.payload["trigger_id"],
                    view={
                        "type": "modal",
                        "callback_id": "hello-modal",
                        "title": {
                            "type": "plain_text",
                            "text": "Greetings!"
                        },
                        "submit": {
                            "type": "plain_text",
                            "text": "Good Bye"
                        },
                        "blocks": [
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "Hello!"
                                }
                            }
                        ]
                    }
                )

        if req.type == "interactive" \
            and req.payload.get("type") == "view_submission":
            if req.payload["view"]["callback_id"] == "hello-modal":
                # Acknowledge the request and close the modal
                response = SocketModeResponse(envelope_id=req.envelope_id)
                client.send_socket_mode_response(response)

    # Add a new listener to receive messages from Slack
    # You can add more listeners like this
    client.socket_mode_request_listeners.append(process)
    # Establish a WebSocket connection to the Socket Mode servers
    client.connect()
    # Just not to stop this process
    from threading import Event
    Event().wait()

--------

Supported Libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This SDK offers its own simple WebSocket client covering only required features for Socket Mode. In addition to that, ``SocketModeClient`` is implemented with a few 3rd party open-source libraries. If you prefer any of the following, you can use it over the built-in one.

.. list-table::
   :header-rows: 1

   * - PyPI Project
     - SocketModeClient
   * - `slack_sdk <https://pypi.org/project/slack-sdk/>`_
     - `slack_sdk.socket_mode.SocketModeClient <https://github.com/slackapi/python-slack-sdk/blob/main/slack_sdk/socket_mode/builtin>`_
   * - `websocket_client <https://pypi.org/project/websocket_client/>`_
     - `slack_sdk.socket_mode.websocket_client.SocketModeClient <https://github.com/slackapi/python-slack-sdk/blob/main/slack_sdk/socket_mode/websocket_client>`_
   * - `aiohttp <https://pypi.org/project/aiohttp/>`_ (asyncio-based)
     - `slack_sdk.socket_mode.aiohttp.SocketModeClient <https://github.com/slackapi/python-slack-sdk/blob/main/slack_sdk/socket_mode/aiohttp>`_
   * - `websockets <https://pypi.org/project/websockets/>`_ (asyncio-based)
     - `slack_sdk.socket_mode.websockets.SocketModeClient <https://github.com/slackapi/python-slack-sdk/blob/main/slack_sdk/socket_mode/websockets>`_


To use the `websocket_client <https://pypi.org/project/websocket_client/>`_ based one, all you need to do are to add `websocket_client <https://pypi.org/project/websocket_client/>`_ dependency and to change the import as below.

.. code-block:: python

    # Note that the pockage is different
    from slack_sdk.socket_mode.websocket_client import SocketModeClient

    client = SocketModeClient(
        app_token=os.environ.get("SLACK_APP_TOKEN"),  # xapp-A111-222-xyz
        web_client=WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))  # xoxb-111-222-xyz
    )

You can pass a few additional arguments that are specific to the library. Apart from that, all the functionalities work in the same way with the built-in version.

--------

Asyncio Based Libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To use the asyncio-based ones such as aiohttp, your app needs to be compatible with asyncio's async/await programming model. The `SocketModeClient` only works with `AsyncWebClient` and async listeners.

.. code-block:: python

    import asyncio
    import os
    from slack_sdk.web.async_client import AsyncWebClient
    from slack_sdk.socket_mode.aiohttp import SocketModeClient

    # Use async method
    async def main():
        from slack_sdk.socket_mode.response import SocketModeResponse
        from slack_sdk.socket_mode.request import SocketModeRequest

        # Initialize SocketModeClient with an app-level token + AsyncWebClient
        client = SocketModeClient(
            # This app-level token will be used only for establishing a connection
            app_token=os.environ.get("SLACK_APP_TOKEN"),  # xapp-A111-222-xyz
            # You will be using this AsyncWebClient for performing Web API calls in listeners
            web_client=AsyncWebClient(token=os.environ.get("SLACK_BOT_TOKEN"))  # xoxb-111-222-xyz
        )

        # Use async method
        async def process(client: SocketModeClient, req: SocketModeRequest):
            if req.type == "events_api":
                # Acknowledge the request anyway
                response = SocketModeResponse(envelope_id=req.envelope_id)
                # Don't forget having await for method calls
                await client.send_socket_mode_response(response)

                # Add a reaction to the message if it's a new message
                if req.payload["event"]["type"] == "message" \
                    and req.payload["event"].get("subtype") is None:
                    await client.web_client.reactions_add(
                        name="eyes",
                        channel=req.payload["event"]["channel"],
                        timestamp=req.payload["event"]["ts"],
                    )
            if req.type == "interactive" \
                and req.payload.get("type") == "shortcut":
                if req.payload["callback_id"] == "hello-shortcut":
                    # Acknowledge the request
                    response = SocketModeResponse(envelope_id=req.envelope_id)
                    await client.send_socket_mode_response(response)
                    # Open a welcome modal
                    await client.web_client.views_open(
                        trigger_id=req.payload["trigger_id"],
                        view={
                            "type": "modal",
                            "callback_id": "hello-modal",
                            "title": {
                                "type": "plain_text",
                                "text": "Greetings!"
                            },
                            "submit": {
                                "type": "plain_text",
                                "text": "Good Bye"
                            },
                            "blocks": [
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "Hello!"
                                    }
                                }
                            ]
                        }
                    )

            if req.type == "interactive" \
                and req.payload.get("type") == "view_submission":
                if req.payload["view"]["callback_id"] == "hello-modal":
                    # Acknowledge the request and close the modal
                    response = SocketModeResponse(envelope_id=req.envelope_id)
                    await client.send_socket_mode_response(response)

        # Add a new listener to receive messages from Slack
        # You can add more listeners like this
        client.socket_mode_request_listeners.append(process)
        # Establish a WebSocket connection to the Socket Mode servers
        await client.connect()
        # Just not to stop this process
        await asyncio.sleep(float("inf"))

    # You can go with other way to run it. This is just for easiness to try it out.
    asyncio.run(main())

.. include:: ../metadata.rst
