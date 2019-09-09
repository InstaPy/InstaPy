"""
The generic driver encapsulating the correct implemented driver we need
for the current session
"""

from .appium_webdriver import AppiumWebDriver
from .appium_actions import AppiumActions
from instapy.common import Settings


class WebDriver(object):
    driver = None
    actions = None

    APPIUM_DRIVER = "appium-driver"
    SELENIUM_DRIVER = "selenium-driver"

    def __init__(self, type: str = "", **kwargs):
        """

        :param type: the choice of driver to use
        """
        if type == self.APPIUM_DRIVER:

            self.driver = AppiumWebDriver(
                kwargs.get("devicename") or Settings.devicename,
                kwargs.get("devicetimeout") or Settings.devicetimeout,
                kwargs.get("client_host") or Settings.client_host,
                kwargs.get("client_port") or Settings.client_port,
            )
            self.actions = AppiumActions()

        if type == self.SELENIUM_DRIVER:
            self.driver = SeleniumWebDriver(
                kwargs.get("proxy_address") or Settings.proxy_address,
                kwargs.get("proxy_port") or Settings.proxy_port,
                kwargs.get("proxy_username") or Settings.proxy_username,
                kwargs.get("proxy_password") or Settings.proxy_password,
                kwargs.get("headless_browser") or Settings.headless_browser,
                kwargs.get("browser_profile_path") or Settings.browser_profile_path,
                kwargs.get("disable_image_load") or Settings.disable_image_load,
                kwargs.get("page_delay") or Settings.page_delay,
                kwargs.get("geckodriver_path") or Settings.geckodriver_path,
            )
            self.actions = SeleniumActions()
