import logging

logging.basicConfig(level=logging.DEBUG)

# export SLACK_API_TOKEN=xoxb-***
# python3 integration_tests/samples/basic_usage/sending_a_message.py

import os
from slack_sdk.web import WebClient

slack_token = os.environ["SLACK_API_TOKEN"]
client = WebClient(token=slack_token)

if __name__ == "__main__":
    channel_id = "#random"
    user_id = client.users_list()["members"][0]["id"]
else:
    channel_id = "C0XXXXXX"
    user_id = "U0XXXXXXX"

response = client.chat_postMessage(channel=channel_id, text="Hello from your app! :tada:")
# Ensure the channel_id is not a name
channel_id = response["channel"]

thread_ts = response["message"]["ts"]

response = client.chat_postEphemeral(channel=channel_id, user=user_id, text="Hello silently from your app! :tada:")

response = client.chat_postMessage(
    channel=channel_id,
    blocks=[
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Danny Torrence left the following review for your property:",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "<https://example.com|Overlook Hotel> \n :star: \n Doors had too many axe holes, guest in room "
                + "237 was far too rowdy, whole place felt stuck in the 1920s.",
            },
            "accessory": {
                "type": "image",
                "image_url": "https://images.pexels.com/photos/750319/pexels-photo-750319.jpeg",
                "alt_text": "Haunted hotel image",
            },
        },
        {
            "type": "section",
            "fields": [{"type": "mrkdwn", "text": "*Average Rating*\n1.0"}],
        },
    ],
)

# Threading Messages
response = client.chat_postMessage(channel=channel_id, text="Hello from your app! :tada:", thread_ts=thread_ts)

response = client.chat_postMessage(
    channel=channel_id,
    text="Hello from your app! :tada:",
    thread_ts=thread_ts,
    reply_broadcast=True,
)

# Updating a message
response = client.chat_postMessage(channel=channel_id, text="To be modified :eyes:")
ts = response["message"]["ts"]

response = client.chat_update(channel=channel_id, ts=ts, text="updates from your app! :tada:")

# Deleting a message
response = client.chat_postMessage(channel=channel_id, text="To be deleted :eyes:")
ts = response["message"]["ts"]
response = client.chat_delete(channel=channel_id, ts=ts)
