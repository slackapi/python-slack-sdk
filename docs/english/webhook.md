# Webhook client

## Incoming webhooks {#incoming-webhooks}

You can use `slack_sdk.webhook.WebhookClient` for [incoming webhooks](/messaging/sending-messages-using-incoming-webhooks) and message responses using [`response_url`](/interactivity/handling-user-interaction#message_responses) in payloads.

To use [incoming webhooks](/messaging/sending-messages-using-incoming-webhooks), calling the `WebhookClient(url)#send(payload)` method works for you. The call posts a message in a channel associated with the webhook URL.

``` python
from slack_sdk.webhook import WebhookClient
url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
webhook = WebhookClient(url)

response = webhook.send(text="Hello!")
assert response.status_code == 200
assert response.body == "ok"
```

It's also possible to use `blocks` using [Block Kit](/block-kit).

``` python
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
```

## The `response_url`

User actions in channels generates a [`response_url`](/interactivity/handling-user-interaction#message_responses) and includes the URL in its payload. You can use `WebhookClient` to send a message via the `response_url`.

``` python
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
    # https://docs.slack.dev/authentication/verifying-requests-from-slack
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
```

## AsyncWebhookClient {#asyncwebhookclient}

The webhook client is available in asynchronous programming using the standard [asyncio](https://docs.python.org/3/library/asyncio.html) library. You use `AsyncWebhookClient` instead. `AsyncWebhookClient` internally relies on the [AIOHTTP](https://docs.aiohttp.org/en/stable/) library, but it is an optional dependency. To use this class, run `pip install aiohttp` beforehand.

``` python
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
```

## RetryHandler {#retryhandler}

With the default settings, only `ConnectionErrorRetryHandler` with its default configuration (=only one retry in the manner of [exponential backoff and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)) is enabled. The retry handler retries if an API client encounters a connectivity-related failure (e.g., connection reset by peer).

To use other retry handlers, you can pass a list of `RetryHandler` to the client constructor. For instance, you can add the built-in `RateLimitErrorRetryHandler` this way:

``` python
from slack_sdk.webhook import WebhookClient
url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
webhook = WebhookClient(url=url)

# This handler does retries when HTTP status 429 is returned
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler
rate_limit_handler = RateLimitErrorRetryHandler(max_retry_count=1)

# Enable rate limited error retries as well
client.retry_handlers.append(rate_limit_handler)
```

You can also create one on your own by defining a new class that inherits `slack_sdk.http_retry RetryHandler` (`AsyncRetryHandler` for asyncio apps) and implements required methods (internals of `can_retry` / `prepare_for_next_retry`). Check out the source code for the ones that are built in to learn how to properly implement them.

``` python
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
```

For asyncio apps, `Async` prefixed corresponding modules are available. All the methods in those methods are async/await compatible. Check [the source code](https://github.com/slackapi/python-slack-sdk/blob/main/slack_sdk/http_retry/async_handler.py) for more details.
