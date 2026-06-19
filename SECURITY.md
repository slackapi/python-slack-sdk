# Security Policy

Slack takes the security of its software and services seriously, including all open-source repositories managed through the [slackapi](https://github.com/slackapi) GitHub organization.

## Reporting a Vulnerability

**Do NOT report security vulnerabilities through public GitHub issues, pull requests, or discussions.**

If you believe you have found a security vulnerability in `slack_sdk`, please report it through the Slack bug bounty program on HackerOne:

**<https://hackerone.com/slack>**

Even if `slack_sdk` is not explicitly listed as an in-scope asset on the HackerOne program page, reports for vulnerabilities in this package should still be submitted there. The Slack security team triages reports for all `slackapi` open-source repositories through this program.

If HackerOne is inaccessible, you may alternatively report the issue to [security@salesforce.com](mailto:security@salesforce.com).

Please do not discuss potential vulnerabilities in public without first coordinating with the security team.

## What to Include

To help us triage and respond quickly, please include:

- Type of vulnerability (e.g., signature bypass, token leakage, denial of service)
- Affected version(s) of `slack_sdk`
- Step-by-step reproduction instructions
- Proof-of-concept code or payloads, if available
- Impact assessment: what an attacker could achieve
- Any specific configuration required to trigger the vulnerability
- Affected source file paths, if known

## Threat Model

The Python Slack SDK is a collection of client libraries for interacting with Slack's APIs. It provides utilities for request signature verification, OAuth token management and storage, and real-time WebSocket communication via Socket Mode. The security boundary covers the safe handling of credentials, the integrity of cryptographic verification, and the confidentiality of data in transit and at rest.

### In Scope

The following are considered SDK vulnerabilities:

- Bypass of request signature verification (HMAC-SHA256 validation in `slack_sdk.signature`)
- Token or credential leakage through logs, error messages, HTTP headers, or unintended network requests
- OAuth state parameter validation bypass or CSRF vulnerabilities in the authorization flow (`slack_sdk.oauth`)
- Cross-tenant token exposure or installation data leakage in built-in installation stores
- Token storage vulnerabilities in any built-in installation store or state store backend
- Failure to enforce TLS for connections to Slack's APIs (Web API, WebSocket, or webhook endpoints)
- WebSocket connection hijacking or man-in-the-middle vulnerabilities in Socket Mode clients
- Denial of service caused by malformed API responses or WebSocket frames that crash or hang the client
- Information disclosure through SDK error responses or timing side channels
- Insecure default configurations that could lead to credential exposure

### Out of Scope

The following are NOT SDK vulnerabilities:

- Vulnerabilities in the Python runtime, operating system, or hosting infrastructure
- Security issues in Slack's server-side platform infrastructure (report those directly under Slack's main HackerOne scope)
- Vulnerabilities in third-party PyPI packages chosen and installed by the developer outside of this SDK's direct dependencies (e.g., aiohttp, websockets, SQLAlchemy, boto3)
- Security issues in developer application logic built on top of the SDK (e.g., storing tokens insecurely in application code)
- Attacks that require possession of valid tokens or signing secrets (the SDK assumes credentials provided to it are confidential)
- Rate limiting or resource exhaustion on Slack's servers caused by legitimate API usage
- Issues that only affect end-of-life Python versions with no reproduction on supported versions
- Security of custom API base URLs configured by the developer for testing or proxying

## Disclosure Policy

This project follows coordinated disclosure:

- Allow a reasonable timeframe for the team to investigate, develop, and release a fix before any public disclosure.
- Researchers who follow responsible disclosure practices are eligible for recognition and bounty consideration through the Slack HackerOne program.
