==============================================
SCIM API Client
==============================================

`SCIM API <https://api.slack.com/scim>`_ is a set of APIs for provisioning and managing user accounts and groups. SCIM is used by Single Sign-On (SSO) services and identity providers to manage people across a variety of tools, including Slack.

`SCIM (System for Cross-domain Identity Management) <http://www.simplecloud.info/>`_ is supported by a myriad of services. It behaves slightly differently from other Slack APIs.

Refer to `the API document <https://api.slack.com/scim>`_ for more details.

The Python document for this module is available at https://slack.dev/python-slack-sdk/api-docs/slack_sdk/

SCIMClient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An OAuth token with `the admin scope <https://api.slack.com/scopes/admin>`_ is required to access the SCIM API.

To fetch provisioned user data, you can use the ``search_users`` method in the client.

.. code-block:: python

    import os
    from slack_sdk.scim import SCIMClient

    client = SCIMClient(token=os.environ["SLACK_ORG_ADMIN_USER_TOKEN"])

    response = client.search_users(
        start_index=1,
        count=100,
        filter="""filter=userName Eq "Carly"""",
    )
    response.users  # List[User]

Check out `the class source code <https://github.com/slackapi/python-slack-sdk/blob/main/slack_sdk/scim/v1/user.py>`_ to learn more about the structure of the ``user`` in ``response.users``.

Similarly, the ``search_groups`` method is available and the shape of the ``Group`` object can be `found here <https://github.com/slackapi/python-slack-sdk/blob/main/slack_sdk/scim/v1/group.py>`_.

.. code-block:: python

    response = client.search_groups(
        start_index=1,
        count=10,
    )
    response.groups  # List[Group]

For creating, updating, and deleting users/groups:

.. code-block:: python

    from slack_sdk.scim.v1.user import User, UserName, UserEmail

    # POST /Users
    # Creates a user. Must include the user_name argument and at least one email address.
    # You may provide an email address as the user_name value,
    # but it will be automatically converted to a Slack-appropriate username.
    user = User(
        user_name="cal",
        name=UserName(given_name="C", family_name="Henderson"),
        emails=[UserEmail(value="your-unique-name@example.com")],
    )
    creation_result = client.create_user(user)

    # PATCH /Users/{user_id}
    # Updates an existing user resource, overwriting values for specified attributes.
    patch_result = client.patch_user(
        id=creation_result.user.id,
        partial_user=User(user_name="chenderson"),
    )

    # PUT /Users/{user_id}
    # Updates an existing user resource, overwriting all values for a user
    # even if an attribute is empty or not provided.
    user_to_update = patch_result.user
    user_to_update.name = UserName(given_name="Cal", family_name="Henderson")
    update_result = client.update_user(user=user_to_update)

    # DELETE /Users/{user_id}
    # Sets a Slack user to deactivated. The value of the {id}
    # should be the user's corresponding Slack ID, beginning with either U or W.
    delete_result = client.delete_user(user_to_update.id)

AsyncSCIMClient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Lastly, if you are keen to use asyncio for SCIM API calls, we offer ``AsyncSCIMClient`` for it. This client relies on aiohttp library.

.. code-block:: python

    import asyncio
    import os
    from slack_sdk.scim.async_client import AsyncSCIMClient

    client = AsyncSCIMClient(token=os.environ["SLACK_ORG_ADMIN_USER_TOKEN"])

    async def main():
        response = await client.search_groups(start_index=1, count=2)
        print(response.groups)

    asyncio.run(main())

--------

RetryHandler
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With the default settings, only ``ConnectionErrorRetryHandler`` with its default configuration (=only one retry in the manner of `exponential backoff and jitter <https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/>`_) is enabled. The retry handler retries if an API client encounters a connectivity-related failure (e.g., Connection reset by peer).

To use other retry handlers, you can pass a list of ``RetryHandler`` to the client constructor. For instance, you can add the built-in ``RateLimitErrorRetryHandler`` this way:

.. code-block:: python

    import os
    from slack_sdk.scim import SCIMClient
    client = SCIMClient(token=os.environ["SLACK_ORG_ADMIN_USER_TOKEN"])

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

    client = SCIMClient(
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
