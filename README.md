# Python Slack SDK

The Slack platform offers several APIs to build apps. Each Slack API delivers part of the capabilities from the platform, so that you can pick just those that fit for your needs. This SDK offers a corresponding package for each of Slack’s APIs. They are small and powerful when used independently, and work seamlessly when used together, too.

**Comprehensive documentation on using the Slack Python can be found at [https://slack.dev/python-slack-sdk/](https://slack.dev/python-slack-sdk/)**

[![pypi package][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![Python Version][python-version]][pypi-url]
[![codecov][codecov-image]][codecov-url]
[![contact][contact-image]][contact-url]

Whether you're building a custom app for your team, or integrating a third party service into your Slack workflows, Slack Developer Kit for Python allows you to leverage the flexibility of Python to get your project up and running as quickly as possible.

The **Python Slack SDK** allows interaction with:

- `slack_sdk.web`: for calling the Slack Web API methods ([API Docs site][api-methods])
- `slack_sdk.webhook`: for utilizing the Incoming Webhooks and `response_url`s in payloads
- `slack_sdk.signature`: for verifying incoming requests from the Slack API server
- `slack_sdk.socket_mode`: for receiving and sending messages over [Socket Mode](https://api.slack.com/socket-mode) connections
- `slack_sdk.audit_logs`: for utilizing [Audit Logs APIs](https://api.slack.com/admins/audit-logs)
- `slack_sdk.scim`: for utilizing [SCIM APIs](https://api.slack.com/admins/scim)
- `slack_sdk.oauth`: for implementing the Slack OAuth flow
- `slack_sdk.models`: for constructing UI components using easy-to-use builders
- `slack_sdk.rtm`: for utilizing the [RTM API][rtm-docs]

If you want to use our [Events API][events-docs] and Interactivity features, please check the [Bolt for Python][bolt-python] library. Details on the Tokens and Authentication can be found in our [Auth Guide](https://slack.dev/python-slack-sdk/installation/).

## slackclient is in maintenance mode

Are you looking for [slackclient](https://pypi.org/project/slackclient/)? The website is live [here](https://slack.dev/python-slackclient/) just like before. However, the slackclient project is in maintenance mode now and this [`slack_sdk`](https://pypi.org/project/slack-sdk/) is the successor. If you have time to make a migration to slack_sdk v3, please follow [our migration guide](https://slack.dev/python-slack-sdk/v3-migration/) to ensure your app continues working after updating.

## Table of contents

* [Requirements](#requirements)
* [Installation](#installation)
* [Getting started tutorial](#getting-started-tutorial)
* [Basic Usage of the Web Client](#basic-usage-of-the-web-client)
  * [Sending a message to Slack](#sending-a-message-to-slack)
  * [Uploading files to Slack](#uploading-files-to-slack)
* [Async usage](#async-usage)
  * [WebClient as a script](#asyncwebclient-in-a-script)
  * [WebClient in a framework](#asyncwebclient-in-a-framework)
* [Advanced Options](#advanced-options)
  * [SSL](#ssl)
  * [Proxy](#proxy)
  * [DNS performance](#dns-performance)
  * [Example](#example)
* [Migrating from v1](#migrating-from-v1)
* [Support](#support)
* [Development](#development)

### Requirements

---

This library requires Python 3.6 and above. If you require Python 2, please use our [SlackClient - v1.x][slackclientv1]. If you're unsure how to check what version of Python you're on, you can check it using the following:

> **Note:** You may need to use `python3` before your commands to ensure you use the correct Python path. e.g. `python3 --version`

```bash
python --version

-- or --

python3 --version
```

### Installation

We recommend using [PyPI][pypi] to install the Slack Developer Kit for Python.

```bash
$ pip install slack_sdk
```

### Getting started tutorial

---

We've created this [tutorial](https://github.com/slackapi/python-slack-sdk/tree/main/tutorial) to build a basic Slack app in less than 10 minutes. It requires some general programming knowledge, and Python basics. It focuses on the interacting with Slack's Web and RTM API. Use it to give you an idea of how to use this SDK.

**[Read the tutorial to get started!](https://github.com/slackapi/python-slack-sdk/tree/main/tutorial)**

### Basic Usage of the Web Client

---

Slack provide a Web API that gives you the ability to build applications that interact with Slack in a variety of ways. This Development Kit is a module based wrapper that makes interaction with that API easier. We have a basic example here with some of the more common uses but a full list of the available methods are available [here][api-methods]. More detailed examples can be found in [our guide](https://slack.dev/python-slack-sdk/web/).

#### Sending a message to Slack

One of the most common use-cases is sending a message to Slack. If you want to send a message as your app, or as a user, this method can do both. In our examples, we specify the channel name, however it is recommended to use the `channel_id` where possible. Also, if your app's bot user is not in a channel yet, invite the bot user before running the code snippet (or add `chat:write.public` to Bot Token Scopes for posting in any public channels).

```python
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

try:
    response = client.chat_postMessage(channel='#random', text="Hello world!")
    assert response["message"]["text"] == "Hello world!"
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")
```

Here we also ensure that the response back from Slack is a successful one and that the message is the one we sent by using the `assert` statement.

#### Uploading files to Slack

We've changed the process for uploading files to Slack to be much easier and straight forward. You can now just include a path to the file directly in the API call and upload it that way. You can find the details on this api call [here][files.upload]

```python
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

try:
    filepath="./tmp.txt"
    response = client.files_upload(channels='#random', file=filepath)
    assert response["file"]  # the uploaded file
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")
```

### Async usage

`AsyncWebClient` in this SDK requires [AIOHttp][aiohttp] under the hood for asynchronous requests.

#### AsyncWebClient in a script

```python
import asyncio
import os
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

client = AsyncWebClient(token=os.environ['SLACK_BOT_TOKEN'])

async def post_message():
    try:
        response = await client.chat_postMessage(channel='#random', text="Hello world!")
        assert response["message"]["text"] == "Hello world!"
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

asyncio.run(post_message())
```

#### AsyncWebClient in a framework

If you are using a framework invoking the asyncio event loop like : sanic/jupyter notebook/etc.

```python
import os
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

client = AsyncWebClient(token=os.environ['SLACK_BOT_TOKEN'])
# Define this as an async function
async def send_to_slack(channel, text):
    try:
        # Don't forget to have await as the client returns asyncio.Future
        response = await client.chat_postMessage(channel=channel, text=text)
        assert response["message"]["text"] == text
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        raise e

from aiohttp import web

async def handle_requests(request: web.Request) -> web.Response:
    text = 'Hello World!'
    if 'text' in request.query:
        text = "\t".join(request.query.getall("text"))
    try:
        await send_to_slack(channel="#random", text=text)
        return web.json_response(data={'message': 'Done!'})
    except SlackApiError as e:
        return web.json_response(data={'message': f"Failed due to {e.response['error']}"})


if __name__ == "__main__":
    app = web.Application()
    app.add_routes([web.get("/", handle_requests)])
    # e.g., http://localhost:3000/?text=foo&text=bar
    web.run_app(app, host="0.0.0.0", port=3000)
```

### Advanced Options

#### SSL

You can provide a custom SSL context or disable verification by passing the `ssl` option, supported by both the RTM and the Web client.

For async requests, see the [AIOHttp SSL documentation](https://docs.aiohttp.org/en/stable/client_advanced.html#ssl-control-for-tcp-sockets).

For sync requests, see the [urllib SSL documentation](https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen).

#### Proxy

A proxy is supported when making async requests, pass the `proxy` option, supported by both the RTM and the Web client.

For async requests, see [AIOHttp Proxy documentation](https://docs.aiohttp.org/en/stable/client_advanced.html#proxy-support).

For sync requests, setting either `HTTPS_PROXY` env variable or the `proxy` option works.

#### DNS performance

Using the async client and looking for a performance boost? Installing the optional dependencies (aiodns) may help speed up DNS resolving by the client. We've included it as an extra called "optional":
```bash
$ pip install slack_sdk[optional]
```

#### Example

```python
import os
from slack_sdk import WebClient
from ssl import SSLContext

sslcert = SSLContext()
# pip3 install proxy.py
# proxy --port 9000 --log-level d
proxyinfo = "http://localhost:9000"

client = WebClient(
    token=os.environ['SLACK_BOT_TOKEN'],
    ssl=sslcert,
    proxy=proxyinfo
)
response = client.chat_postMessage(channel="#random", text="Hello World!")
print(response)
```

### Migrating from v2

If you're migrating from slackclient v2.x of slack_sdk to v3.x, Please follow our migration guide to ensure your app continues working after updating.

**[Check out the Migration Guide here!](https://slack.dev/python-slack-sdk/v3-migration/)**

### Migrating from v1

If you're migrating from v1.x of slackclient to v2.x, Please follow our migration guide to ensure your app continues working after updating.

**[Check out the Migration Guide here!](https://github.com/slackapi/python-slack-sdk/wiki/Migrating-to-2.x)**

### Support

---

If you get stuck, we’re here to help. The following are the best ways to get assistance working through your issue:

Use our [Github Issue Tracker][gh-issues] for reporting bugs or requesting features.
Visit the [Slack Community][slack-community] for getting help using Slack Developer Kit for Python or just generally bond with your fellow Slack developers.

### Contributing

We welcome contributions from everyone! Please check out our
[Contributor's Guide](.github/contributing.md) for how to contribute in a
helpful and collaborative way.

<!-- Markdown links -->

[pypi-image]: https://badge.fury.io/py/slack-sdk.svg
[pypi-url]: https://pypi.org/project/slack-sdk/
[python-version]: https://img.shields.io/pypi/pyversions/slack-sdk.svg
[build-image]: https://github.com/slackapi/python-slack-sdk/workflows/CI%20Build/badge.svg
[build-url]: https://github.com/slackapi/python-slack-sdk/actions?query=workflow%3A%22CI+Build%22
[codecov-image]: https://codecov.io/gh/slackapi/python-slack-sdk/branch/main/graph/badge.svg
[codecov-url]: https://codecov.io/gh/slackapi/python-slack-sdk
[contact-image]: https://img.shields.io/badge/contact-support-green.svg
[contact-url]: https://slack.com/support
[slackclientv1]: https://github.com/slackapi/python-slackclient/tree/v1
[api-methods]: https://api.slack.com/methods
[rtm-docs]: https://api.slack.com/rtm
[events-docs]: https://api.slack.com/events-api
[bolt-python]: https://github.com/slackapi/bolt-python
[pypi]: https://pypi.org/
[gh-issues]: https://github.com/slackapi/python-slack-sdk/issues
[slack-community]: https://slackcommunity.com/
[files.upload]: https://api.slack.com/methods/files.upload
[aiohttp]: https://aiohttp.readthedocs.io/
[urllib]: https://docs.python.org/3/library/urllib.request.html
