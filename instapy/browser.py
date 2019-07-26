# selenium
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as Firefox_Options
from selenium.webdriver import Remote
from fake_useragent import UserAgent
from webdriverdownloader import GeckoDriverDownloader

# general libs
import re
import os
import zipfile
from time import sleep

# local project
from .util import interruption_handler
from .util import highlight_print
from .util import emergency_exit
from .util import get_current_url
from .util import check_authorization
from .util import web_address_navigator
from .settings import Settings
from .file_manager import use_assets


def create_firefox_extension():
    ext_path = os.path.abspath(os.path.dirname(__file__) + '/firefox_extension')
    # safe into assets folder
    zip_file = use_assets() + '/extension.xpi'

    files = [ 'manifest.json', 'content.js', 'arrive.js' ]
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED, False) as zipf:
        for file in files:
            zipf.write(ext_path + '/' + file, file)

    return zip_file



def get_geckodriver():
    asset_path = use_assets()
    gdd = GeckoDriverDownloader(asset_path, asset_path)
    # skips download if already downloaded
    bin_path, sym_path = gdd.download_and_install()
    return sym_path



def set_selenium_local_session(proxy_address,
                               proxy_port,
                               proxy_username,
                               proxy_password,
                               headless_browser,
                               browser_profile_path,
                               disable_image_load,
                               page_delay,
                               geckodriver_path,
                               logger):
    """Starts local session for a selenium server.
    Default case scenario."""

    browser = None
    err_msg = ''

    # define fallback useragent
    user_agent = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    )

    # try to fetch latest user agent
    try:
        ua = UserAgent(cache = False, fallback = user_agent)
        user_agent = ua.firefox
    except Exception:
        print('Latest user agent currently not reachable. Using fallback.')

    firefox_options = Firefox_Options()

    if headless_browser:
        firefox_options.add_argument('-headless')

    if browser_profile_path is not None:
        firefox_profile = webdriver.FirefoxProfile(
            browser_profile_path)
    else:
        firefox_profile = webdriver.FirefoxProfile()

    # set English language
    firefox_profile.set_preference('intl.accept_languages', 'en')
    firefox_profile.set_preference('general.useragent.override', user_agent)

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

    # mute audio while watching stories
    firefox_profile.set_preference('media.volume_scale', '0.0')

    # prefer user path before downloaded one
    driver_path = geckodriver_path or get_geckodriver()
    browser = webdriver.Firefox(firefox_profile = firefox_profile,
                                executable_path = driver_path,
                                options = firefox_options)

    # add extenions to hide selenium
    browser.install_addon(create_firefox_extension(), temporary = True)

    # converts to custom browser
    # browser = convert_selenium_browser(browser)

    # authenticate with popup alert window
    if (proxy_username and proxy_password):
        proxy_authentication(browser,
                             logger,
                             proxy_username,
                             proxy_password)


    browser.implicitly_wait(page_delay)

    message = 'Session started!'
    highlight_print('browser', message, 'initialization', 'info', logger)

    return browser, err_msg



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


def close_browser(browser, threaded_session, logger):
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




def retry(max_retry_count = 3, start_page = None):
    """Decorator which refreshes the page and tries to execute the function again.
    Use it like that: @retry() => the '()' are important because its a decorator with params."""

    def real_decorator(org_func):
        def wrapper(*args, **kwargs):
            browser = None
            _start_page = start_page

            # try to find instance of a browser in the arguments
            # all webdriver classes (chrome, firefox, ...) inherit from Remote class
            for arg in args:
                if not isinstance(arg, Remote): continue

                browser = arg
                break

            else:
                for _, value in kwargs.items():
                    if not isinstance(value, Remote): continue

                    browser = value
                    break

            if not browser:
                print('not able to find browser in parameters!')
                return org_func(*args, **kwargs)

            if max_retry_count == 0:
                print('max retry count is set to 0, this function is useless right now')
                return org_func(*args, **kwargs)

            # get current page if none is given
            if not start_page:
                _start_page = browser.current_url

            rv = None
            retry_count = 0
            while True:
                try:
                    rv = org_func(*args, **kwargs)
                    break
                except Exception as e:
                    # TODO: maybe handle only certain exceptions here
                    retry_count += 1

                    # if above max retries => throw original exception
                    if retry_count > max_retry_count:
                        raise e

                    rv = None

                    # refresh page
                    browser.get(_start_page)

            return rv
        return wrapper
    return real_decorator



class custom_browser(Remote):
    '''Custom browser instance for manupulation later on'''


    def find_element_by_xpath(self, *args, **kwargs):
        '''example usage of hooking into built in functions'''
        rv = super(custom_browser, self).find_element_by_xpath(*args, **kwargs)
        return rv


    def wait_for_valid_connection(self, username, logger):
        counter = 0
        while True and counter < 10:
            sirens_wailing, emergency_state = emergency_exit(self, username, logger)
            if sirens_wailing and emergency_state == 'not connected':
                logger.warning('there is no valid connection')
                counter += 1
                sleep(60)
            else:
                break


    def wait_for_valid_authorization(self, username, logger):
        # save current page
        current_url = get_current_url(self)

        # stuck on invalid auth
        auth_method = 'activity counts'
        counter = 0
        while True and counter < 10:
            login_state = check_authorization(self, username, auth_method, logger)
            if login_state is False:
                logger.warning('not logged in')
                counter += 1
                sleep(60)
            else:
                break

        # return to original page
        web_address_navigator(self, current_url)



def convert_selenium_browser(driver):
    """Changed the class to our custom class"""
    driver.__class__ = custom_browser
    return driver
