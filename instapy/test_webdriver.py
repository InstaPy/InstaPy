from appium_webdriver import AppiumWebDriver
from common.model import user as usr
from drivers.appium_endpoints import user_actions

driver = AppiumWebDriver(devicename='emulator-5554')
user = usr()
find_and_populate_user(driver,user)
print(user)
