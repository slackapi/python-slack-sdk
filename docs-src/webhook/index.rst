==============================================
Webhook Client
==============================================

You can use ``slack_sdk.webhook.WebhookClient`` for `Incoming Webhooks <https://api.slack.com/messaging/webhooks>`_ and message responses using `response_url in payloads <https://api.slack.com/interactivity/handling#message_responses>`_.

Incoming Webhooks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To use `Incoming Webhooks <https://api.slack.com/messaging/webhooks>`_, just calling ``WebhookClient(url)#send(payload)`` method works for you. The call posts a message in a channel associated with the webhook URL.

.. code-block:: python

    from slack_sdk.webhook import WebhookClient
    url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
    webhook = WebhookClient(url)

    response = webhook.send(text="Hello!")
    assert response.status_code == 200
    assert response.body == "ok"

It's also possible to use ``blocks``, richer message using `Block Kit <https://api.slack.com/block-kit>`_.

.. code-block:: python

    from slack_sdk.webhook import WebhookClient
    url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
    webhook = WebhookClient(url)
    response = webhook.send(
        text="fallback",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "You have a new request:\n*<fakeLink.toEmployeeProfile.com|Fred Enriquez - New device request>*"
                }
            }
        ]
    )


response_url
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

User actions in channels generates a `response_url <https://api.slack.com/interactivity/handling#message_responses>`_ and includes the URL in its payload. You can use ``WebhookClient`` to send a message via the ``response_url``.

.. code-block:: python

    import os
    from slack_sdk.signature import SignatureVerifier
    signature_verifier = SignatureVerifier(
        signing_secret=os.environ["SLACK_SIGNING_SECRET"]
    )

    from slack_sdk.webhook import WebhookClient

    from flask import Flask, request, make_response
    app = Flask(__name__)

    @app.route("/slack/events", methods=["POST"])
    def slack_app():
        # Verify incoming requests from Slack
        # https://api.slack.com/authentication/verifying-requests-from-slack
        if not signature_verifier.is_valid(
            body=request.get_data(),
            timestamp=request.headers.get("X-Slack-Request-Timestamp"),
            signature=request.headers.get("X-Slack-Signature")):
            return make_response("invalid request", 403)

        # Handle a slash command invocation
        if "command" in request.form \
            and request.form["command"] == "/reply-this":
            response_url = request.form["response_url"]
            text = request.form["text"]
            webhook = WebhookClient(response_url)
            # Send a reply in the channel
            response = webhook.send(text=f"You said '{text}'")
            # Acknowledge this request
            return make_response("", 200)

        return make_response("", 404)

AsyncWebhookClient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The webhook client is available in asynchronous programming using the standard `asyncio <https://docs.python.org/3/library/asyncio.html>`_ library, too. You use ``AsyncWebhookClient`` instead for it.

``AsyncWebhookClient`` internally relies on `AIOHTTP <https://docs.aiohttp.org/en/stable/>`_ library but it is an optional dependency. So, to use this class, run ``pip install aiohttp`` beforehand.

.. code-block:: python

    import asyncio
    # requires: pip install aiohttp
    from slack_sdk.webhook.async_client import AsyncWebhookClient
    url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"

    async def send_message_via_webhook(url: str):
        webhook = AsyncWebhookClient(url)
        response = await webhook.send(text="Hello!")
        assert response.status_code == 200
        assert response.body == "ok"

    # This is the simplest way to run the async method
    # but you can go with any ways to run it
    asyncio.run(send_message_via_webhook(url))

.. include:: ../metadata.rst
