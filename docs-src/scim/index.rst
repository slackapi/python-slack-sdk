==============================================
SCIM API Client
==============================================

`SCIM API <https://api.slack.com/scim>`_ is a set of APIs for provisioning and managing user accounts and groups. SCIM is used by Single Sign-On (SSO) services and identity providers to manage people across a variety of tools, including Slack.

`SCIM (System for Cross-domain Identity Management) <http://www.simplecloud.info/>`_ is supported by a myriad of services. It behaves slightly differently from other Slack APIs.

Refer to `the API document <https://api.slack.com/scim>`_ for more details.

The Python document for this module is available at https://slack.dev/python-slack-sdk/api-docs/

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

.. include:: ../metadata.rst
