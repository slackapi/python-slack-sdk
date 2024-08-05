# Python Slack SDK

The Slack Python SDK has corresponding
package for Slack APIs. They are small and powerful when used
independently, and work seamlessly when used together, too.

The Slack platform offers several APIs to build apps. Each Slack API
delivers part of the capabilities from the platform, so that you can
pick just those that fit for your needs.

## Features

| Feature                        | Use              | Package                            |
|--------------------------------|----------|-------|
| Web API                        | Send data to or query data from Slack using any of over 200 methods.                          | ``slack_sdk.web``, ``slack_sdk.web.async_client`` |
| Webhooks / `response_url`        | Send a message using Incoming Webhooks or `response_url`                                      | ``slack_sdk.webhook``, ``slack_sdk.webhook.async_client``            |
| Socket Mode                    | Receive and send messages over Socket Mode connections.                                       | ``slack_sdk.socket_mode``          |
| OAuth                          | Setup the authentication flow using V2 OAuth, OpenID Connect for Slack apps.                  | ``slack_sdk.oauth``                |
| Audit Logs API                 | Receive audit logs API data.                                                                  | ``slack_sdk.audit_logs``           |
| SCIM API                       | Utilize the SCIM APIs for provisioning and managing user accounts and groups.                 | ``slack_sdk.scim``                 |
| RTM API                        | Listen for incoming messages and a limited set of events happening in Slack, using WebSocket. | ``slack_sdk.rtm_v2``               |
| Request Signature Verification | Verify incoming requests from the Slack API servers.                                          | ``slack_sdk.signature``            |
| UI Builders                    | Construct UI components using easy-to-use builders.                                           | ``slack_sdk.models``               |

You can also view the [Python module documents](https://slack.dev/python-slack-sdk/api-docs/slack_sdk/)!

## Getting help

These docs have lots of information on the Python Slack SDK. There's also an in-depth Reference section. Please explore!

If you otherwise get stuck, we're here to help. The following are the best ways to get assistance working through your issue:

* [Issue Tracker](http://github.com/slackapi/python-slack-sdk/issues) for questions, bug reports, feature requests, and general discussion related to the Python Slack SDK. Try searching for an existing issue before creating a new one.
* [Email](mailto:support@slack.com) our developer support team: `support@slack.com`.

## Contributing

These docs live within the [Python Slack SDK](https://github.com/slackapi/python-slack-sdk) repository and are open source.

We welcome contributions from everyone! Please check out our
[Contributor's Guide](https://github.com/slackapi/python-slack-sdk/blob/main/.github/contributing.md) for how to contribute in a helpful and collaborative way.