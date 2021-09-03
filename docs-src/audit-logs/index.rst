==============================================
Audit Logs API Client
==============================================

`Audit Logs API <https://api.slack.com/admins/audit-logs>`_ is a set of APIs for monitoring what’s happening in your `Enterprise Grid <https://api.slack.com/enterprise/grid>`_ organization.

The Audit Logs API can be used by security information and event management (SIEM) tools to provide an analysis of how your Slack organization is being accessed. You can also use this API to write your own applications to see how members of your organization are using Slack.

Follow the instructions in `the API document <https://api.slack.com/admins/audit-logs>`_ to get a valid token for using Audit Logs API. The Slack app using the Audit Logs API needs to be installed in the Enterprise Grid Organization, not an individual workspace within the organization.

The Python document for this module is available at https://slack.dev/python-slack-sdk/api-docs/slack_sdk/

AuditLogsClient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An OAuth token with `the admin scope <https://api.slack.com/scopes/admin>`_ is required to access this API.

You will likely use the ``/logs`` endpoint as it's the essential part of this API.

To learn about the available parameters for this endpoint, check out `this guide <https://api.slack.com/admins/audit-logs#how_to_call_the_audit_logs_api>`_. You can also learn more about the data structure of ``api_response.typed_body`` from `the class source code <https://github.com/slackapi/python-slack-sdk/blob/main/slack_sdk/audit_logs/v1/logs.py>`_.

.. code-block:: python

    import os
    from slack_sdk.audit_logs import AuditLogsClient

    client = AuditLogsClient(token=os.environ["SLACK_ORG_ADMIN_USER_TOKEN"])

    api_response = client.logs(action="user_login", limit=1)
    api_response.typed_body  # slack_sdk.audit_logs.v1.LogsResponse

If you would like to access ``/schemes`` or ``/actions``, you can use the following methods:

.. code-block:: python

    api_response = client.schemas()
    api_response = client.actions()

AsyncAuditLogsClient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are keen to use asyncio for SCIM API calls, we offer AsyncSCIMClient for it. This client relies on aiohttp library.

.. code-block:: python

    from slack_sdk.audit_logs.async_client import AsyncAuditLogsClient
    client = AsyncAuditLogsClient(token=os.environ["SLACK_ORG_ADMIN_USER_TOKEN"])

    api_response = await client.logs(action="user_login", limit=1)
    api_response.typed_body  # slack_sdk.audit_logs.v1.LogsResponse


--------

RetryHandler
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With the default settings, only ``ConnectionErrorRetryHandler`` with its default configuration (=only one retry in the manner of `exponential backoff and jitter <https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/>`_) is enabled. The retry handler retries if an API client encounters a connectivity-related failure (e.g., Connection reset by peer).

To use other retry handlers, you can pass a list of ``RetryHandler`` to the client constructor. For instance, you can add the built-in ``RateLimitErrorRetryHandler`` this way:

.. code-block:: python

    import os
    from slack_sdk.audit_logs import AuditLogsClient
    client = AuditLogsClient(token=os.environ["SLACK_ORG_ADMIN_USER_TOKEN"])

    # This handler does retries when HTTP status 429 is returned
    from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler
    rate_limit_handler = RateLimitErrorRetryHandler(max_retry_count=1)

    # Enable rate limited error retries as well
    client.retry_handlers.append(rate_limit_handler)

Creating your own ones is also quite simple. Defining a new class that inherits ``slack_sdk.http_retry.RetryHandler`` (``AsyncRetryHandler`` for asyncio apps) and implements required methods (internals of ``can_retry`` / ``prepare_for_next_retry``). Check the built-in ones' source code for learning how to properly implement.

.. code-block:: python

    import socket
    from typing import Optional
    from slack_sdk.http_retry import (RetryHandler, RetryState, HttpRequest, HttpResponse)
    from slack_sdk.http_retry.builtin_interval_calculators import BackoffRetryIntervalCalculator
    from slack_sdk.http_retry.jitter import RandomJitter

    class MyRetryHandler(RetryHandler):
        def _can_retry(
            self,
            *,
            state: RetryState,
            request: HttpRequest,
            response: Optional[HttpResponse] = None,
            error: Optional[Exception] = None
        ) -> bool:
            # [Errno 104] Connection reset by peer
            return error is not None and isinstance(error, socket.error) and error.errno == 104

    client = AuditLogsClient(
        token=os.environ["SLACK_ORG_ADMIN_USER_TOKEN"],
        retry_handlers=[MyRetryHandler(
            max_retry_count=1,
            interval_calculator=BackoffRetryIntervalCalculator(
                backoff_factor=0.5,
                jitter=RandomJitter(),
            ),
        )],
    )

For asyncio apps, ``Async`` prefixed corresponding modules are available. All the methods in those methods are async/await compatible. Check `the source code <https://github.com/slackapi/python-slack-sdk/blob/main/slack_sdk/http_retry/async_handler.py>`_ and `tests <https://github.com/slackapi/python-slack-sdk/blob/main/tests/slack_sdk_async/web/test_async_web_client_http_retry.py>`_ for more details.

.. include:: ../metadata.rst
