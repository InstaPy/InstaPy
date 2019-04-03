# selenium
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# general libs
import re

# local project
from .util import interruption_handler
from .util import highlight_print
from .settings import Settings
from .file_manager import get_chromedriver_location


def set_selenium_local_session(proxy,
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
        firefox_options = FirefoxOptions()
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

        # proxify the Firefox instance if has proxy enabled
        proxy.proxify(browser_name="Firefox",
                      firefox_profile=firefox_profile,
                      headless_browser=headless_browser)

        browser = webdriver.Firefox(firefox_profile=firefox_profile,
                                    options=firefox_options)

        # authenticate the proxy after starting the webdriver
        if proxy.username and proxy.password:
            proxy.authenticate(browser, logger)

    else:
        chromedriver_location = get_chromedriver_location()
        chrome_options = ChromeOptions()
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

        chrome_capabilities = DesiredCapabilities.CHROME

        # proxify the Chrome instance if has proxy enabled
        proxy.proxify(browser_name="Chrome",
                      chrome_options=chrome_options,
                      chrome_capabilities=chrome_capabilities,
                      headless_browser=headless_browser)

        # using saved profile for Chrome
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
            browser = webdriver.Chrome(
                chromedriver_location,
                desired_capabilities=chrome_capabilities,
                chrome_options=chrome_options
            )

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
            err_msg = ('chromedriver {} is not supported, expects {}+'
                       .format(float(matches.groups()[0]),
                               Settings.chromedriver_min_version))
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
