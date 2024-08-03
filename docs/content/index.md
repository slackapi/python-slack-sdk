# Python Slack SDK

The Slack platform offers several APIs to build apps. Each Slack API
delivers part of the capabilities from the platform, so that you can
pick just those that fit for your needs.

The Slack Python SDK offers a corresponding
package for each of the Slack APIs. They are small and powerful when used
independently, and work seamlessly when used together, too.

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

## Reporting Bugs

Let us know on the [Issue Tracker](https://github.com/slackapi/python-slack-sdk/issues). If
you're feeling particularly ambitious, why not submit a [pull
request](api.slack.com) with a bug fix?

## Requesting Features

There's always something more that could be added! You can let us know
in the [Issue Tracker](https://github.com/slackapi/python-slack-sdk/issues) to start a discussion around the proposed
feature, that's a good start. If you're feeling particularly
ambitious, why not write the feature yourself, and submit a [pull
request](api.slack.com)! We love feedback and we love help and we don't bite. Much.

## Contributing

Excellent! First, please have a look at our
general [contributing guidelines](https://github.com/slackapi/python-slack-sdk/blob/main/.github/contributing.md).

All done? Great! While we're super excited to incorporate your new
feature, there are a couple of things we want to make sure you've given
thought to.

* Please write unit tests for your new code. But don't **just** aim
to increase the test coverage, rather, we expect you to have written
**thoughtful** tests that ensure your new feature will continue to
work as expected, and to help future contributors to ensure they
don't break it!

* Please document your new feature. Think about **concrete use cases**
for your feature, and add a section to the appropriate document,
including a **complete** sample program that demonstrates your
feature.

Including these two items with your pull request will totally make our
day — and, more importantly, your future users' days!