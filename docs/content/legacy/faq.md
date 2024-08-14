# Frequently Asked Questions

:::danger

The [slackclient](https://pypi.org/project/slackclient/) PyPI project is in maintenance mode now and [slack-sdk](https://pypi.org/project/slack-sdk/) project is the successor. The v3 SDK provides more functionalities such as Socket Mode, OAuth flow module, SCIM API, Audit Logs API, better asyncio support, retry handlers, and many more.

:::

## I cannot install `slackclient`

We recommend using [virtualenv (venv)](https://docs.python.org/3/tutorial/venv.html) to set up your
Python runtime.

``` bash
# Create a dedicated virtual env for running your Python scripts
python -m venv env

# Run env\Scripts\activate on Windows OS
source env/bin/activate

# Install slackclient PyPI package
pip install "slackclient>=2.0"

# Set your token as an env variable (`set` command for Windows OS)
export SLACK_API_TOKEN=xoxb-***
```

Then, verify the following code works on the Python REPL (you can start
it by just `python`).

``` python
import os
import logging
from slack import WebClient
logging.basicConfig(level=logging.DEBUG)
client = WebClient(token=os.environ["SLACK_API_TOKEN"])
res = client.api_test()
```

If you encounter an error saying
`AttributeError: module 'slack' has no attribute 'WebClient'`, run
`pip list`. If you find both `slackclient` and `slack` in the output,
try removing `slack` by `pip uninstall slack` and reinstalling
`slackclient`.

## Should I go with `run_async`?

For most cases, we recommend going with `run_async=False` mode. So, the
default is `False`.

If your application turns `run_async` on, the app should follow right
and efficient ways to use
[asyncio](https://docs.python.org/3/library/asyncio.html)'s
non-blocking event loops and
[aiohttp](https://docs.aiohttp.org/en/stable/). Also, consider using
async frameworks and their appropriate runtime. Running event loops
along with Flask or similar may not be a good fit.

If you have to simultaneously run `WebClient` with `run_async=True`
outside an event loop for some reason, sharing a single `WebClient`
instance doesn't work for you. Create an instance every time you run
the code. The `run_async=False` mode doesn't have such issues.

## I found a bug!

That's great! Thank you. Let us know on the Issue Tracker. If
you're feeling particularly ambitious, why not submit a pull request with a bug fix?

## There's a feature missing!

There's always something more that could be added! You can let us know
in the Issue Tracker to start a discussion around the proposed
feature, that's a good start. If you're feeling particularly
ambitious, why not write the feature yourself, and submit a pull request! We love feedback and we love help and we don't bite. Much.

## How do I contribute?

What an excellent question. First of all, please have a look at our
general contributing guidelines.

All done? Great! While we're super excited to incorporate your new
feature, there are a couple of things we want to make sure you've given
thought to.

-   Please write unit tests for your new code. But don't **just** aim
    to increase the test coverage, rather, we expect you to have written
    **thoughtful** tests that ensure your new feature will continue to
    work as expected, and to help future contributors to ensure they
    don't break it!
-   Please document your new feature. Think about **concrete use cases**
    for your feature, and add a section to the appropriate document,
    including a **complete** sample program that demonstrates your
    feature. Don't forget to update the changelog in `changelog.rst`!

Including these two items with your pull request will totally make our
day---and, more importantly, your future users' days!
