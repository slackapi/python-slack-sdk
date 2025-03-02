// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
    sidebarPythonSDK: [
        {
            type: "doc",
            id: "index",
            label: "Python Slack SDK",
            className: "sidebar-title",
        },
        "installation",
        "web",
        "webhook",
        "socket-mode",
        "oauth",
        "audit-logs",
        "rtm",
        "scim",
        { type: "html", value: "<hr>" },
        {
            type: "category",
            label: "Legacy slackclient v2",
            items: [
                "legacy/index",
                "legacy/auth",
                "legacy/basic_usage",
                "legacy/conversations",
                "legacy/real_time_messaging",
                "legacy/faq",
                "legacy/changelog",
            ],
        },
        "v3-migration",
        { type: "html", value: "<hr>" },
        {
            type: "category",
            label: "Tutorials",
            items: ["tutorial/uploading-files", "tutorial/understanding-oauth-scopes"],
        },
        { type: "html", value: "<hr>" },
        {
            type: "link",
            label: "Reference",
            href: "https://tools.slack.dev/python-slack-sdk/api-docs/slack_sdk/",
        },
        { type: "html", value: "<hr>" },
        {
            type: "link",
            label: "Release notes",
            href: "https://github.com/slackapi/python-slack-sdk/releases",
        },
        {
            type: "link",
            label: "Code on GitHub",
            href: "https://github.com/SlackAPI/python-slack-sdk",
        },
        {
            type: "link",
            label: "Contributors Guide",
            href: "https://github.com/SlackAPI/python-slack-sdk/blob/main/.github/contributing.md",
        },
    ],
};

export default sidebars;
