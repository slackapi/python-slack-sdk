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
GitHub Actions](https://github.com/slackapi/python-slack-sdk/blob/main/.github/workflows/tests.yml),
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

### Testing

#### Unit Tests

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

#### Integration Tests with Real Slack APIs

This project also has integration tests that verify the SDK works with the Slack API platform. As a preparation, you need to set [the required env variables](https://github.com/slackapi/python-slack-sdk/blob/main/integration_tests/env_variable_names.py) properly. You don't need to setup all of them if you just want to run some of the tests. Commonly, `SLACK_SDK_TEST_BOT_TOKEN` and `SLACK_SDK_TEST_USER_TOKEN` are used for running `WebClient` tests.

Run all integration tests:

```bash
$ ./scripts/run_integration_tests.sh
```

Run a specific integration test:

```bash
$ ./scripts/run_integration_tests.sh integration_tests/web/test_async_web_client.py
```

#### Develop Locally

If you want to test the package locally you can.

1. Build the package locally
   - Run
     ```bash
     scripts/build_pypi_package.sh
     ```
   - This will create a `.whl` file in the `./dist` folder
2. Use the built package
   - Example `/dist/slack_sdk-1.2.3-py2.py3-none-any.whl` was created
   - From anywhere on your machine you can install this package to a project with
     ```bash
     pip install <project path>/dist/slack_sdk-1.2.3-py2.py3-none-any.whl
     ```
   - It is also possible to include `slack_sdk @ file:///<project path>/dist/slack_sdk-1.2.3-py2.py3-none-any.whl` in a [requirements.txt](https://pip.pypa.io/en/stable/user_guide/#requirements-files) file

### Generating Documentation

See [`/docs/README`](https://github.com/slackapi/python-slack-sdk/blob/main/docs/README.md) for information on editing documentation pages.

The API reference is generated from a script. You can generate and preview the **API _reference_ documents for `slack_sdk` package modules** by running:

```bash
$ ./scripts/generate_api_docs.sh
```

### Releasing

1. Create the commit for the release:

   - Bump the version number in adherence to [Semantic Versioning](http://semver.org/) in `slack_sdk/version.py`.
   - Build the reference docs with `./scripts/generate_api_docs.sh`.
   - Create a branch for the release with `git checkout -b v2.5.0`
   - Make a commit that includes the new version number: `git commit -a -m 'version 2.5.0'`.
   - Open a PR and merge after receiving at least one approval from other maintainers.

2. Distribute the release

   - Use the latest stable Python runtime
     - `python -m venv env`
     - `./scripts/deploy_to_prod_pypi_org.sh`
   - Create a new GitHub Release from the [Releases page](https://github.com/slackapi/python-slack-sdk/releases) by clicking the "Draft a new release" button.
      - Enter the new version number updated from the commit (e.g. `v2.5.0`) into the "Choose a tag" input.
      - Ensure the tag `Target` branch is `main` (e.g `Target:main`).
      - Click the "Create a new tag: x.x.x on publish" button. This won't create your tag immediately.
      - Name the release after the version number updated from the commit (e.g. `version 2.5.0`)
      - Auto-generate the release notes by clicking the "Auto-generate release
      notes" button. This will pull in changes that will be included in your
      release.
      - Edit the resulting notes to ensure they have decent messaging that are
      understandable by non-contributors, but each commit should still have it's
      own line.
      - Ensure that this version adheres to [semantic versioning][semver]. See
      [Versioning](#versioning-and-tags) for correct version format. Version tags
      should match the following pattern: `v2.5.0`.

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
