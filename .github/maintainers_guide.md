# Maintainers Guide

This document describes tools, tasks and workflow that one needs to be familiar with in order to effectively maintain
this project. If you use this package within your own software as is but don't plan on modifying it, this guide is
**not** for you.

## Tools

### Python (and friends)

We recommend using [pyenv](https://github.com/pyenv/pyenv) for Python runtime management. If you use macOS, follow the following steps:

```bash
$ brew update
$ brew install pyenv
```

You can hook `pyenv` into your shell automatically by running `pyenv init` and following the instructions.

Install necessary Python runtimes for development/testing. It is not necessary
to install all the various Python versions we test in [continuous integration on
GitHub Actions](https://github.com/slackapi/python-slack-sdk/blob/main/.github/workflows/ci-build.yml),
but make sure you are running at least one version that we execute our tests in
locally so that you can run the tests yourself.

```bash
$ pyenv install -l | grep -v "-e[conda|stackless|pypy]"

$ pyenv install 3.9.6 # select the latest patch version
$ pyenv local 3.9.6

$ pyenv versions
  system
  3.6.10
  3.7.7
* 3.9.6 (set by /path-to-python-slack-sdk/.python-version)

$ pyenv rehash
```

Then, you can create a new [Virtual Environment](https://docs.python.org/3/tutorial/venv.html) specific to the Python version you just installed by running:

```bash
$ python -m venv env_3.9.6
$ source env_3.9.6/bin/activate
```

At this point you have a clean, Python-version-specific environment "activated" for
use just for this project. All `python` and `pip` commands run in your shell
from this point on run in the context of this virtual environment. You can
deactivate the virtual environment by running `deactivate`; it is recommended to
do so after you are done working in this project. To come back to development
work for this project again in the future, `cd` into this project directory and
run `source env_3.9.6/bin/activate` again.

The last step is to install this project's dependencies and run all unit tests; to do so, you can run

```bash
$ ./scripts/run_validation.sh 
```

Also check out [how
we configure GitHub Actions to install dependencies for this project for use in
our continuous integration](https://github.com/slackapi/python-slack-sdk/blob/v3.17.0/.github/workflows/ci-build.yml#L28-L32).

## Tasks

### Testing (Unit Tests)

When you make changes to this SDK, please write unit tests verifying if the changes work as you expected. You can easily run all the tests and formatting/linter with the below scripts.

Run all the unit tests, code formatter, and code analyzer:

```bash
$ ./scripts/run_validation.sh 
```

Run all the unit tests (no formatter nor code analyzer):

```bash
$ ./scripts/run_unit_tests.sh
```

Run a specific unit test:

```bash
$ ./scripts/run_unit_tests.sh tests/web/test_web_client.py
```

You can rely on GitHub Actions builds for running the tests on a variety of Python runtimes.

### Testing (Integration Tests with Real Slack APIs)

This project also has integration tests that verify the SDK works with the Slack API platform. As a preparation, you need to set [the required env variables](https://github.com/slackapi/python-slack-sdk/blob/main/integration_tests/env_variable_names.py) properly. You don't need to setup all of them if you just want to run some of the tests. Commonly, `SLACK_SDK_TEST_BOT_TOKEN` and `SLACK_SDK_TEST_USER_TOKEN` are used for running `WebClient` tests.

Run all integration tests:

```bash
$ ./scripts/run_integration_tests.sh
```

Run a specific integration test:

```bash
$ ./scripts/run_integration_tests.sh integration_tests/web/test_async_web_client.py
```

### Generating Documentation

The documentation is generated from the source and templates in the `docs-src` directory. The generated documentation
gets committed to the repo in `docs` and also published to a GitHub Pages website.

You can generate and preview the **SDK document pages** by running

```bash
$ ./scripts/docs.sh
$ open docs/index.html
```

Similarly you can generate and preview the **API documents for `slack_sdk` package modules** by running

```bash
$ ./scripts/generate_api_docs.sh
```

### Releasing

1. Create the commit for the release:

   - Bump the version number in adherence to [Semantic Versioning](http://semver.org/) in `slack_sdk/version.py`.
   - Build the docs with `./scripts/docs.sh` and then `./scripts/generate_api_docs.sh`.
   - Create a branch for the release with `git checkout -b v2.5.0`
   - Make a commit that includes the new version number: `git commit -m 'version 2.5.0'`.
   - Open a PR and merge after receiving at least one approval from other maintainers.
   - Create a git tag for the release. For example `git tag v2.5.0`.
   - Push the tag up to github with `git push origin --tags`

2. Distribute the release

   - Use the latest stable Python runtime
     - `python -m venv env`
     - `./scripts/deploy_to_prod_pypi_org.sh`
   - Create a GitHub Release. You will select the commit with updated version number (e.g. `version 2.5.0`) to associate with the tag, and name the tag after this version (e.g. `v2.5.0`). This will also serve as a Changelog for the project. Add a description of changes to the Release. Mention Issue and PR #'s and @-mention contributors.

   ```markdown
   Refer to [v{version} milestone](https://github.com/slackapi/python-slack-sdk/milestone/{TODO}?closed=1) to know the complete list of the issues resolved by this release.

   **Updates**

   1. [WebClient] #111 Make an awesome change - Thanks @SlackHQ
   2. [RTMClient] #222 Make an awesome change - Thanks @SlackAPI

   **All Changes**

   * All issues/pull requests: https://github.com/slackapi/python-slack-sdk/milestone/{milestone for the release}
   * All changes: https://github.com/slackapi/python-slack-sdk/compare/{the previous release version tag}...{the release version tag}
   ```

   - Close the milestone relating to the Release
   - Create the next patch version Milestone. To be used by the following release.

3. (Slack Internal) Communicate the release internally

   - Include a link to the GitHub release

4. Make announcements

   - #slack-api in dev4slack.slack.com
   - #lang-python in community.slack.com

5. (Slack Internal) Tweet by @SlackAPI

   - Not necessary for patch updates, might be needed for minor updates, definitely needed for major updates. Include a link to the GitHub release

## Workflow

### Versioning and Tags

This project uses semantic versioning, expressed through the numbering scheme of
[PEP-0440](https://www.python.org/dev/peps/pep-0440/).

### Branches

The `main` branch is where active development occurs. Long running named feature branches are occasionally created for
collaboration on a feature that has a large scope (because everyone cannot push commits to another person's open Pull
Request). At some point in the future after a major version increment, there may be maintenance branches for older major
versions.

### Issue Management

Labels are used to run issues through an organized workflow. Here are the basic definitions:

- `bug`: A confirmed bug report. A bug is considered confirmed when reproduction steps have been
  documented and the issue has been reproduced.
- `enhancement`: A feature request for something this package might not already do.
- `docs`: An issue that is purely about documentation work.
- `tests`: An issue that is purely about testing work.
- `question`: An issue that is like a support request because the user's usage was not correct.

**Triage** is the process of taking new issues that aren't yet "seen" and marking them with a basic level of information
with labels. An issue should have **one** of the following labels applied: `bug`, `enhancement`, `question`, `docs`, `tests`, or `discussion`.

Issues are closed when a resolution has been reached. If for any reason a closed issue seems relevant once again,
reopening is great and better than creating a duplicate issue.

## Everything else

When in doubt, find the other maintainers and ask.
