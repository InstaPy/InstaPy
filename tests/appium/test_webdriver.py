from instapy.drivers import AppiumWebDriver
from instapy.common.model import user as usr

# from instapy.drivers.appium_endpoints import user_actions

driver = AppiumWebDriver(devicename="emulator-5554")
user = usr()
find_and_populate_user(driver, user)
print(user)
