""" Module to be used for InstaPy's proxy configuration """

from time import sleep
import os
from os.path import exists as path_exists
import json
from zipfile import ZipFile
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy as SeleniumProxy
from selenium.webdriver.common.proxy import ProxyType as SeleniumProxyType

from .file_manager import get_workspace
from .util import parse_cli_args


class Proxy:
    """ Store proxy data and also do proxy operations """

    def __init__(self,
                 address=None,
                 port=None,
                 username=None,
                 password=None):

        # assign values of flags which has higher priority than formal args
        cli_args = parse_cli_args()
        self.address = cli_args.proxy_address or address
        self.port = cli_args.proxy_port or port
        self.username = cli_args.proxy_username or username
        self.password = cli_args.proxy_password or password

    def make_extension(self):
        """ Make a proxy extension for Chrome """

        manifest = {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version": "22.0.0"
        }

        background_js = """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                      singleProxy: {
                        scheme: "http",
                        host: "%s",
                        port: parseInt(%s)
                      },
                      bypassList: ["localhost"]
                    }
                  };
            chrome.proxy.settings.set({value: config, scope: "regular"},
            function() {});
            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "%s",
                        password: "%s"
                    }
                };
            }
            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
        """ % (self.address, self.port, self.username, self.password)

        workspace = get_workspace()
        extension_dir = "{}/assets/chrome_extensions".format(workspace["path"])
        if not path_exists(extension_dir):
            os.makedirs(extension_dir)

        plugin_file = "{}/proxy_auth_{}:{}.zip".format(
            extension_dir, self.address, self.port)

        with ZipFile(plugin_file, 'w') as zf:
            zf.writestr("manifest.json", json.dumps(manifest))
            zf.writestr("background.js", background_js)

        return plugin_file

    def proxify(self,
                browser_name=None,
                chrome_options=None,
                chrome_capabilities=None,
                firefox_profile=None,
                headless_browser=None):
        """ Add proxy configuration to browser objects """

        if not self.address and not self.port:
            # proxy is not enabled
            return False

        if browser_name == "Chrome":
            # proxy for Chrome
            if self.username and self.password and not headless_browser:
                # set proxy using an extension if it has to be authenticated
                chrome_proxy_extension = self.make_extension()
                chrome_options.add_extension(chrome_proxy_extension)

            else:
                chrome_proxy = "{}:{}".format(self.address, self.port)
                if headless_browser:
                    # set proxy by a Chrome flag if it is headless
                    chrome_options.add_argument(
                        "--proxy-server=http://{}".format(chrome_proxy))
                else:
                    # set proxy by Selenium
                    selenium_proxy = SeleniumProxy()
                    selenium_proxy.proxy_type = SeleniumProxyType.MANUAL
                    selenium_proxy.http_proxy = chrome_proxy
                    selenium_proxy.socks_proxy = chrome_proxy
                    selenium_proxy.ssl_proxy = chrome_proxy
                    selenium_proxy.add_to_capabilities(chrome_capabilities)

        elif browser_name == "Firefox":
            firefox_profile.set_preference('network.proxy.type', 1)
            firefox_profile.set_preference('network.proxy.http',
                                           self.address)
            firefox_profile.set_preference('network.proxy.http_port',
                                           self.port)
            firefox_profile.set_preference('network.proxy.ssl',
                                           self.address)
            firefox_profile.set_preference('network.proxy.ssl_port',
                                           self.port)

        return True

    def authenticate(self, browser, logger):
        """ Authenticate proxy using popup alert window in Firefox """

        try:
            # sleep(1) is enough, sleep(2) is to make sure we
            # give time to the popup windows
            sleep(2)
            alert_popup = browser.switch_to_alert()
            alert_popup.send_keys('{username}{tab}{password}{tab}'
                                  .format(username=self.username,
                                          tab=Keys.TAB,
                                          password=self.password))
            alert_popup.accept()

        except Exception:
            logger.warn('Unable to proxy authenticate')

