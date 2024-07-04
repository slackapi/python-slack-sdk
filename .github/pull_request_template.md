## Summary

<!-- Describe the goal of this PR. Mention any related issue numbers -->

### Testing

<!-- Describe what steps a reviewer should follow to test your changes. -->

### Category <!-- place an `x` in each of the `[ ]`  -->

- [ ] **slack_sdk.web.WebClient (sync/async)** (Web API client)
- [ ] **slack_sdk.webhook.WebhookClient (sync/async)** (Incoming Webhook, response_url sender)
- [ ] **slack_sdk.socket_mode** (Socket Mode client)
- [ ] **slack_sdk.signature** (Request Signature Verifier)
- [ ] **slack_sdk.oauth** (OAuth Flow Utilities)
- [ ] **slack_sdk.models** (UI component builders)
- [ ] **slack_sdk.scim** (SCIM API client)
- [ ] **slack_sdk.audit_logs** (Audit Logs API client)
- [ ] **slack_sdk.rtm_v2** (RTM client)
- [ ] `/docs-src` (Documents, have you run `./scripts/docs.sh`/`./scripts/generate_api_docs.sh`?)
- [ ] `/tutorial` (PythOnBoardingBot tutorial)
- [ ] `tests`/`integration_tests` (Automated tests for this library)

## Requirements <!-- place an `x` in each `[ ]` -->

- [ ] I've read and understood the [Contributing Guidelines](https://github.com/slackapi/python-slack-sdk/blob/main/.github/contributing.md) and have done my best effort to follow them.
- [ ] I've read and agree to the [Code of Conduct](https://slackhq.github.io/code-of-conduct).
- [ ] I've run `python3 -m venv .venv && source .venv/bin/activate && ./scripts/run_validation.sh` after making the changes.
