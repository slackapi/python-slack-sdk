# Overview

:::danger[The [`slackclient`](https://pypi.org/project/slackclient/) PyPI project is in maintenance mode and the [slack-sdk](https://pypi.org/project/slack-sdk/) project is its successor.] 

The v3 SDK provides additional features such as Socket Mode, OAuth flow, SCIM API, Audit Logs API, better async support, retry handlers, and more.

:::

Refer to the [migration guide](/tools/python-slack-sdk/v3-migration) to learn how to smoothly migrate your existing code.

Slack APIs allow anyone to build full featured integrations that extend and expand the capabilities of your Slack workspace. These APIs allow you to build applications that interact with Slack just like the people on your team. They can post messages, respond to events that happen, and build complex UIs for getting work done.

To make it easier for Python programmers to build Slack applications, we've provided this open source SDK that will help you get started building Python apps as quickly as possible. The current version is built for Python 3.7 and higher — if you need to target Python 2.x, you might consider using v1 of the SDK.

## Slack platform basics {#platform-basics}

If you're new to the Slack platform, we have a general purpose [quickstart guide](/quickstart) that isn't specific to any language or framework. Its a great place to learn all about the concepts that go into building a great Slack app.

Before you get started building on the Slack platform, you need to set up [your app's configuration](https://api.slack.com/apps/new). This is where you define things like your apps permissions and the endpoints that Slack should use for interacting with the backend you'll build using Python.

The app configuration page is also where you'll acquire the OAuth token you'll use to call Slack API methods. Treat this token with care, just like you would a password, because it has access to your workspace and can potentially read and write data to and from it.

## Installation {#installation}

We recommend using [PyPI](https://pypi.python.org/pypi) to install as follows:

``` bash
pip install slackclient
```

Of course, you can always pull the source code directly into your project like this:

``` bash
git clone https://github.com/slackapi/python-slackclient.git
```

And then, save a few lines of code as `./test.py` like so:

``` python
# test.py
import sys
# Load the local source directly
sys.path.insert(1, "./python-slackclient")
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
# Verify it works
from slack import WebClient
client = WebClient()
api_response = client.api_test()
```

Run the code as follows:

``` bash
python test.py
```
