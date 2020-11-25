# import built-in & third-party modules
import os
import zipfile
import shutil

from os.path import sep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as Chrome_Options
from selenium.webdriver import Remote

# import InstaPy modules
from .util import interruption_handler
from .util import highlight_print
from .util import emergency_exit
from .util import get_current_url
from .util import check_authorization
from .util import web_address_navigator
from .file_manager import use_assets
from .settings import Settings
from .time_util import sleep

# import exceptions
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import UnexpectedAlertPresentException


def get_chromedriver():
    chromedriver_path = shutil.which("chromedriver") or shutil.which("chromedriver.exe")
    if not chromedriver_path:
        raise Exception("Chromedriver not found. Please download it and add it to PATH.")
    else:
        return chromedriver_path

    

def set_selenium_local_session(
    proxy_address,
    proxy_port,
    proxy_username,
    proxy_password,
    headless_browser,
    browser_profile_path,
    disable_image_load,
    page_delay,
    chromedriver_path,
    browser_executable_path,
    logfolder,
    logger,
    chromedriver_log_level,
):
    browser = None
    err_msg = ""
    user_agent = ( # TODO: set user agent to chrome
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) FxiOS/18.1 Mobile/16B92 Safari/605.1.15"
    )

    Settings.user_agent = user_agent
    chrome_options = Chrome_Options()

    if headless_browser:
        chrome_options.add_argument("--headless")
    
    # if browser_profile_path is not None:
    #     chrome_profile = webdriver.ChromeProfile(browser_profile_path)
    # else:
    #     chrome_profile = webdriver.ChromeProfile()
    
    if browser_executable_path is not None:
        chrome_options.binary = browser_executable_path
    
    # set "info" by default
    # set "trace" for debugging, development only
    chrome_options.add_argument("--log-level={}".format(chromedriver_log_level))


    # set language to English
    chrome_options.add_argument("--lang={}".format('en'))
    if user_agent:
        chrome_options.add_argument("--user-agent={}".format(user_agent))

    if disable_image_load:
    # There also exists an extension for this, for further information:
    # https://stackoverflow.com/questions/28070315/python-disable-images-in-selenium-google-chromedriver
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)

    if proxy_address and proxy_port:
        chrome_options.add_argument('{0}:{1}'.format(proxy_address, proxy_port))
    
    chrome_options.add_argument("--mute-audio")

    #TODO: extension to hide selenium, check out browser_firefox to see how it's done
    # 

    chromedriver_log = "{}chromedriver.log".format(logfolder)
    chrome_options.add_argument("--log_path={}".format(chromedriver_log))
    driver_path = chromedriver_path or get_chromedriver()
    browser = webdriver.Chrome(
        # chrome_profile=chrome_profile,
        executable_path=driver_path,
        # log_path=chromedriver_log,
        options=chrome_options
    )
   

    if proxy_username and proxy_password:
        # proxy_authentication(browser, logger, proxy_username, proxy_password)
        pass #TODO: implement proxy_authentication
        
    browser.implicitly_wait(page_delay)
    try:
        browser.set_window_size(375, 812)
    except UnexpectedAlertPresentException as exc:
        logger.exception(
            "Unexpected alert on resizing web browser!\n\t"
            "{}".format(str(exc).encode("utf-8"))
        )
        close_browser(browser, False, logger)
        return browser, "Unexpected alert on browser resize"

    message = "Session started!"
    highlight_print("browser", message, "initialization", "info", logger)
    browser.typeofbr = "Chrome"
    return browser, err_msg





# def proxy_authentication(browser, logger, proxy_username, proxy_password): TODO: implement this
    

    
def close_browser(browser, threaded_session, logger):
   with interruption_handler(threaded=threaded_session):
       #delete cookies
        try:
           browser.delete_all_cookies()
        except Exception as exc:
            if isinstance(exc, WebDriverException):
                logger.exception(
                    "Error ocurred while deleting cookies"
                    "from web browser!\n\t{}".format(str(exc).encode('utf-8'))       
                )
