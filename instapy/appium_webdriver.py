"""
Class to define everything needed to work with Appium
"""

from appium import webdriver
import subprocess

class AppiumWebDriver():
    """
    Appium WebDriver class
    """

    def __init__(self, devicename: str='',devicetimeout: int=600):

        super().__init__()

        __desired_caps = {}
        _driver = None


        if devicename != '':
            __desired_caps['platformName'] = 'Android'
            #todo: use python adb to do a adb devices and double check that we have a match
            __desired_caps['deviceName'] = devicename
            __desired_caps['appPackage'] = 'com.instagram.android'
            __desired_caps['appActivity'] = 'com.instagram.mainactivity.MainActivity'
            __desired_caps['noReset'] = True
            __desired_caps['fullReset'] = False
            __desired_caps['unicodeKeyboard'] = True
            __desired_caps['resetKeyboard'] = True
            __desired_caps['newCommandTimeout'] = devicetimeout

            try:
                _driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
            except:
                self.logger.error("Could not create webdriver, is Appium running?")

        else:
            self.logger.error("Invalid Device Name")

    @property
    def driver(self):
        return _driver

    def _adb_list_devices(self,adb_path: str=''):
        """
        protected function to check the current running simulators
        :return:
        """

        console_output = subprocess.check_output([adb_path, 'devices']).splitlines()
        devices = []

        print('List of available devices:')
        for line in console_output[1:]:
            line = line.decode("utf-8")
            if line != '':
                device = line.split('\t')[0] # Not sure if \\ is only for windows; have to check
                devices.append(device)
                print(device)
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
