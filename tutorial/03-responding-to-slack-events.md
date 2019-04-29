# Responding to Slack events
The code for this step is available [here](/tutorial/PythOnBoardingBot).

## Install the dependencies
> 💡 **[“Requirements files”](https://pip.pypa.io/en/stable/user_guide/#id12)** are files containing a list of items to be installed using pip install. Details on the format of the files are here: [Requirements File Format](https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format).

- In the root directory create a "requirements.txt" file.
- Add the following contents to that file and save the file.
```
slackclient>=2.0.0
certifi
```
> 💡 **[Certifi](https://github.com/certifi/python-certifi)** is a carefully curated collection of Root Certificates for validating the trustworthiness of SSL certificates while verifying the identity of TLS hosts. It has been extracted from the Requests project.

- Next you can install those dependencies by running the following command from your terminal:
```
$ pip3 install -r requirements.txt
-> Successfully installed slackclient-2.0.0
```

## Creating the app

- Create an `app.py` file to run the app.

The first thing we'll need to do is import the code our app needs to run.
- In `app.py` add the following code:
```Python
import os
import logging
import slack
import ssl as ssl_lib
import certifi
from onboarding_tutorial import OnboardingTutorial
```

Next we'll need our app to store some data. For simplicity we'll store our app data in-memory with the following data structure: `{"channel": {"user_id": OnboardingTutorial}}`.
- Add the the following line to `app.py`.
```Python
onboarding_tutorials_sent = {}
```

Let's add a function that's responsible for creating and sending the onboarding welcome message to new users. We'll also save the time stamp of the message when it's posted so we can update this message in the future.
- Add the following lines of code to `app.py`.
```Python
def start_onboarding(web_client: slack.WebClient, user_id: str, channel: str):
    # Create a new onboarding tutorial.
    onboarding_tutorial = OnboardingTutorial(channel)

    # Get the onboarding message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the onboarding message in Slack
    response = web_client.chat_postMessage(**message)

    # Capture the timestamp of the message we've just posted so
    # we can use it to update the message after a user
    # has completed an onboarding task.
    onboarding_tutorial.timestamp = response["ts"]

    # Store the message sent in onboarding_tutorials_sent
    if channel not in onboarding_tutorials_sent:
        onboarding_tutorials_sent[channel] = {}
    onboarding_tutorials_sent[channel][user_id] = onboarding_tutorial
```
**Note:** We're using the `WebClient` to send messages into Slack.
> 💡 **[WebClient](/slack/web/client.py)** A WebClient allows apps to communicate with the Slack Platform's Web API. This client handles constructing and sending HTTP requests to Slack as well as parsing any responses received into a `SlackResponse` dictionary-like object.

### Responding to events in Slack
When events occurr in Slack there are two primary ways to be notified about them. We can send you an HTTP Request through our Events API (preferred) or you can stream events through a websocket connection with our RTM API. The RTM API is only recommended if you're behind a firewall and cannot receive incoming web requests from Slack.

In this tutorial we'll be using the RTM API via the `RTMClient`. If you're interested in using the Events API take a look at the [SlackEventAdapter](https://github.com/slackapi/python-slack-events-api). We'll be adding support for the Events API into this library soon (See [#403](https://github.com/slackapi/python-slackclient/issues/403)).

> 💡 **[RTMClient](/slack/rtm/client.py)** An RTMClient allows apps to communicate with the Slack Platform's RTM API. The event-driven architecture of this client allows you to simply link callbacks to their corresponding events. When an event occurs this client executes your callback while passing along any information it receives.

Back to our application, it's time to link our onboarding functionality to Slack events.
- Add the following lines of code to `app.py`.
```Python
# ================ Team Join Event =============== #
# When the user first joins a team, the type of the event will be 'team_join'.
# Here we'll link the onboarding_message callback to the 'team_join' event.
@slack.RTMClient.run_on(event="team_join")
def onboarding_message(**payload):
    """Create and send an onboarding welcome message to new users. Save the
    time stamp of this message so we can update this message in the future.
    """
    # Get the id of the Slack user associated with the incoming event
    user_id = payload["data"]["user"]["id"]
    # Get WebClient so you can communicate back to Slack.
    web_client = payload["web_client"]

    # Open a DM with the new user.
    response = web_client.im_open(user_id)
    channel = response["channel"]["id"]

    # Post the onboarding message.
    start_onboarding(web_client, user_id, channel)


# ============= Reaction Added Events ============= #
# When a users adds an emoji reaction to the onboarding message,
# the type of the event will be 'reaction_added'.
# Here we'll link the update_emoji callback to the 'reaction_added' event.
@slack.RTMClient.run_on(event="reaction_added")
def update_emoji(**payload):
    """Update onboarding welcome message after recieving a "reaction_added"
    event from Slack. Update timestamp for welcome message as well.
    """
    data = payload["data"]
    web_client = payload["web_client"]
    channel_id = data["item"]["channel"]
    user_id = data["user"]

    # Get the original tutorial sent.
    onboarding_tutorial = onboarding_tutorials_sent[channel_id][user_id]

    # Mark the reaction task as completed.
    onboarding_tutorial.reaction_task_completed = True

    # Get the new message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the updated message in Slack
    updated_message = web_client.chat_update(**message)

    # Update the timestamp saved on the onboarding tutorial object
    onboarding_tutorial.timestamp = updated_message["ts"]


# =============== Pin Added Events ================ #
# When a users pins a message the type of the event will be 'pin_added'.
# Here we'll link the update_pin callback to the 'reaction_added' event.
@slack.RTMClient.run_on(event="pin_added")
def update_pin(**payload):
    """Update onboarding welcome message after recieving a "pin_added"
    event from Slack. Update timestamp for welcome message as well.
    """
    data = payload["data"]
    web_client = payload["web_client"]
    channel_id = data["channel_id"]
    user_id = data["user"]

    # Get the original tutorial sent.
    onboarding_tutorial = onboarding_tutorials_sent[channel_id][user_id]

    # Mark the pin task as completed.
    onboarding_tutorial.pin_task_completed = True

    # Get the new message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the updated message in Slack
    updated_message = web_client.chat_update(**message)

    # Update the timestamp saved on the onboarding tutorial object
    onboarding_tutorial.timestamp = updated_message["ts"]


# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the update_share callback to the 'message' event.
@slack.RTMClient.run_on(event="message")
def message(**payload):
    """Display the onboarding welcome message after receiving a message
    that contains "start".
    """
    data = payload["data"]
    web_client = payload["web_client"]
    channel_id = data.get("channel")
    user_id = data.get("user")
    text = data.get("text")

    if text and text.lower() == "start":
        return start_onboarding(web_client, user_id, channel_id)
```

Finally, we need to make our app runnable.
- 🏁 Add the following lines of code to the end of `app.py`.
```Python
if __name__ == "__main__":
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    slack_token = os.environ["SLACK_BOT_TOKEN"]
    rtm_client = slack.RTMClient(token=slack_token, ssl=ssl_context)
    rtm_client.start()
```
**Note:** When running in a virtual environment you often need to specify the location of the SSL Certificate(`cacert.pem`). To make this easy we use Certifi's built-in `where()` function to locate the installed certificate authority (CA) bundle.

**Final Note:** If you're interested in learning how to modify this app to run asynchronously I've adapted this code as such [here](/tutorial/PythOnBoardingBot/async_app.py).

---

**Next section: [04 - Running the app](/tutorial/04-running-the-app.md).**

**Previous section: [02 - Building a message](/tutorial/01-building-a-message.md).**

**Back to the [Table of contents](/tutorial/#table-of-contents).**
