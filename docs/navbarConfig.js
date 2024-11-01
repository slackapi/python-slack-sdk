const navbar = {
  title: 'Slack Developer Tools',
  logo: {
    src: 'img/slack-logo.svg',
    href: 'https://tools.slack.dev',
  },
  items: [
    {
      type: 'dropdown',
      label: 'Bolt',
      position: 'left',
      items: [
        {
          label: 'Java',
          to: 'https://tools.slack.dev/java-slack-sdk/guides/bolt-basics',
          target: '_self',
        },
        {
          label: 'JavaScript',
          to: 'https://tools.slack.dev/bolt-js',
          target: '_self',
        },
        {
          label: 'Python',
          to: 'https://tools.slack.dev/bolt-python',
          target: '_self',
        },
      ],
    },
    {
      type: 'dropdown',
      label: 'SDKs',
      position: 'left',
      items: [
        {
          label: 'Java Slack SDK',
          to: 'https://tools.slack.dev/java-slack-sdk/',
          target: '_self',
        },
        {
          label: 'Node Slack SDK',
          to: 'https://tools.slack.dev/node-slack-sdk/',
          target: '_self',
        },
        {
          label: 'Python Slack SDK',
          to: 'https://tools.slack.dev/python-slack-sdk/',
          target: '_self',
        },
        {
          label: 'Deno Slack SDK',
          to: 'https://api.slack.com/automation/quickstart',
          target: '_self',
        },
      ],
    },
    {
      type: 'dropdown',
      label: 'Community',
      position: 'left',
      items: [
        {
          label: 'Community tools',
          to: 'https://tools.slack.dev/community-tools',
          target: '_self',
        },
        {
          label: 'Slack Community',
          to: 'https://slackcommunity.com/',
          target: '_self',
        },
      ],
    },
    {
      to: 'https://api.slack.com/docs',
      label: 'API Docs',
      target: '_self',
    },
    {
      'aria-label': 'GitHub Repository',
      className: 'navbar-github-link',
      href: 'https://github.com/slackapi',
      position: 'right',
      target: '_self',
    },
  ],
};

module.exports = navbar;
