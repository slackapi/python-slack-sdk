const navbar = {
  style: 'dark',
  title: 'Slack Developer Tools',
  logo: {
    src: 'img/slack-logo-on-white.png',
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
          to: 'https://tools.slack.dev/deno-slack-sdk/',
          target: '_self',
        },
      ],
    },
    {
      to: 'https://tools.slack.dev/slack-cli',
      label: 'Slack CLI',
      target: '_self',
    },
    {
      to: 'https://api.slack.com',
      label: 'API Docs',
      position: 'right',
      target: '_self',
    },
    {
      label: 'Developer Program',
      position: 'right',
      to: 'https://api.slack.com/developer-program',
      target: '_blank',
      rel: "noopener noreferrer"
    },
    {
      label: 'Your apps',
      to: 'https://api.slack.com/apps',
      position: 'right',
      target: '_blank',
      rel: "noopener noreferrer"
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
