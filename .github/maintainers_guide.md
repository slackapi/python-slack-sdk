# Maintainers Guide

This document describes tools, tasks and workflow that one needs to be familiar with in order to effectively maintain
this project. If you use this package within your own software as is but don't plan on modifying it, this guide is
**not** for you.

## Tools

### Python (and friends)

Not surprisingly, you will need to have Python installed on your system to work on this package. We support non-EOL,
stable versions of CPython. The current supported versions are listed in the CI configurations (e.g. `.travis.yml`).
At a minimum, you should have the latest version of Python 2 and the latest version of Python 3 to develop against.
It's tricky to set up a system that has more than that, so you can lean on the CI servers to test changes on the
in-between versions for you.

You should also make sure you have the latest versions of `pip`, `setuptools`, `virtualenv`, `wheel`, `twine` and
[`tox`](https://tox.readthedocs.io/en/latest/) installed with your version of Python.

On macOS, the easiest way to install these tools is by using [Homebrew](https://brew.sh/) and installing the `python`
and `python3` packages. Some of the above packages are preinstalled and you can install the remaining on your own:
`pip install virtualenv wheel twine tox && pip3 install virtualenv twine tox`.

## Tasks

### Testing

Tox is used to run the test suite across multiple isolated versions of Python. It is configured in `tox.ini` to
run all the supported versions of Python, but when you invoke it, you should only select the versions you have on your
system. For example, on a system with Python 2.7.13 and Python 3.6.1, you would run the tests using the following
command: `tox -e flake8,py27,py36` (flake8 is a quality analysis tool).

### Generating Documentation

The documentation is generated from the source and templates in the `docs-src` directory. The generated documentation
gets committed to the repo in `docs` and also published to a GitHub Pages website.

You can generate the documentation by running `tox -e docs`.

### Releasing

1.  Create the commit for the release:
    *  Bump the version number in adherence to [Semantic Versioning](http://semver.org/) in `slackclient/version.py`.
    *  Commit with a message including the new version number. For example `1.0.6`.

2.  Distribute the release
    *  Build the distribtuions: `python setup.py sdist bdist_wheel`. This will create artifacts in the `dist` directory.
    *  Publish to PyPI: `twine upload dist/*`. You must have access to the credentials to publish.
    *  Create a GitHub Release. You will select the commit with updated version number (e.g. `1.0.6`) to assiociate with
       the tag, and name the tag after this version (e.g. `1.0.6`). This will also serve as a Changelog for the project.
       Add a description of changes to the Release. Mention Issue and PR #'s and @-mention contributors.

3.  (Slack Internal) Communicate the release internally. Include a link to the GitHub Release.

4.  Announce on Slack Team dev4slack in #slack-api

5.  (Slack Internal) Tweet? Not necessary for patch updates, might be needed for minor updates, definitely needed for
    major updates. Include a link to the GitHub Release.

## Workflow

### Versioning and Tags

This project uses semantic versioning, expressed through the numbering scheme of
[PEP-0440](https://www.python.org/dev/peps/pep-0440/).

### Branches

`master` is where active development occurs. Long running named feature branches are occasionally created for
collaboration on a feature that has a large scope (because everyone cannot push commits to another person's open Pull
Request). At some point in the future after a major version increment, there may be maintenance branches for older major
versions.

### Issue Management

Labels are used to run issues through an organized workflow. Here are the basic definitions:

*  `bug`: A confirmed bug report. A bug is considered confirmed when reproduction steps have been
   documented and the issue has been reproduced.
*  `enhancement`: A feature request for something this package might not already do.
*  `docs`: An issue that is purely about documentation work.
*  `tests`: An issue that is purely about testing work.
*  `needs feedback`: An issue that may have claimed to be a bug but was not reproducible, or was otherwise missing some information.
*  `discussion`: An issue that is purely meant to hold a discussion. Typically the maintainers are looking for feedback in this issues.
*  `question`: An issue that is like a support request because the user's usage was not correct.
*  `semver:major|minor|patch`: Metadata about how resolving this issue would affect the version number.
*  `security`: An issue that has special consideration for security reasons.
*  `good first contribution`: An issue that has a well-defined relatively-small scope, with clear expectations. It helps when the testing approach is also known.
*  `duplicate`: An issue that is functionally the same as another issue. Apply this only if you've linked the other issue by number.

**Triage** is the process of taking new issues that aren't yet "seen" and marking them with a basic level of information
with labels. An issue should have **one** of the following labels applied: `bug`, `enhancement`, `question`,
`needs feedback`, `docs`, `tests`, or `discussion`.

Issues are closed when a resolution has been reached. If for any reason a closed issue seems relevant once again,
reopening is great and better than creating a duplicate issue.

## Everything else

When in doubt, find the other maintainers and ask.