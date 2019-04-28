# 01 - Create a Slack app

## Slack Apps
> 💡 Build useful apps, internal tools, simplified workflows, or brillant bots for just your team or Slack's millions of users.

- To get started, create a new Slack App on [api.slack.com](https://api.slack.com/apps?new_app=1).
  1. Type in your app name
  2. Select the team you'd like to build your app on.
<img width="570" alt="Create-A-Slack-App" src="https://user-images.githubusercontent.com/3329665/56550657-13224680-653b-11e9-8f91-15c17e6977b7.png">

### Add A Bot User

Let's get ourselves a shiny new **Bot User** so our app can communicate on Slack. 

- On the left side navigation of your app's settings page you'll find the **Bot Users** tab where you can create a new bot user for your app.

<img width="191" alt="app_settings_nav_bot_user" src="https://user-images.githubusercontent.com/3329665/56551168-76f93f00-653c-11e9-9fd8-1a3e434773fe.png">

- Next click "Add a Bot User".

<img width="631" alt="Add a Bot User" src="https://user-images.githubusercontent.com/3329665/56551307-dfe0b700-653c-11e9-94ad-e1d34fdbd6f5.png">

- Give your bot user a name (e.g. "pythonboardingbot"), click "Add Bot User", and "Save Changes".

<img width="613" alt="Bot User" src="https://user-images.githubusercontent.com/3329665/56551468-52ea2d80-653d-11e9-85d7-e383bd1b3537.png">

🎉 You should briefly see a success banner.

<img width="1050" alt="Success banner" src="https://user-images.githubusercontent.com/3329665/56551675-d60b8380-653d-11e9-983a-5dd53cb55a97.png">

### Install the app in your workspace
- Under "Settings" on the lefthand side, click "Install App" and then "Install App to Workspace".
<img width="961" alt="Install App" src="https://user-images.githubusercontent.com/3329665/56844936-c2c62400-686d-11e9-8417-f79d92b7ae27.png">

Next you'll need to authorize the app for the Bot User permissions.
- Click the "Authorize" button.

<img width="527" alt="Authorize the app" src="https://user-images.githubusercontent.com/3329665/56844940-e6896a00-686d-11e9-922c-045031c418b9.png">

🏁 Finally copy and save your token. You'll need this to communicate with Slack's Platform.
<img width="786" alt="Copy the Bot token" src="https://user-images.githubusercontent.com/3329665/56845230-ec357e80-6872-11e9-83d4-5f953aee20b5.png">

---

**Next section: [02 - Building a message](02-building-a-message.md).**

**Back to the [Table of contents](/tutorial/#table-of-contents).**