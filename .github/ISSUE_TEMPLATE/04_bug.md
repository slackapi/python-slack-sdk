---
name: Bug
about: Report the SDK bug
title: (Set a clear title describing the issue)
labels: 'bug'
assignees: ''
---

## Bug Report

(Filling out the following details about bugs will help us solve your issue sooner.)

### Reproducible in:

```bash
pip freeze | grep slack
python --version
sw_vers && uname -v # or `ver`
```

#### The Slack SDK version

(Paste the output of `pip freeze | grep slack`)

#### Python runtime version

(Paste the output of `python --version`)

#### OS info

(Paste the output of `sw_vers && uname -v` on macOS/Linux or `ver` on Windows OS)

#### Steps to reproduce:

(Share the commands to run, source code, and project settings (e.g., setup.py))

1.
2.
3.

### Expected result:

(Tell what you expected to happen)

### Actual result:

(Tell what actually happened with logs, screenshots)

## Requirements (place an `x` in each of the `[ ]`)

(For general questions/issues about Slack API platform or its server-side, could you submit questions at https://my.slack.com/help/requests/new instead. :bow:)

* [ ] This is a bug specific to this SDK project.
* [ ] I've read and understood the [Contributing guidelines](https://github.com/slackapi/python-slackclient/blob/main/.github/contributing.md) and have done my best effort to follow them.
* [ ] I've read and agree to the [Code of Conduct](https://slackhq.github.io/code-of-conduct).
* [ ] I've searched for any related issues and avoided creating a duplicate issue [here](https://github.com/slackapi/python-slackclient/issues).