# Running your app
### Set App Credentials
Before you can run your app you need to put your bot token into the environment.

**Note:** This is the same token you copied at the end of [Step 1](/tutorial/01-creating-the-slack-app.md#add-a-bot-user).
<img width="786" alt="Copy the Bot token" src="https://user-images.githubusercontent.com/3329665/56845230-ec357e80-6872-11e9-83d4-5f953aee20b5.png">

- Add this token to your environment variables:
```
$ export SLACK_BOT_TOKEN='xoxb-XXXXXXXXXXXX-xxxxxxxxxxxx-XXXXXXXXXXXXXXXXXXXXXXXX'
```

- 🏁Run your app
```
$ python3 app.py
-> The Websocket connection has been opened.
```

### 🎉 That's it. Congratulations! You've just built a Slack app. 🤖

To demo the app, simply send the bot a message that says "start".

![Onboarding](https://user-images.githubusercontent.com/3329665/56870674-ab02b300-69c7-11e9-9101-eb823235f3c2.gif)
---

**Previous section: - [03 - Responding to Slack events](/tutorial/03-responding-to-slack-events.md).**

**Back to the [Table of contents](/tutorial/#table-of-contents).**
