==============================================
Webhook Client
==============================================

You can use ``slack_sdk.webhook.WebhookClient`` for `Incoming Webhooks <https://api.slack.com/messaging/webhooks>`_ and message responses using `response_url in payloads <https://api.slack.com/interactivity/handling#message_responses>`_.

The Python document for this module is available at https://slack.dev/python-slack-sdk/api-docs/slack_sdk/

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

--------

RetryHandler
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With the default settings, only ``ConnectionErrorRetryHandler`` with its default configuration (=only one retry in the manner of `exponential backoff and jitter <https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/>`_) is enabled. The retry handler retries if an API client encounters a connectivity-related failure (e.g., Connection reset by peer).

To use other retry handlers, you can pass a list of ``RetryHandler`` to the client constructor. For instance, you can add the built-in ``RateLimitErrorRetryHandler`` this way:

.. code-block:: python

    from slack_sdk.webhook import WebhookClient
    url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
    webhook = WebhookClient(url=url)

    # This handler does retries when HTTP status 429 is returned
    from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler
    rate_limit_handler = RateLimitErrorRetryHandler(max_retry_count=1)

    # Enable rate limited error retries as well
    client.retry_handlers.append(rate_limit_handler)

Creating your own ones is also quite simple. Defining a new class that inherits ``slack_sdk.http_retry.RetryHandler`` (``AsyncRetryHandler`` for asyncio apps) and implements required methods (internals of ``can_retry`` / ``prepare_for_next_retry``). Check the built-in ones' source code for learning how to properly implement.

.. code-block:: python

    import socket
    from typing import Optional
    from slack_sdk.http_retry import (RetryHandler, RetryState, HttpRequest, HttpResponse)
    from slack_sdk.http_retry.builtin_interval_calculators import BackoffRetryIntervalCalculator
    from slack_sdk.http_retry.jitter import RandomJitter

    class MyRetryHandler(RetryHandler):
        def _can_retry(
            self,
            *,
            state: RetryState,
            request: HttpRequest,
            response: Optional[HttpResponse] = None,
            error: Optional[Exception] = None
        ) -> bool:
            # [Errno 104] Connection reset by peer
            return error is not None and isinstance(error, socket.error) and error.errno == 104

    webhook = WebhookClient(
        url=url,
        retry_handlers=[MyRetryHandler(
            max_retry_count=1,
            interval_calculator=BackoffRetryIntervalCalculator(
                backoff_factor=0.5,
                jitter=RandomJitter(),
            ),
        )],
    )

For asyncio apps, ``Async`` prefixed corresponding modules are available. All the methods in those methods are async/await compatible. Check `the source code <https://github.com/slackapi/python-slack-sdk/blob/main/slack_sdk/http_retry/async_handler.py>`_ and `tests <https://github.com/slackapi/python-slack-sdk/blob/main/tests/slack_sdk_async/web/test_async_web_client_http_retry.py>`_ for more details.

.. include:: ../metadata.rst
