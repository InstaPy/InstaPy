const path = require('path');

module.exports = {
  title: 'InstaPy',
  tagline: 'Tool to automate your Social Media interactions.',
  url: 'https://instapy.org',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  favicon: 'img/favicon.ico',
  organizationName: 'timgrossmann', // Usually your GitHub org/user name.
  projectName: 'InstaPy', // Usually your repo name.
  themeConfig: {
    googleAdsense: { dataAdClient: 'ca-pub-4875789012193531' },
    gtag: {
      trackingID: 'G-F16VNTTQ7S',
      anonymizeIP: false,
    },
    sidebarCollapsible: false,
    navbar: {
      title: 'InstaPy - Documentation',
      logo: {
        alt: 'InstaPy Logo',
        src: 'img/instapy_logo.png',
      },
      items: [
        //{
          //to: 'docs/',
          //activeBasePath: 'docs',
          //label: 'Docs',
          //position: 'left',
        //},
        //{to: 'blog', label: 'Blog', position: 'left'},
        {
          href: 'https://github.com/timgrossmann/InstaPy',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Community',
          items: [
            {
              label: 'Discord',
              href: 'https://discordapp.com/invite/docusaurus',
            },
            {
              label: 'Twitter',
              href: 'https://twitter.com/docusaurus',
            },
          ],
        },
        {
          title: 'Links',
          items: [
            // TODO add affiliate links here
            //{
              //label: 'Style Guide',
              //to: 'docs/',
            //},
            //{
              //label: 'Second Doc',
              //to: 'docs/doc2/',
            //},
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/timgrossmann/InstaPy',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} InstaPy.`,
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          routeBasePath: '/',
          path: '../docs',
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl:
            'https://github.com/timgrossmann/InstaPy/edit/master/website/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
  plugins: [
    path.resolve(__dirname, 'plugin-google-adsense'),
  ],
};
