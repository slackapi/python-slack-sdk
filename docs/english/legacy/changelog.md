# Changelog

## v3.0.0 (2020-11-09)

This is the first stable version of [slack_sdk](https://pypi.org/project/slack-sdk/) v3. The remarkable updates in this major version are:
-   Newly added OAuth flow support
-   Better async/sync separation for `WebClient` and `WebhookClient`
-   Renamed packages (from `slack` to `slack_sdk`) with deprecation warnings

Refer to [v3.0.0 milestone](https://github.com/slackapi/python-slack-sdk/milestone/10?closed=1) and [the docs website](/tools/python-slack-sdk/) for details. If you're a `slackclient` user, the migration guide for `slackclient` v2.x users is available at http://localhost:3000/python-slack-sdk/v3-migration.

## v2.9.3 (2020-10-20)

Refer to [v2.9.3 milestone](https://github.com/slackapi/python-slackclient/milestone/20?closed=1) to know the complete list of the issues resolved by this release.

**Updates**

-  \[Block Kit\] #851 #852 Set default_type for HeaderBlock text - Thanks \@fwump38
-  \[Block Kit\] #853 #854 Enable to use input blocks in Home tab views - Thanks \@fwump38
-  \[RTMClient\] #857 #846 RTMClient does not pass timeout value to WebClient - Thanks \@Luden \@seratch

## v2.9.2 (2020-10-09)

Refer to [v2.9.2 milestone](https://github.com/slackapi/python-slackclient/milestone/19?closed=1) to know the complete list of the issues resolved by this release.

**Updates**

-  \[Block Kit\] #841 Dispatch Action in Input blocks - Thanks \@seratch
-  \[WebClient\] #838 Add apps.event.authorizations.list and other APIs - Thanks \@seratch
-  \[WebClient\]\[WebhookClient\] #829 Improve error body parser to handle no charset responses - Thanks \@adamchainz \@seratch
-  \[Block Kit\] #824 Correct text field validation in Header blocks - Thanks \@seratch

## v2.9.1 (2020-09-23)

Refer to [v2.9.1 milestone](https://github.com/slackapi/python-slackclient/milestone/18?closed=1) to know the complete list of the issues resolved by this release.

**Updates**

- \[WebClient\]\[WebhookClient\] #820 #821 #822 The proxy option in WebClient/WebhookClient no longer works - Thanks \@seratch

## v2.9.0 (2020-09-17)

Refer to [v2.9.0 milestone](https://github.com/slackapi/python-slackclient/milestone/17?closed=1) to know the complete list of the issues resolved by this release.

**Updates**

-  \[WebClient\] #811 Add workflows.\* API support - Thanks \@misscoded
-  \[WebClient\] #810 #809 Only set default filename in files_upload if file is an instance of str - Thanks \@csaska

## v2.8.2 (2020-09-04)

Refer to [v2.8.2 milestone](https://github.com/slackapi/python-slackclient/milestone/16?closed=1) to know the complete list of the issues resolved by this release.

**Updates**

-  \[WebClient\] #795 #794 Add admin.conversations.\* API methods in WebClient/AsyncWebClient - Thanks \@ruberVulpes
-  \[WebClient\] #796 Fix a link to the Static options documentation - Thanks \@Jamim

## v2.8.1 (2020-08-28)

Refer to [v2.8.1 milestone](https://github.com/slackapi/python-slackclient/milestone/15?closed=1) to know the complete list of the issues resolved by this release.

**Updates**

-  \[WebClient\] #778 #779 Adding support for View objects for views.push/update/publish - Thanks \@ruberVulpes
-  \[WebClient\] #786 Fix admin.conversations.restrictAccess.\* methods to match documentation - Thanks \@ruberVulpes

## v2.8.0 (2020-08-06)

Refer to [v2.8.0 milestone](https://github.com/slackapi/python-slackclient/milestone/14?closed=1) to know the complete list of the issues resolved by this release.

**New Features**

-  \[WebClient\] #765 #766 Introduce AsyncWebClient/AsyncWebhookClient providing coroutines - Thanks \@seratch
-  \[Block Kit\] #767 #768 Add \"header\" block support - Thanks \@mwbrooks

**Updates**

-  \[WebClient\] #738 Add HTTP_PROXY, HTTPS_PROXY env variable support in async WebClient - Thanks \@iamtofr \@seratch
-  \[WebClient\] #769 #773 Enable User-Agent to have additional info part - Thanks \@seratch
-  \[WebClient\] #770 #771 Fix a bug where `files.upload`\'s file param doesn\'t accept bytes data - Thanks \@seratch

## v2.7.3 (2020-07-20)

Refer to [v2.7.3 milestone](https://github.com/slackapi/python-slackclient/milestone/13?closed=1) to know the complete list of the issues resolved by this release.

**Updates**

-  \[WebClient\] #754 Fix #729 Add admin.conversations.restrictAccess.\*, conversations.mark API - Thanks \@ruberVulpes \@kian2attari
-  \[WebClient\] #758 Fix #757 Add admin.usergroups.addTeams, calls.participants.remove API - Thanks \@seratch
-  \[WebClient\] #727 Fix #645 Unclosed client session - Thanks \@NoAnyLove \@jourdanrodrigues
-  \[WebClient\] #745 Fix #744 a validation logic bug in DatePickerElement - Thanks \@dzudi941
-  \[WebClient\] #752 Fix #733 Better error handling when getting TimeoutError in RTMClient#start() - Thanks \@liorblob \@seratch
-  \[WebClient\] #751 Fix #718 by handling unexpected response body format - Thanks \@jeffbuswell \@seratch

## v2.7.2 (2020-06-23)

Refer to [v2.7.2 milestone](https://github.com/slackapi/python-slackclient/milestone/12?closed=1) to know the complete list of the issues resolved by this release.

**Updates**

-  \[WebClient\] Fix #728 by adding bytearray support in files_upload (sync mode) - Thanks \@sofya-salmanova \@seratch
-  \[WebClient\] #726 Fix InputBlock.hint validation failure - Thanks \@jourdanrodrigues
-  \[WebClient\] #723 Correct the default value of InputBlock.label, hint - Thanks \@jourdanrodrigues

## v2.7.1 (2020-06-04)

This release includes the fixes for regression bugs in `WebClient` since v2.6.0. Refer to [v2.7.1 milestone](https://github.com/slackapi/python-slackclient/milestone/11?closed=1) to know the complete list of the issues resolved by this release.

**Updates**

-  \[WebClient\] #716 #712 Support timeout in sync sync web clients - Thanks \@DanialErfanian \@seratch
-  \[WebClient\] #713 Support custom SSL context in sync sync web clients - Thanks \@austinbutler
-  \[WebClient\] #715 #714 Support proxy in sync sync web clients - Thanks \@austinbutler \@seratch

## v2.7.0 (2020-06-02)

Refer to [v2.7.0 milestone](https://github.com/slackapi/python-slackclient/milestone/6?closed=1) to know the complete list of the issues resolved by this release.

**New Features**

-  \[WebhookClient\] #707 #270 #531 Add `WebhookClient` for Incoming Webhooks & response_url - Thanks \@seratch \@chubz \@Ambro17

**Updates**

-  \[WebClient\] #704 #695 Add `calls\_\*` methods to `WebClient` and `CallBlock` in Block Kit classes - Thanks \@seratch
-  \[WebClient\] #710 #536 Allow Tokens to be specified per request - Thanks \@seratch
-  \[WebClient\] #709 #708 Add default_to_current_conversation in conversations_select elements - Thanks \@seratch

## v2.6.2 (2020-05-28)

Refer to [v2.6.2 milestone](https://github.com/slackapi/python-slackclient/milestone/9?closed=1) to know the complete details of this release.

**Updates**

- \[WebClient\] #705 WebClient\'s paginated API calls may fail with no params - Thanks \@seratch

## v2.6.1 (2020-05-24)

This patch release is a quick fix for #701, a major issue that affected RTMClient users in v2.6.0. The malfunction was introduced by #667 trying to address #558 #619. Those issues were reopened and will be resolved by another approach. Refer to [v2.6.1 milestone](https://github.com/slackapi/python-slackclient/milestone/8) to know the complete list of the issues resolved by this release.

**Updates**

- \[RTMClient\] #701 RTMClient drops some messages when they come in rapid succession - Thanks \@pbrackin \@seratch

## v2.6.0 (2020-05-21)

Refer to [v2.6.0 milestone](https://github.com/slackapi/python-slackclient/milestone/5?closed=1) to know the complete list of the issues resolved by this release.

**New Features**

-  \[Block Kit\] #659 Add complete supports for Block Kit components and fixed a few existing bugs as well (#500 #519 #623 #632 #635 #639 #676 #699) - Thanks \@seratch \@diurnalist \@ruberVulpes \@jeremyschulman \@e271828- \@RodneyU215
-  \[Signature\] #686 Add slack.signature.SignatureVerifier for request verification - Thanks \@seratch
-  \[WebClient\] #682 Add missing Grid admin APIs (`admin.usergroups.\*`, `admin.users.\*`, `admin.apps.\*`) - Thanks \@stevengill \@seratch

**Updates**

-  \[WebClient\]\[RTMClient\] Fixed a bunch of the currency issues this SDK had (#429 #463 #492 #497 #530 #569 #605 #613 #626 #630 #631 #633 #669) - Thanks \@seratch \@aaguilartablada \@aoberoi \@stevengill \@marshallino16
-  \[WebClient\] #681 #560 Enable using bool values for request parameters - Thanks \@roman-kachanovsky \@seratch
-  \[WebClient\] #661 #678 Improve handling of required \"ids\" parameters (e.g., channel_ids, users) - Thanks \@seratch
-  \[WebClient\] #680 Add non-conversation API deprecation warnings - Thanks \@seratch
-  \[WebClient\] #671 #670 Enable passing None values for request parameters (they used to result in errors) - Thanks \@yuji38kwmt \@seratch
-  \[WebClient\] #673 Fix #672 files.upload fails with a filepath containing multi byte chars - Thanks \@yuji38kwmt \@seratch
-  \[WebClient\] #656 Fix #594 preview_image for files.remote.add API method is not properly supported - Thanks \@Eothred \@seratch
-  \[Maintenance\] #618 Add py.typed file to package distribution - Thanks \@JKillian
-  \[WebClient\] #599 Strip token string parameters of whitespace - Thanks \@TheFrozenFire
- \[WebClient\] #692 Fix superfluous_charset warnings since v2.4.0 - Thanks \@seratch
- \[WebClient\] #652 Update oauth_v2_access to include redirect_uri (as optional) - Thanks \@tomasreimers

## v2.5.0 (2019-12-09)

**New Features**

- \[WebClient\] Adding new oauth.v2.access Web API method. #577

## v2.4.0 (2019-11-27)

**New Features**

- \[WebClient\] Adding new admin.\* Web API methods. #571

**Updates** 

- \[WebClient\] We\'re no longer validating token types for Web API methods. Improves compatibility with granular bot permissions. #568 (Thanks \@Smotko) 
- \[WebClient\] Correcting typos in descriptions #554 (Thanks \@phamk)
- \[WebClient\] Fixed \'iteracting\' typo in library file headers #564 (Thanks \@acabey)
- \[Message Builders\] Remove value from LinkButtonElement #563 (Thanks \@pedroma)

## v2.3.1 (2019-10-29)

**Updates**

-  \[WebClient\] Fixing a regression that causes the client to close sessions prematurely. #544 (Thanks \@fatih-acar!)
- \[WebClient\] Adding required missing view param to views.update Web API method. #542

## v2.3.0 (2019-10-22)

**New Features**

- \[WebClient\] Adding new views.publish Web API method. #540

**Updates**

-  \[WebClient\] Some server responses don\'t return json. Correcting initial assumption. #540
-  \[Maintenance\] Add `py.typed` to mark the library to support type hinting #524s

## v2.2.1 (2019-10-08)

**Updates**

-  \[Docs\] Fix Indentation of Code Snippets in README.md #525 (Thanks \@abhishekjiitr)
-  \[WebClient\] Fix Web Client custom iterator #521 (Thanks \@smaeda-ks)
-  \[WebClient\] Oauth previously failed to pass along credentials properly. This is fixed now. #527
-  \[WebClient\] When a SlackApiError occurs we\'re now passing the entire SlackResponse into the exception. #527

## v2.2.0 (2019-09-25)

**New Features**

-  \[WebClient\] Adding new admin and remote files API methods. #501
-  \[WebClient\] Adding new view API methods. #517

**Updates**

-  \[Message Builders\] Update BlockAttachment to not send invalid JSON due to fields attribute #473 (Thanks \@paul-griffith)
-  \[Docs\] Add RTM section for docs v2 #477 (Thanks \@shanedewael)
-  \[Docs\] Fix typo; recieved -\> received #478 (Thanks \@joakimnordling)
-  \[Docs\] Fix block kit link & update docs #484 (Thanks \@clavin)
-  \[RTMClient\] Return callback from `RTMClient.run_on` #490 (Thanks \@clavin)
-  \[Docs\] Fix link to Auth Guide in readme #498 (Thanks \@asherf)
-  \[Docs\] Fix missing word and typo #512 (Thanks \@marks)
-  \[Message Builders\] bugfix for value length in button elements #514 (Thanks \@avanderm)
-  \[Docs\] Fixes formatting #515 (Thanks \@vpetersson)
- \[Docs\] Improve a code snippet on README #516 (Thanks \@seratch)
- \[WebClient\] Fixed an OAuth Headers bug and made the `token` param optional. #517

## v2.1.0 (2019-07-01)

**New Features**

- Type-hinted helper classes for building messages in v2 #400 (Thanks \@paul-griffith)

**Breaking Changes**

- \[RTMClient\] Converted the `RTMClient#typing()` function to async #446

**Updates**

-  \[RTMClient\] Handle case in which aiohttp closes the websocket due to lack of ping responses. #453 (Thanks \@flyte)
-  Modify package identifier in user agent to match v1.x identifier #418 (Thanks \@aoberoi)
-  \[WebClient\] Fixed typo in Scheduled message #428 & #435 (Thanks \@splinterific)
-  Transform install_requires of \'aiodns\' into extras_require. #440 (Thanks \@staticdev)

**Thank you!** To everyone who has opened, commented or reacted to an issue; this project is better because of you! Thank you for helping the Slack community!

## v2.0.0 (2019-04-29)

[Original RFC](https://github.com/slackapi/python-slackclient/issues/384)

[v2 PR](https://github.com/slackapi/python-slackclient/pull/394)

**New Features**

-  Client Decomposition: We've split the client into two.
    - WebClient: A HTTP client focused on Slack\'s Web API.
    - RTMClient: A websocket client focused on Slack\'s RTM API.
-  RTMClient: Completely redesigned, this client allows you to link your application\'s callbacks to corresponding Slack events.
-  WebClient: The WebClient now provides built-in methods for Slack\'s Web API. These methods act as helpers enabling you to focus less on how the request is constructed. Here are a few things this provides:
    - Basic information about each method through the docstring.
    - Easy File Uploads: You can now pass in the location of a file and the library will handle opening and retrieving the file object to be transmitted.
    - Token type validation: This gives you better error messaging when you\'re attempting to consume an API method that your token doesn\'t have access to.
    - Constructs requests using Slack\'s preferred HTTP methods and content-types.

**Breaking Changes:** If you\'re migrating from v1.x of slackclient to v2.x, Please follow our [migration guide](https://github.com/slackapi/python-slackclient/wiki/Migrating-to-2.x) to ensure your app continues working after updating.

**Thank you!** This release would not have been possible without the support of our community. Thank you to everyone who has contributed to this release.

## v1.3.1 (2019-02-28)

-   Lock websocket-client version to \< 0.55.0: temp fix for #385

## v1.3.0 (2018-09-11)

**New Features** 

- Adds support for short lived tokens and automatic token refresh #347 (Thanks \@roach!)

**Other**

- Update RTM rate limiting comment and error message #308 (Thanks \@benoitlavigne!) 
- Use logging instead of traceback #309 (Thanks \@harlowja!) 
- Remove Python 3.3 from test environments #346 (Thanks \@roach!) 
- Enforced linting when using VSCode. #347 (Thanks \@roach!)

## v1.2.1 (2018-03-26)

-   Added rate limit handling for rtm connections (thanks \@jayalane!)

## v1.2.0 (2018-03-20)

-   You can now tell the RTM client to automatically reconnect by passing `auto_reconnect=True`

## v1.1.3 (2018-03-01)

-   Fixed another API param encoding bug. It encodes things properly now.

## v1.1.2 (2018-01-31)

-   Fixed an encoding issue which was encoding some Web API params incorrectly

## v1.1.1 (2018-01-30)

-   Adds HTTP response headers to `api_call` responses to expose things like rate limit info
-   Moves `token` into auth header rather than request params

## v1.1.0 (2017-11-21)

-   Adds new SlackClientError and ResponseParseError types to describe errors - thanks \@aoberoi!
-   Fix Build Error (#245) - thanks \@stasfilin!
-   Include email as user property (#173) - thanks \@acaire!
-   Add http reply into slack login and slack connection error (#216) - thanks \@harlowja!
-   Removed unused exception class (#233)
-   Fix rtm_send_message bug (#225) - thanks \@kt5356!
-   Allow use of custom parameters on rtm_connect() (#210) - thanks \@kamushadenes!
-   Fix link to rtm.connect docs (#223) - \@sampart!

## v1.0.9 (2017-08-31)

-   Fixed rtm_send_message ID bug introduced in 1.0.8

## v1.0.8 (2017-08-31)

-   Added rtm.connect support

## v1.0.7 (2017-08-02)

-   Fixes an issue where connecting over RTM to large teams may result in "Websocket URL expired" errors
-   A bunch of packaging improvements

## v1.0.6 (2017-06-12)

-   Added proxy support (thanks \@timfeirg!)
-   Tidied up docs (thanks \@schlueter!)
-   Added tox settings for Python 3 testing (thanks \@cclauss!)

## v1.0.5 (2017-01-23)

-   Allow RTM Channel.send_message to reply to a thread
-   Index users by ID instead of Name (non-breaking change)
-   Added timeout to api calls
-   Fixed a typo about token access in auth.rst, thanks \@kelvintaywl!
-   Added Message Threads to the docs

## v1.0.4 (2016-12-15)

-   Fixed the ability to search for a user by ID

## v1.0.3 (2016-12-13)

-   Fixed an issue causing RTM connections to fail for large teams

## v1.0.2 (2016-09-22)

-   Removed unused ping counter
-   Fixed contributor guidelines links
-   Updated documentation
-   Fix bug preventing API calls requiring a file ID
-   Removes files from api_calls before JSON encoding, so the request is properly formatted

## v1.0.1 (2016-03-25)

-   Fix for \_\_eq\_\_ comparison in channels using \'#\' in channel name
-   Added copyright info to the LICENSE file

## v1.0.0 (2016-02-28)

-   The `api_call` function now returns a decoded JSON object, rather than a JSON encoded string
-   Some `api_call` calls now call actions on the parent server object:
    -   `dm.open`
    -   `mpdm.open`, `groups.create`, `groups.createChild`
    -   `channels.create`, `channels.join`

## v0.18.0 (2016-02-21)

-   Moves to use semver for versioning
-   Adds support for private groups and MPDMs
-   Switches to use requests instead of urllib
-   Gets Travis CI integration working
-   Fixes some formatting issues so the code will work for python 2.6
-   Cleans up some unused imports, some PEP-8 fixes and a couple bad default args fixes

## v0.17.0 (2016-02-15)

-   Fixes the server so that it doesn\'t add duplicate users or channels to its internal lists, https://github.com/slackapi/python-slackclient/commit/0cb4bcd6e887b428e27e8059b6278b86ee661aaa
-   README updates:
    -   Updates the URLs pointing to Slack docs for configuring authentication, https://github.com/slackapi/python-slackclient/commit/7d01515cebc80918a29100b0e4793790eb83e7b9 
    -   s/channnels/channels, https://github.com/slackapi/python-slackclient/commit/d45285d2f1025899dcd65e259624ee73771f94bb
    -   Adds users to the local cache when they join the team, https://github.com/slackapi/python-slackclient/commit/f7bb8889580cc34471ba1ddc05afc34d1a5efa23
    -   Fixes urllib py 2/3 compatibility, https://github.com/slackapi/python-slackclient/commit/1046cc2375a85a22e94573e2aad954ba7287c886
