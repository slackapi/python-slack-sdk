# Running your app

## Set App Credentials

Before you can run your app you need to put your bot token into the environment.

**Note:** This is the same token you copied at the end of [Step 1](/tutorial/01-creating-the-slack-app.md#add-a-bot-user).
![Copy bot token](assets/bot-token.png)

- Add this token to your environment variables:

```
$ export SLACK_BOT_TOKEN='xoxb-XXXXXXXXXXXX-xxxxxxxxxxxx-XXXXXXXXXXXXXXXXXXXXXXXX'
```

- Navigate to your app's **Basic Information** page from the left sidebar and scroll down to **App Credentials** and copy the value for **Signing Secret**:
  ![Copy signing secret](assets/signing-secret.png)

```
$ export SLACK_SIGNING_SECRET='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

- 🏁Run your app

```
$ python3 app.py
```

When running locally, you'll likely need to tunnel requests from a public URL to your machine. We recommend [ngrok](https://ngrok.com/) to set up a tunnel. Once you've started ngrok, you'll have a URL that you can set in the Event Subscriptions portion of the Slack app configuration. Append the URL from ngrok with /slack/events. For example, https://abcdef.ngrok.io/slack/events.

## Subscribe to events

In the previous section, we set up handlers for a couple of events, but we need to set up our app to listen to those events. Click on **Event Subscriptions** on the left hand sidebar of your app.

- Toggle the switch to **Enable Events**
  ![Enable events](assets/enable-events.png)

- Enter your public URL (for example, in the last step, ours was https://abcdef.ngrok.io/slack/events) and, if your server is running, the domain should be verified.

- Next, subscribe to the events we used in the previous step: `message.channels`, `team_join`, `pin_added`, and `reaction_added`.

![Subscribe to events](assets/subscribe-events.png).

When you click the green **Save Changes** button, you'll need to reinstall your app.

### 🎉 That's it. Congratulations! You've just built a Slack app. 🤖

To demo the app, simply invite your bot to a public channel and send a message that says "start". And then, the app will post a new message in the same channel. You can interact with the message by adding a reaction to it and adding the message to the pinned items. If the app is properly configured, you will see the modifications of the message accordingly.

## ![Onboarding](https://user-images.githubusercontent.com/3329665/56870674-ab02b300-69c7-11e9-9101-eb823235f3c2.gif)

**Previous section: [03 - Responding to Slack events](03-responding-to-slack-events.md).**

**Back to the [Table of contents](README.md#table-of-contents).**
