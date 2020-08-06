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

Install necessary Python runtimes for development/testing. You can rely on Travis CI builds for testing with various major versions. https://github.com/slackapi/python-slackclient/blob/main/.travis.yml

```bash
$ pyenv install -l | grep -v "-e[conda|stackless|pypy]"

$ pyenv install 3.8.5 # select the latest patch version
$ pyenv local 3.8.5

$ pyenv versions
  system
  3.6.10
  3.7.7
* 3.8.5 (set by /path-to-python-slackclient/.python-version)

$ pyenv rehash
```

Then, you can create a new Virtual Environment this way:

```
$ python -m venv env_3.8.5
$ source env_3.8.5/bin/activate
```

## Tasks

### Testing (Unit Tests)

When you make changes to this SDK, please write unit tests verifying if the changes work as you expected. You can easily run all the tests by running the command. The `validate` command runs Flake8 (static code analyzer), Black (code formatter), and unit tests in the `tests` directory for you.

```bash
python setup.py validate # run all

# run a single test
python setup.py validate \
  --test-target tests/web/test_web_client.py
```

You can rely on Travis CI builds for running the tests on a variety of Python runtimes.

### Testing (Integration Tests with Real Slack APIs)

This project also has integration tests that verify the SDK works with the Slack API platform. As a preparation, you need to set [the required env variables](https://github.com/slackapi/python-slackclient/blob/main/integration_tests/env_variable_names.py) properly. You don't need to setup all of them if you just want to run some of the tests. Commonly, `SLACK_SDK_TEST_BOT_TOKEN` and `SLACK_SDK_TEST_USER_TOKEN` are used for running `WebClient` tests.

```bash
python setup.py run_integration_tests # run all

# run a single test
python setup.py run_integration_tests \
  --test-target integration_tests/web/test_web_client.py
```

### Generating Documentation

The documentation is generated from the source and templates in the `docs-src` directory. The generated documentation
gets committed to the repo in `docs` and also published to a GitHub Pages website.

You can generate the documentation by running `./docs.sh`.

### Releasing

1. Create the commit for the release:

- Bump the version number in adherence to [Semantic Versioning](http://semver.org/) in `slackclient/version.py`.
- Add a description of changes to the Changelog in `docs-src/changelog.rst`
- Build the docs with `./docs.sh`.
- Cut off a branch for the release with `git branch -b v2.5.0-release`
- Set the version in `slack/version.py` (e.g., `2.5.0`)
- Commit with a message including the new version number: `git commit -m'version 2.5.0'`.
- Push the commit to a branch and create a PR to sanity check.
- Merge in release PR after receiving at least one approval from other maintainers.
- Create a git tag for the release. For example `git tag 2.5.0`.
- Push the tag up to github with `git push origin --tags`

2. Distribute the release

- Use the latest stable Python runtime
  - `python -m venv env`
  - `python setup.py upload`
- Create a GitHub Release. You will select the commit with updated version number (e.g. `version 2.5.0`) to associate with the tag, and name the tag after this version (e.g. `v2.5.0`). This will also serve as a Changelog for the project. Add a description of changes to the Release. Mention Issue and PR #'s and @-mention contributors.

```markdown
Refer to [v{version} milestone](https://github.com/slackapi/python-slackclient/milestone/{TODO}?closed=1) to know the complete list of the issues resolved by this release.

**Updates**

1. [WebClient] #111 Make an awesome change - Thanks @SlackHQ
1. [RTMClient] #222 Make an awesome change - Thanks @SlackAPI

**All Changes**

https://github.com/slackapi/python-slackclient/compare/{the previous release version tag}...{the release version tag}
```

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
