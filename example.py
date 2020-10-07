from slack_sdk.socketmode import SocketModeClient
from slack_sdk import WebClient
import os
import asyncio

slack_app_token = os.environ["SLACK_APP_TOKEN"]
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]

client_options = {
    # 'base_url': 'https://dev.slack.com/api/'
}
socketClient = SocketModeClient(token=slack_app_token, client_options=client_options)
webclient = WebClient(token=slack_bot_token, base_url=client_options['base_url'] if 'base_url' in client_options else 'https://slack.com/api/')


@socketClient.all()
def global_listener(slack_event):
    print('in global listener')
    # print(slack_event)
    # slack_event.ack()
    # print(body)
    # print(ack)
    # print(event)


# TODO: Figure out how to split up event argument into body, event, ack
# TODO: We seem to be receiving this event multiple times (at least twice). Maybe we aren't responding correctly?
@socketClient.event('app_home_opened')
def app_home_opened_listener(event):
    print('in event listener')
    # print(event)
    print(event['event'])
    # Call ack
    event['ack']()

    # TODO: call client.views.publish
    webclient.views_publish(user_id=event['event'].get('user'), view={
        "type": "home",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "App Home Published"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Farmhouse",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "action_id": 'farm_button'
                    },
                ]
            }
        ]
    })

# TODO: clicking the button and responding is taking longer than 3 seconds, so we get the little warning in slack
@socketClient.interactive()
def handle_farm_button_click(event):
    print('handling button click')
    action_id = event['body'].get('actions', {})[0].get('action_id')
    print('action_id', action_id)

    # Call ack
    event['ack']()

    if action_id == 'farm_button':
        # handle farm button
        print('matched button')

# Potential alternative design
# @socketCLient.on('interactive')


asyncio.run(socketClient.start())
