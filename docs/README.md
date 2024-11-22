# tools.slack.dev/python-slack-sdk

This website is built using [Docusaurus](https://docusaurus.io/). 'Tis cool.

Each Bolt/SDK has its own Docusaurus website, with matching CSS and nav/footer. There is also be a Docusaurus website of just the homepage and community tools. 

```
docs/
├── content/ (the good stuff. md/mdx files supported)
│   ├── rtm.md
│   └── oauth.md
├── static/
│   ├── api_docs/ (generated reference docs)
│   │   └── slack_sdk/
│   │   │   └── index.html
│   ├── css/
│   │   └── custom.css (the css for everything!)
│   └── img/ (the pictures for the site)
│       ├── rory.png 
│       └── oslo.svg 
├── src/
│   └── theme (only contains the 404 page)
├── docusaurus.config.js (main config file)
├── footerConfig.js (footer. go to main repo to change)
├── navbarConfig.js (navbar. go to main repo to change)
└── sidebar.js (manually set where the content docs are in the sidebar.)
```

A cheat-sheet:
* _I want to edit a doc._ `docs/*/*.md`
* _I want to change the docs sidebar._ `sidebar.js`
* _I want to change the css._ Don't use this repo, use the home repo and the changes will propagate here.
* _I want to change anything else._ `docusaurus.config.js`

----

## Adding a doc

1. Make a markdown file. Add a `# Title` or use [front matter](https://docusaurus.io/docs/next/create-doc) with `title:`. 
2. Save it in `docs/folder/title.md` or `docs/title.md`, depending on if it's in a sidebar category. The nuance is just for internal organization.
3. Add the doc's path to the sidebar within `docusaurus.config.js`. Where ever makes most sense for you.
4. Test the changes ↓

---

## Running locally

Docusaurus requires at least Node 18. You can update Node however you want. `nvm` is one way. 

Install `nvm` if you don't have it:

```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

Then grab the latest version of Node.

```
nvm install node
```


If you are running this project locally for the first time, you'll need to install the packages with the following command:

```
npm install
```

The following command starts a local development server and opens up a browser window. 

```
npm run start
```

Edits to pages are reflected live — no restarting the server or reloading the page. (I'd say... 95% of the time, and 100% time if you're just editing a markdown file). FYI: The generated reference docs only load on build!

Remember — you're only viewing the Python Slack SDK docs right now.
---

## Deploying

The following command generates static content into the `build` directory. 

```
$ npm run build
```

Then you can test out with the following command: 

```
npm run serve
```

If it looks good, make a PR request!

### Deployment to GitHub pages

There is a GitHub action workflow set up in each repo. 

* On PR, it tests a site build.
* On Merge, it builds the site and deploys it. Site should update in a minute or two.

---

## Something's broken

Luke goofed. Open an issue please! `:bufo-appreciates-the-insight:`