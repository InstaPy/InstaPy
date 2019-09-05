from instapy.drivers import AppiumWebDriver
from instapy.drivers.appium_endpoints.appium_user import AppiumUser

# from instapy.drivers.appium_endpoints import user_actions

driver = AppiumWebDriver(devicename="emulator-5554")
user = AppiumUser()
find_and_populate_user(driver, user)
print(user)
