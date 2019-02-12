# selenium
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as Firefox_Options


# general libs
import re
from time import sleep

# local project
from .util import interruption_handler
from .util import highlight_print
from .settings import Settings
from .file_manager import get_chromedriver_location


def set_selenium_local_session(proxy_address,
                               proxy_port,
                               proxy_username,
                               proxy_password,
                               proxy_chrome_extension,
                               headless_browser,
                               use_firefox,
                               browser_profile_path,
                               disable_image_load,
                               page_delay,
                               logger):
    """Starts local session for a selenium server.
    Default case scenario."""

    browser = None
    err_msg = ''

    if use_firefox:
        firefox_options = Firefox_Options()
        if headless_browser:
            firefox_options.add_argument('-headless')

        if browser_profile_path is not None:
            firefox_profile = webdriver.FirefoxProfile(
                browser_profile_path)
        else:
            firefox_profile = webdriver.FirefoxProfile()

        if disable_image_load:
            # permissions.default.image = 2: Disable images load,
            # this setting can improve pageload & save bandwidth
            firefox_profile.set_preference('permissions.default.image', 2)

        if proxy_address and proxy_port:
            firefox_profile.set_preference('network.proxy.type', 1)
            firefox_profile.set_preference('network.proxy.http',
                                           proxy_address)
            firefox_profile.set_preference('network.proxy.http_port',
                                           proxy_port)
            firefox_profile.set_preference('network.proxy.ssl',
                                           proxy_address)
            firefox_profile.set_preference('network.proxy.ssl_port',
                                           proxy_port)

        browser = webdriver.Firefox(firefox_profile=firefox_profile,
                                    options=firefox_options)

        # authenticate with popup alert window
        if (proxy_username and proxy_password):
            proxy_authentication(browser,
                                 logger,
                                 proxy_username,
                                 proxy_password)

    else:
        chromedriver_location = get_chromedriver_location()
        chrome_options = Options()
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--lang=en-US')
        chrome_options.add_argument('--disable-setuid-sandbox')

        # this option implements Chrome Headless, a new (late 2017)
        # GUI-less browser. chromedriver 2.9 and above required
        if headless_browser:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')

            if disable_image_load:
                chrome_options.add_argument(
                    '--blink-settings=imagesEnabled=false')

            # replaces browser User Agent from "HeadlessChrome".
            user_agent = "Chrome"
            chrome_options.add_argument('user-agent={user_agent}'
                                        .format(user_agent=user_agent))

        capabilities = DesiredCapabilities.CHROME

        # Proxy for chrome
        if proxy_address and proxy_port:
            prox = Proxy()
            proxy = ":".join([proxy_address, str(proxy_port)])
            if headless_browser:
                chrome_options.add_argument(
                    "--proxy-server=http://{}".format(proxy))
            else:
                prox.proxy_type = ProxyType.MANUAL
                prox.http_proxy = proxy
                prox.socks_proxy = proxy
                prox.ssl_proxy = proxy
                prox.add_to_capabilities(capabilities)

        # add proxy extension
        if proxy_chrome_extension and not headless_browser:
            chrome_options.add_extension(proxy_chrome_extension)

        # using saved profile for chrome
        if browser_profile_path is not None:
            chrome_options.add_argument(
                'user-data-dir={}'.format(browser_profile_path))

        chrome_prefs = {
            'intl.accept_languages': 'en-US',
        }

        if disable_image_load:
            chrome_prefs['profile.managed_default_content_settings.images'] = 2

        chrome_options.add_experimental_option('prefs', chrome_prefs)
        try:
            browser = webdriver.Chrome(chromedriver_location,
                                       desired_capabilities=capabilities,
                                       chrome_options=chrome_options)

        except WebDriverException as exc:
            logger.exception(exc)
            err_msg = 'ensure chromedriver is installed at {}'.format(
                Settings.chromedriver_location)
            return browser, err_msg

        # prevent: Message: unknown error: call function result missing 'value'
        matches = re.match(r'^(\d+\.\d+)',
                           browser.capabilities['chrome'][
                               'chromedriverVersion'])
        if float(matches.groups()[0]) < Settings.chromedriver_min_version:
            err_msg = 'chromedriver {} is not supported, expects {}+'.format(
                float(matches.groups()[0]), Settings.chromedriver_min_version)
            return browser, err_msg

    browser.implicitly_wait(page_delay)

    message = "Session started!"
    highlight_print('browser', message, "initialization", "info", logger)
    print('')

    return browser, err_msg


def set_selenium_remote_session(use_firefox,
                                logger,
                                selenium_url='',
                                selenium_driver=None):
    """
    Starts remote session for a selenium server.
    Creates a new selenium driver instance for remote session or uses provided
    one. Useful for docker setup.

    :param selenium_url: string
    :param selenium_driver: selenium WebDriver
    :return: self
    """
    if selenium_driver:
        browser = selenium_driver
    else:
        if use_firefox:
            browser = webdriver.Remote(
                command_executor=selenium_url,
                desired_capabilities=DesiredCapabilities.FIREFOX)
        else:
            browser = webdriver.Remote(
                command_executor=selenium_url,
                desired_capabilities=DesiredCapabilities.CHROME)

    message = "Session started!"
    highlight_print('browser', message, "initialization", "info", logger)
    print('')

    return browser


def proxy_authentication(browser,
                         logger,
                         proxy_username,
                         proxy_password):
    """ Authenticate proxy using popup alert window """
    try:
        # sleep(1) is enough, sleep(2) is to make sure we
        # give time to the popup windows
        sleep(2)
        alert_popup = browser.switch_to_alert()
        alert_popup.send_keys('{username}{tab}{password}{tab}'
                              .format(username=proxy_username,
                                      tab=Keys.TAB,
                                      password=proxy_password))
        alert_popup.accept()
    except Exception:
        logger.warn('Unable to proxy authenticate')


def close_browser(browser,
                  threaded_session,
                  logger):
    with interruption_handler(threaded=threaded_session):
        # delete cookies
        try:
            browser.delete_all_cookies()
        except Exception as exc:
            if isinstance(exc, WebDriverException):
                logger.exception(
                    "Error occurred while deleting cookies "
                    "from web browser!\n\t{}"
                    .format(str(exc).encode("utf-8")))

        # close web browser
        try:
            browser.quit()
        except Exception as exc:
            if isinstance(exc, WebDriverException):
                logger.exception(
                    "Error occurred while "
                    "closing web browser!\n\t{}"
                    .format(str(exc).encode("utf-8")))
