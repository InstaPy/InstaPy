"""
Class to define everything needed to work with Appium
"""

from appium import webdriver
from adb.client import Client as AdbClient


class AppiumWebDriver():
    """
    Appium WebDriver class
    """

    def __init__(
        self,
        devicename: str = "",
        devicetimeout: int = 600,
        client_host: str = "127.0.0.1",
        client_port: int = 5037,
    ):

        super().__init__()
        self.adb_client = AdbClient(host=client_host, port=client_port)
        self.adb_devices = self._get_adb_devices()
        self._driver = None

        __desired_caps = {}

        if any(devicename in device for device in self.adb_devices):
            self.devicename = devicename
            __desired_caps["platformName"] = "Android"
            __desired_caps["deviceName"] = devicename
            __desired_caps["appPackage"] = "com.instagram.android"
            __desired_caps["appActivity"] = "com.instagram.mainactivity.MainActivity"
            __desired_caps["automationName"] = "UiAutomator2"
            __desired_caps["noReset"] = True
            __desired_caps["fullReset"] = False
            __desired_caps["unicodeKeyboard"] = True
            __desired_caps["resetKeyboard"] = True
            __desired_caps["newCommandTimeout"] = devicetimeout

            try:
                self._driver = webdriver.Remote(
                    "http://{}:4723/wd/hub".format(client_host), __desired_caps
                )
            except:
                # self.logger.error("Could not create webdriver, is Appium running?")
                print("Could not create webdriver; please make sure Appium is running")

        else:
            # self.logger.error("Invalid Device Name")
            print(
                "Invalid Device Name. \nList of available devices: {}".format(
                    ", ".join(self.adb_devices)
                )
            )

    @property
    def driver(self):
        return self._driver

    def _get_adb_devices(self):
        """
        protected function to check the current running simulators
        :return:
        """
        devices = []

        for device in self.adb_client.devices():
            devices.append(device.serial)

        return devices

    def find_element_by_xpath(self, xpath: str = ""):
        """
        wrapper for find_element by_xpath
        :param xpath:
        :return:
        """
        return self.driver.find_element_by_xpath(xpath)

    def find_element_by_id(self, resource_id: str = ""):
        """
        wrapper for find_element_by_id
        :param resource_id:
        :return:
        """
        return self.driver.find_element_by_id(resource_id)

    def find_element_by_uiautomator(self, uiautomator: str = ""):
        """
        wrapper for find_element_by_android_uiautomator
        :param uiautomator:
        :return:
        """
        return self.driver.find_element_by_android_uiautomator(uiautomator)

    def click(self, webelem):
        """
        wrapper for element clicking
        :param webelem:
        :return:
        """
        webelem.click()
