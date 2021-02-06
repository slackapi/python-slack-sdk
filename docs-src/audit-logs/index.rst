==============================================
Audit Logs API Client
==============================================

`Audit Logs API <https://api.slack.com/admins/audit-logs>`_ is a set of APIs for monitoring what’s happening in your `Enterprise Grid <https://api.slack.com/enterprise/grid>`_ organization.

The Audit Logs API can be used by security information and event management (SIEM) tools to provide an analysis of how your Slack organization is being accessed. You can also use this API to write your own applications to see how members of your organization are using Slack.

Follow the instructions in `the API document <https://api.slack.com/admins/audit-logs>`_ to get a valid token for using Audit Logs API. The Slack app using the Audit Logs API needs to be installed in the Enterprise Grid Organization, not an individual workspace within the organization.

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


.. include:: ../metadata.rst
