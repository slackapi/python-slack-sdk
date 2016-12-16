==============================================
Changelog
==============================================

v1.0.4 (2016-12-15)
-------------------

  - fixed the ability to search for a user by ID

v1.0.3 (2016-12-13)
-------------------

  - fixed an issue causing RTM connections to fail for large teams

v1.0.2 (2016-09-22)
-------------------

  - removed unused ping counter
  - fixed contributor guidelines links
  - updated documentation
  - Fix bug preventing API calls requiring a file ID
  - Removes files from api_calls before JSON encoding, so the request is properly formatted

v1.0.1 (2016-03-25)
-------------------

  - fix for __eq__ comparison in channels using '#' in channel name
  - added copyright info to the LICENSE file

v1.0.0 (2016-02-28)
-------------------

  - the ``api_call`` function now returns a decoded JSON object, rather than a JSON encoded string
  - some ``api_call`` calls now call actions on the parent server object:
    - ``im.open``
    - ``mpim.open``, ``groups.create``, ``groups.createChild``
    - ``channels.create``, `channels.join``

v0.18.0 (2016-02-21)
--------------------

  - Moves to use semver for versioning
  - Adds support for private groups and MPDMs
  - Switches to use requests instead of urllib
  - Gets Travis CI integration working
  - Fixes some formatting issues so the code will work for python 2.6
  - Cleans up some unused imports, some PEP-8 fixes and a couple bad default args fixes

v0.17 (2016-02-15)
------------------

  - Fixes the server so that it doesn't add duplicate users or channels to its internal lists, https://github.com/slackapi/python-slackclient/commit/0cb4bcd6e887b428e27e8059b6278b86ee661aaa
  - README updates:
    - Updates the URLs pointing to Slack docs for configuring authentication, https://github.com/slackapi/python-slackclient/commit/7d01515cebc80918a29100b0e4793790eb83e7b9
    - s/channnels/channels, https://github.com/slackapi/python-slackclient/commit/d45285d2f1025899dcd65e259624ee73771f94bb
  - Adds users to the local cache when they join the team, https://github.com/slackapi/python-slackclient/commit/f7bb8889580cc34471ba1ddc05afc34d1a5efa23
  - Fixes urllib py 2/3 compatibility, https://github.com/slackapi/python-slackclient/commit/1046cc2375a85a22e94573e2aad954ba7287c886



.. include:: metadata.rst