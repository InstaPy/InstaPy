"""
Class to define everything needed to work with Appium
"""

#class import
from instapy.common import Logger

# libraries import
from appium import webdriver
from adb.client import Client as AdbClient
from time import sleep


class AppiumWebDriver:
    """
    Appium WebDriver class
    """

    driver = None
    webdriver_instance = None  # might not be needed
    DISPLAYSIZE = None

    @classmethod
    def construct_webdriver(
        cls,
        devicename: str = "",
        devicetimeout: int = 600,
        client_host: str = "127.0.0.1",
        client_port: int = 5037,
    ):
        if cls.driver is None or cls.webdriver_instance is None:
            cls.webdriver_instance = AppiumWebDriver(
                devicename, devicetimeout, client_host, client_port
            )

    def __init__(
        self,
        devicename: str = "",
        devicetimeout: int = 600,
        client_host: str = "127.0.0.1",
        client_port: int = 5037,
    ):

        self.adb_client = AdbClient(host=client_host, port=client_port)
        self.adb_devices = self._get_adb_devices()

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
                self.driver = webdriver.Remote(
                    "http://{}:4723/wd/hub".format(client_host), __desired_caps
                )
                Logger.info("Succesfully connected to: {}".format(self.devicename))
                self.DISPLAYSIZE = driver.get_window_size()
                sleep(10)
            except:
                # self.logger.error("Could not create webdriver, is Appium running?")
                Logger.error("Could not create webdriver; please make sure Appium is running")
                quit()  # TODO: nicer way of exiting

        else:

            Logger.error(
                "Invalid Device Name. \nList of available devices: [{}]".format(
                    ", ".join(self.adb_devices)
                )
            )
            quit()  # TODO: nicer way of exiting

    def _get_adb_devices(self):
        """
        protected function to check the current running simulators
        :return:
        """
        devices = []

        for device in self.adb_client.devices():
            devices.append(device.serial)

        return devices

    @classmethod
    def get_driver(cls):
        """
        wrapper for find_element by_xpath
        :param xpath:
        :return:
        """
        return cls.driver

    @classmethod
    def find_elements_by_xpath(cls, xpath: str = ""):
        """
        wrapper for find_element by_xpath
        :param xpath:
        :return:
        """
        return cls.driver.find_elements_by_xpath(xpath)

    @classmethod
    def find_element_by_id(cls, resource_id: str = ""):
        """
        wrapper for find_element_by_id
        :param resource_id:
        :return:
        """
        return cls.driver.find_element_by_id(resource_id)

    @classmethod
    def find_element_by_uiautomator(cls, uiautomator: str = ""):
        """
        wrapper for find_element_by_android_uiautomator
        :param uiautomator:
        :return:
        """
        return cls.driver.find_element_by_android_uiautomator(uiautomator)

    @staticmethod
    def click(webelem):
        """
        wrapper for element clicking
        :param webelem:
        :return:
        """
        webelem.click()
