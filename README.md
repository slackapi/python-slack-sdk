# Python slackclient

The Python `slackclient` library is a developer kit for interfacing with the Slack Web API and Real Time Messaging (RTM) API on Python 3.6 and above.

**Comprehensive documentation on using the Slack Python can be found at [https://slack.dev/python-slackclient/](https://slack.dev/python-slackclient/)**

[![pypi package][pypi-image]][pypi-url]
[![Build Status][travis-image]][travis-url]
[![Python Version][python-version]][pypi-url]
[![codecov][codecov-image]][codecov-url]
[![contact][contact-image]][contact-url]

Whether you're building a custom app for your team, or integrating a third party service into your Slack workflows, Slack Developer Kit for Python allows you to leverage the flexibility of Python to get your project up and running as quickly as possible.

The **Python slackclient** allows interaction with:

- The Slack web api methods available at our [Api Docs site][api-methods]
- Interaction with our [RTM API][rtm-docs]

If you want to use our [Events API][events-docs], please check the [Slack Events API adapter for Python][python-slack-events-api].

Details on the Tokens and Authentication can be found in our [Auth Guide](https://slack.dev/python-slackclient/auth.html).

## Table of contents

* [Requirements](#requirements)
* [Installation](#installation)
* [Getting started tutorial](#getting-started-tutorial)
* [Basic Usage of the Web Client](#basic-usage-of-the-web-client)
  * [Sending a message to Slack](#sending-a-message-to-slack)
  * [Uploading files to Slack](#uploading-files-to-slack)
* [Basic Usage of the RTM Client](#basic-usage-of-the-rtm-client)
* [Async usage](#async-usage)
  * [Slackclient as a script](#slackclient-as-a-script)
  * [Slackclient in a framework](#slackclient-in-a-framework)
* [Advanced Options](#advanced-options)
  * [SSL](#ssl)
  * [Proxy](#proxy)
  * [DNS performance](#dns-performance)
  * [Example](#example)
* [Migrating from v1](#migrating-from-v1)
* [Support](#support)

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
$ pip3 install slackclient
```

### Getting started tutorial

---

We've created this [tutorial](/tutorial) to build a basic Slack app in less than 10 minutes. It requires some general programming knowledge, and Python basics. It focuses on the interacting with Slack's Web and RTM API. Use it to give you an idea of how to use this SDK.

**[Read the tutorial to get started!](/tutorial)**

### Basic Usage of the Web Client

---

Slack provide a Web API that gives you the ability to build applications that interact with Slack in a variety of ways. This Development Kit is a module based wrapper that makes interaction with that API easier. We have a basic example here with some of the more common uses but a full list of the available methods are available [here][api-methods]. More detailed examples can be found in our [Basic Usage](https://slack.dev/python-slackclient/basic_usage.html) guide.

#### Sending a message to Slack

One of the most common use-cases is sending a message to Slack. If you want to send a message as your app, or as a user, this method can do both. In our examples, we specify the channel name, however it is recommended to use the `channel_id` where possible. Also, if your app's bot user is not in a channel yet, invite the bot user before running the code snippet (or add `chat:write.public` to Bot Token Scopes for posting in any public channels).

```python
import os
from slack import WebClient
from slack.errors import SlackApiError

client = WebClient(token=os.environ['SLACK_API_TOKEN'])

try:
    response = client.chat_postMessage(
        channel='#random',
        text="Hello world!")
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
from slack import WebClient
from slack.errors import SlackApiError

client = WebClient(token=os.environ['SLACK_API_TOKEN'])

try:
    filepath="./tmp.txt"
    response = client.files_upload(
        channels='#random',
        file=filepath)
    assert response["file"]  # the uploaded file
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")
```

### Basic Usage of the RTM Client

---

The [Real Time Messaging (RTM) API][rtm-docs] is a WebSocket-based API that allows you to receive events from Slack in real time and send messages as users.

If you prefer events to be pushed to you instead, we recommend using the HTTP-based [Events API][events-docs] instead. Most event types supported by the RTM API are also available in the Events API. You can check out our [Python Slack Events Adaptor][events-sdk] if you want to use this API instead.

An RTMClient allows apps to communicate with the Slack Platform's RTM API.

The event-driven architecture of this client allows you to simply link callbacks to their corresponding events. When an event occurs this client executes your callback while passing along any information it receives. We also give you the ability to call our web client from inside your callbacks.

In our example below, we watch for a [message event][message-event] that contains "Hello" and if its received, we call the `say_hello()` function. We then issue a call to the web client to post back to the channel saying "Hi" to the user.

```python
import os
from slack import RTMClient
from slack.errors import SlackApiError

@RTMClient.run_on(event='message')
def say_hello(**payload):
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']
    if 'text' in data and 'Hello' in data.get('text', []):
        channel_id = data['channel']
        thread_ts = data['ts']
        user = data['user']

        try:
            response = web_client.chat_postMessage(
                channel=channel_id,
                text=f"Hi <@{user}>!",
                thread_ts=thread_ts
            )
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")

rtm_client = RTMClient(token=os.environ["SLACK_API_TOKEN"])
rtm_client.start()
```

Please note that the default way of creating Slack apps no longer supports RTM API. Events using the RTM API **must** use a classic Slack app (with a plain `bot` scope).

If you already have a classic Slack app, you can use those credentials. If you don't and need to use the RTM API, you can create a classic Slack app from [this link](https://api.slack.com/apps?new_classic_app=1). You can learn more in the [API documentation](https://api.slack.com/authentication/basics#soon).

Also, even if the Slack app configuration pages encourage you to upgrade to the newer permission model, don't upgrade it and keep using the "classic" bot permission.

### Async usage

slackclient v2 and higher uses [AIOHttp][aiohttp] under the hood for asynchronous requests and [urllib][urllib] for synchronous requests.

Normal usage of the library does not run it in async, hence a kwarg of `run_async=True` is needed.

When in async mode its important to remember to await or run/run_until_complete the call.

#### Slackclient as a script

```python 
import asyncio
import os
from slack import WebClient
from slack.errors import SlackApiError

client = WebClient(
    token=os.environ['SLACK_API_TOKEN'],
    run_async=True
)
future = client.chat_postMessage(
    channel='#random',
    text="Hello world!"
)

loop = asyncio.get_event_loop()
try:
    # run_until_complete returns the Future's result, or raise its exception.
    response = loop.run_until_complete(future)
    assert response["message"]["text"] == "Hello world!"
except SlackApiError as e:
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")
finally:
    loop.close()
```

#### Slackclient in a framework

If you are using a framework invoking the asyncio event loop like : sanic/jupyter notebook/etc.

```python
import os
from slack import WebClient
from slack.errors import SlackApiError

client = WebClient(
    token=os.environ['SLACK_API_TOKEN'],
    run_async=True # turn async mode on
)
# Define this as an async function
async def send_to_slack(channel, text):
    try:
        # Don't forget to have await as the client returns asyncio.Future
        response = await client.chat_postMessage(
            channel=channel,
            text=text
        )
        assert response["message"]["text"] == text
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        raise e

# https://sanicframework.org/
from sanic import Sanic
from sanic.response import json

app = Sanic()
# e.g., http://localhost:3000/?text=foo&text=bar
@app.route('/')
async def test(request):
    text = 'Hello World!'
    if 'text' in request.args:
        text = "\t".join(request.args['text'])
    try:
        await send_to_slack(channel="#random", text=text)
        return json({'message': 'Done!'})
    except SlackApiError as e:
        return json({'message': f"Failed due to {e.response['error']}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
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
$ pip3 install slackclient[optional]
```

#### Example

```python
import os
from slack import WebClient
from ssl import SSLContext

sslcert = SSLContext()
# pip3 install proxy.py
# proxy --port 9000 --log-level d
proxyinfo = "http://localhost:9000"

client = WebClient(
    token=os.environ['SLACK_API_TOKEN'],
    ssl=sslcert,
    proxy=proxyinfo
)
response = client.chat_postMessage(
    channel="#random",
    text="Hello World!")
print(response)
```


### Migrating from v1

---

If you're migrating from v1.x of slackclient to v2.x, Please follow our migration guide to ensure your app continues working after updating.

**[Check out the Migration Guide here!](https://github.com/slackapi/python-slackclient/wiki/Migrating-to-2.x)**

### Support

---

If you get stuck, we’re here to help. The following are the best ways to get assistance working through your issue:

Use our [Github Issue Tracker][gh-issues] for reporting bugs or requesting features.
Visit the [Slack Community][slack-community] for getting help using Slack Developer Kit for Python or just generally bond with your fellow Slack developers.

<!-- Markdown links -->

[pypi-image]: https://badge.fury.io/py/slackclient.svg
[pypi-url]: https://pypi.python.org/pypi/slackclient
[travis-image]: https://travis-ci.org/slackapi/python-slackclient.svg?branch=main
[travis-url]: https://travis-ci.org/slackapi/python-slackclient
[python-version]: https://img.shields.io/pypi/pyversions/slackclient.svg
[codecov-image]: https://codecov.io/gh/slackapi/python-slackclient/branch/main/graph/badge.svg
[codecov-url]: https://codecov.io/gh/slackapi/python-slackclient
[contact-image]: https://img.shields.io/badge/contact-support-green.svg
[contact-url]: https://slack.com/support
[api-docs]: https://api.slack.com
[slackclientv1]: https://github.com/slackapi/python-slackclient/tree/v1
[api-methods]: https://api.slack.com/methods
[rtm-docs]: https://api.slack.com/rtm
[events-docs]: https://api.slack.com/events-api
[events-sdk]: https://github.com/slackapi/python-slack-events-api
[message-event]: https://api.slack.com/events/message
[python-slack-events-api]: https://github.com/slackapi/python-slack-events-api
[pypi]: https://pypi.python.org/pypi
[pipenv]: https://pypi.org/project/pipenv/
[gh-issues]: https://github.com/slackapi/python-slackclient/issues
[slack-community]: http://slackcommunity.com/
[dev-roadmap]: https://github.com/slackapi/python-slackclient/wiki/Slack-Python-SDK-Roadmap
[migration-guide]: documentation_v2/Migration.md
[files.upload]: https://api.slack.com/methods/files.upload
[auth-guide]: documentation_v2/auth.md
[basic-usage]: documentation_v2/basic_usage.md
[aiohttp]: https://aiohttp.readthedocs.io/
[urllib]: https://docs.python.org/3/library/urllib.request.html
