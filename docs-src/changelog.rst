==============================================
Changelog
==============================================

v2.3.1 (2019-10-29)
-------------------
**Updates**

1. [WebClient] Fixing a regression that causes the client to close sessions prematurely. #544 (Thanks @fatih-acar!) 
2. [WebClient] Adding required missing `view` param to views.update Web API method. #542

v2.3.0 (2019-10-22)
-------------------
**New Features**

1. [WebClient] Adding new views.publish Web API method. #540

**Updates**

1. [WebClient] Some server responses don't return json. Correcting initial assumption. #540
2. [Maintenance] Add `py.typed` to mark the library to support type hinting #524s

v2.2.1 (2019-10-08)
-------------------
**Updates**

1. [Docs] Fix Indentation of Code Snippets in README.md #525 (Thanks @abhishekjiitr)
2. [WebClient] Fix Web Client custom iterator #521 (Thanks @smaeda-ks)
3. [WebClient] Oauth previously failed to pass along credentials properly. This is fixed now. #527
4. [WebClient] When a SlackApiError occurs we're now passing the entire SlackResponse into the exception. #527

v2.2.0 (2019-09-25)
-------------------
**New Features**

1. [WebClient] Adding new admin and remote files API methods. #501
2. [WebClient] Adding new view API methods. #517

**Updates**

1. [Message Builders] Update BlockAttachment to not send invalid JSON due to fields attribute #473 (Thanks @paul-griffith)
2. [Docs] Add RTM section for docs v2 #477 (Thanks @shanedewael)
3. [Docs] Fix typo; recieved -> received #478 (Thanks @joakimnordling)
4. [Docs] Fix block kit link & update docs #484 (Thanks @clavin)
5. [RTMClient] Return callback from `RTMClient.run_on` #490 (Thanks @clavin)
6. [Docs] Fix link to Auth Guide in readme #498 (Thanks @asherf)
7. [Docs] Fix missing word and typo #512 (Thanks @marks)
8. [Message Builders] bugfix for value length in button elements #514 (Thanks @avanderm)
9. [Docs] Fixes formatting #515 (Thanks @vpetersson)
10. [Docs] Improve a code snippet on README #516 (Thanks @seratch)
11. [WebClient] Fixed an OAuth Headers bug and made the `token` param optional. #517

v2.1.0 (2019-07-01)
-------------------
**New Features**

1. Type-hinted helper classes for building messages in v2 #400 (Thanks @paul-griffith)

**Breaking Changes**

1. [RTMClient] Converted the `RTMClient#typing()` function to async #446

**Updates**

1. [RTMClient] Handle case in which aiohttp closes the websocket due to lack of ping responses. #453 (Thanks @flyte)
2. Modify package identifier in user agent to match v1.x identifier #418 (Thanks @aoberoi)
3. [WebClient] Fixed typo in Scheduled message #428 & #435 (Thanks @splinterific)
4. Transform install_requires of 'aiodns' into extras_require. #440 (Thanks @staticdev)

**Thank you!!**
To everyone who's opened, commented or reacted to an issue; this project is better because of you!
Thank you for helping the Slack community!

v2.0.0 (2019-04-29)
-------------------
`Original RFC <https://github.com/slackapi/python-slackclient/issues/384>`_

`v2 PR <https://github.com/slackapi/python-slackclient/pull/394>`_

**New Features**

1. Client Decomposition: We’ve split the client into two.

  a. WebClient: A HTTP client focused on Slack's Web API.
  b. RTMClient: A websocket client focused on Slack's RTM API.

2. RTMClient: Completely redesigned, this client allows you to link your application's callbacks to corresponding Slack events.
3. WebClient: The WebClient now provides built-in methods for Slack's Web API. These methods act as helpers enabling you to focus less on how the request is constructed. Here are a few things that this provides:
  
  a. Basic information about each method through the docstring.
  b. Easy File Uploads: You can now pass in the location of a file and the library will handle opening and retrieving the file object to be transmitted.
  c. Token type validation: This gives you better error messaging when you're attempting to consume an api method that your token doesn't have access to.
  d. Constructs requests using Slack's preferred HTTP methods and content-types.

**Breaking Changes:**
If you're migrating from v1.x of slackclient to v2.x, Please follow our migration guide to ensure your app continues working after updating.

`Check out the Migration Guide here! <https://github.com/slackapi/python-slackclient/wiki/Migrating-to-2.x>`_

**Thank you!**
This release would not have been possible without the support of our community. Thank you to everyone who’s contributed to this release.


v1.3.1 (2019-02-28)
-------------------

- Lock websocket-client version to < 0.55.0: temp fix for #385


v1.3.0 (2018-09-11)
-------------------

## New Features
- Adds support for short lived tokens and automatic token refresh #347 (Thanks @roach!)

## Other
- update RTM rate limiting comment and error message #308 (Thanks @benoitlavigne!)
- Use logging instead of traceback #309 (Thanks @harlowja!)
- Remove Python 3.3 from test environments #346 (Thanks @roach!)
- Enforced linting when using VSCode. #347 (Thanks @roach!)


v1.2.1 (2018-03-26)
-------------------

- Added rate limit handling for rtm connections (thanks @jayalane!)


v1.2.0 (2018-03-20)
-------------------

- You can now tell the RTM client to automatically reconnect by passing `auto_reconnect=True`

v1.1.3 (2018-03-01)
-------------------

- Fixed another API param encoding bug. It encodes things properly now.

v1.1.2 (2018-01-31)
-------------------

- Fixed an encoding issue which was encoding some Web API params incorrectly (sorry)

v1.1.1 (2018-01-30)
-------------------

 - Adds HTTP response headers to `api_call` responses to expose things like rate limit info
 - Moves `token` into auth header rather than request params

v1.1.0 (2017-11-21)
-------------------

 - Aadds new SlackClientError and ResponseParseError types to describe errors - thanks @aoberoi!
 - Fix Build Error (#245) - thanks @stasfilin!
 - include email as user property (#173) - thanks @acaire!
 - Add http reply into slack login and slack connection error (#216) - thanks @harlowja!
 - Removed unused exception class (#233)
 - Fix rtm_send_message bug (#225) - thanks @kt5356!
 - Allow use of custom parameters on rtm_connect() (#210) - thanks @kamushadenes!
 - Fix link to rtm.connect docs (#223) - @sampart!

v1.0.9 (2017-08-31)
-------------------

  - Fixed rtm_send_message ID bug introduced in 1.0.8

v1.0.8 (2017-08-31)
-------------------

  - Added rtm.connect support

v1.0.7 (2017-08-02)
-------------------

  - Fixes an issue where connecting over RTM to large teams may result in “Websocket URL expired” errors
  - A load of packaging improvements

v1.0.6 (2017-06-12)
-------------------

  - Added proxy support (thanks @timfeirg!)
  - Tidied up docs (thanks @schlueter!)
  - Added tox settings for Python 3 testing (thanks @cclauss!)

v1.0.5 (2017-01-23)
-------------------

  - Allow RTM Channel.send_message to reply to a thread
  - Index users by ID instead of Name (non-breaking change)
  - Added timeout to api calls.
  - Fixed a typo about token access in auth.rst, thanks @kelvintaywl!
  - Added Message Threads to the docs

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

v0.17.0 (2016-02-15)
--------------------

  - Fixes the server so that it doesn't add duplicate users or channels to its internal lists, https://github.com/slackapi/python-slackclient/commit/0cb4bcd6e887b428e27e8059b6278b86ee661aaa
  - README updates:
    - Updates the URLs pointing to Slack docs for configuring authentication, https://github.com/slackapi/python-slackclient/commit/7d01515cebc80918a29100b0e4793790eb83e7b9
    - s/channnels/channels, https://github.com/slackapi/python-slackclient/commit/d45285d2f1025899dcd65e259624ee73771f94bb
  - Adds users to the local cache when they join the team, https://github.com/slackapi/python-slackclient/commit/f7bb8889580cc34471ba1ddc05afc34d1a5efa23
  - Fixes urllib py 2/3 compatibility, https://github.com/slackapi/python-slackclient/commit/1046cc2375a85a22e94573e2aad954ba7287c886



.. include:: metadata.rst
