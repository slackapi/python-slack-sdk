import os
import pdb
import logging
import slack
import ssl as ssl_lib
import certifi
from onboarding_message import OnboardingMessage

# For simplicity we'll store our bot data with the following data structure.
# onboarding_messages = {'team_id': {"user_id": "onboarding_message_ts"}}
onboarding_messages_sent = {}


def store_message_sent(
    channel_id: str, user_id: str, onboarding_message: OnboardingMessage
):
    """Store the message sent in onboarding_messages_sent."""
    if channel_id not in onboarding_messages_sent:
        onboarding_messages_sent[channel_id] = {}
    onboarding_messages_sent[channel_id][user_id] = onboarding_message


def start_onboarding(web_client, user_id, channel):
    # Post the onboarding message.
    onboarding_message = OnboardingMessage(channel)
    response = web_client.chat_postMessage(**onboarding_message.to_dict())
    # We'll save the timestamp of the message we've just posted so
    # we can use it to update the message after a user
    # has completed an onboarding task.
    onboarding_message.timestamp = response["ts"]
    store_message_sent(channel, user_id, onboarding_message)


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

    # Get the original message sent.
    message = onboarding_messages_sent[channel_id][user_id]

    # Mark the reaction task as completed.
    message.reaction_task_completed = True

    # Update the message in Slack
    updated_message = web_client.chat_update(**message.to_dict())

    # Update the timestamp saved on the message object
    message.timestamp = updated_message["ts"]


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

    # Get the original message sent.
    message = onboarding_messages_sent[channel_id][user_id]

    # Mark the reaction task as completed.
    message.pin_task_completed = True

    # Update the message in Slack
    updated_message = web_client.chat_update(**message.to_dict())

    # Update the timestamp saved on the message object
    message.timestamp = updated_message["ts"]


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


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    slack_token = os.environ["SLACK_BOT_TOKEN"]
    rtm_client = slack.RTMClient(token=slack_token, ssl=ssl_context)
    rtm_client.start()
