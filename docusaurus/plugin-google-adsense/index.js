const path = require('path');

module.exports = function(context) {
    const {siteConfig} = context;
    const {themeConfig} = siteConfig;
    const {googleAdsense} = themeConfig || {};

    if(!googleAdsense) {
        throw new Error (
            'You need to specify `googleAdsense` object in `themeConfig` with `dataAdClient` field in it to use docusaurus-plugin-google-adsense',
          );
    }

    const {dataAdClient} = googleAdsense;

    if (!dataAdClient) {
        throw new Error (
          'You specified the `googleAdsense` object in `themeConfig` but the `dataAdClient` field was missing. ' +
            'Please ensure this is not a mistake.',
        );
      }

    const isProd = process.env.NODE_ENV === 'production';

    return {
        name: 'plugin-google-adsense',

        injectHtmlTags() {
            if (!isProd) return {};

            return {
                headTags: [
                    {
                        tagName: 'script',
                        attributes: {
                            'data-ad-client': dataAdClient,
                            async: true,
                            src: 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js',
                        },
                    },
                ],
            };
        },
    };
}
