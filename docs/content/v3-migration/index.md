==============================================
Migration Guide
==============================================

The v2 website is live `here <https://slack.dev/python-slackclient/>`_ just like before. However, the **slackclient** project is in maintenance mode now and this **slack_sdk** project is the successor.

From slackclient 2.x
*************************************************

There are a few changes introduced in v3.0:

* The PyPI project is renamed from ``slackclient`` to ``slack_sdk``
* Importing ``slack_sdk.*`` is recommended. You can still use ``slack.*`` with deprecation warnings for a while.
* ``slack_sdk`` has no required dependencies. This means ``aiohttp`` is no longer automatically resolved.
* ``WebClient`` no longer has ``run_async`` and ``aiohttp`` specific options. If you still need the option or other ``aiohttp`` specific options, use ``LegacyWebClient`` (``slackclient`` v2 compatible) or ``AsyncWebClient``.

We're sorry for the inconvenience.

-----

**Change:** The PyPI project is renamed from ``slackclient`` to ``slack_sdk``

**Action**: Remove ``slackclient``, add ``slack_sdk`` in ``requirements.txt``

Since v3, the PyPI project name is `slack_sdk <https://pypi.org/project/slack_sdk/>`_ (technically ``slack-sdk`` also works).

The biggest reason for the renaming is the feature coverage in v3 and newer. The SDK v3 provides not only API clients but also other modules. As the first step, it starts supporting OAuth flow out-of-the-box. The secondary reason is to make the names more consistent. The renaming addresses the long-lived confusion between the PyPI project and package names.

-----

**Change:** Importing ``slack_sdk.*`` is recommended. You can still use ``slack.*`` with deprecation warnings for a while.

**Action**: Replace ``from slack import``, ``import slack``, and so on in your source code.


Most imports can be simply replaced by ``find your_app -name '*.py' | xargs sed -i '' 's/from slack /from slack_sdk /g'`` or something similar. If you use ``slack.web.classes.*``, the conversion is not so simple that we recommend manually replacing imports for those.

That said, all existing code can be migrated to v3 without any code changes. If you don't have time for it, you can use ``slack`` package with deprecation warnings saying ``UserWarning: slack package is deprecated. Please use slack_sdk.web/webhook/rtm package instead. For more info, go to https://slack.dev/python-slack-sdk/v3-migration/`` for a while. We won't remove the compatibility in the short term.

-----

**Change:** ``slack_sdk`` has no required dependencies. This means ``aiohttp`` is no longer automatically resolved.

**Action**: Add ``aiohttp`` to ``requirements.txt`` if you use any of ``AsyncWebClient``, ``AsyncWebhookClient``, and ``LegacyWebClient``

If you use some modules that require ``aiohttp``, your ``requirements.txt`` needs to explicitly have ``aiohttp``. The ``slack_sdk`` dependency doesn't resolve it for you, unlike ``slackclient`` v2.


-----

**Change:** ``WebClient`` no longer has ``run_async`` and ``aiohttp`` specific options.

**Action:** If you still need the option or other ``aiohttp`` specific options, use ``LegacyWebClient`` (``slackclient`` v2 compatible) or ``AsyncWebClient``.

The new ``slack_sdk.web.WebClient`` doesn't rely on ``aiohttp`` internally at all. The class provides only the synchronous way to call Web APIs. If you need a v2 compatible one, you can use ``LegacyWebClient``. Apart from the name, there is no breaking change in the class.

If you're using ``run_async=True`` option, we highly recommend switching to ``AsyncWebClient``. ``AsyncWebClient`` is a straight-forward async HTTP client. You can expect the class properly works in the nature of ``async/await`` provided by the standard ``asyncio`` library.

From slackclient 1.x
*************************************************

Refer to `the migration guide <https://github.com/slackapi/python-slack-sdk/wiki/Migrating-to-2.x>`_.

.. include:: ../metadata.rst
