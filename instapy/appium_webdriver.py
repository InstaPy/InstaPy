"""
Class to define everything needed to work with Appium
"""

from appium import webdriver
import subprocess
import os
import sys

class AppiumWebDriver():
    """
    Appium WebDriver class
    """

    def __init__(self, devicename: str='',adb_path: str='',devicetimeout: int=600):

        super().__init__()
        self.adb_path = adb_path

        __desired_caps = {}
        self._driver = None

        devices = self._adb_list_devices(self.adb_path)

        if any(devicename in device for device in devices):
            self.devicename = devicename
            __desired_caps['platformName'] = 'Android'
            __desired_caps['deviceName'] = devicename
            __desired_caps['appPackage'] = 'com.instagram.android'
            __desired_caps['appActivity'] = 'com.instagram.mainactivity.MainActivity'
            __desired_caps['automationName'] = 'UiAutomator2'
            __desired_caps['noReset'] = True
            __desired_caps['fullReset'] = False
            __desired_caps['unicodeKeyboard'] = True
            __desired_caps['resetKeyboard'] = True
            __desired_caps['newCommandTimeout'] = devicetimeout

            try:
                self._driver = webdriver.Remote('http://localhost:4723/wd/hub', __desired_caps)
            except:
                #self.logger.error("Could not create webdriver, is Appium running?")
                print("Could not create webdriver; please make sure Appium is running")

        else:
            #self.logger.error("Invalid Device Name")
            print("Invalid Device Name. \nList of available devices: {}".format(', '.join(devices)))

    @property
    def driver(self):
        return self._driver

    def _get_adb_path(self):
        """
        protected function to get the installation path of adb
        :return:
        """
        # todo: programatically get path to adb
        return path

    def _adb_list_devices(self,adb_path: str=''):
        """
        protected function to check the current running simulators
        :return:
        """

        console_output = subprocess.check_output([adb_path, 'devices']).splitlines()
        devices = []

        for line in console_output[1:]:
            line = line.decode("utf-8")
            if line != '':
                device = line.split('\t')[0] # Not sure if \\ is only for windows; have to check
                devices.append(device)
        return devices


    def find_element_by_xpath(self,xpath: str=''):
        """
        wrapper for find_element by_xpath
        :param xpath:
        :return:
        """
        return self.driver.find_element_by_xpath(xpath)

    def find_element_by_id(self, resource_id: str=''):
        """
        wrapper for find_element_by_id
        :param resource_id:
        :return:
        """
        return self.driver.find_element_by_id(uiautomator)

    def find_element_by_uiautomator(self, uiautomator: str=''):
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
