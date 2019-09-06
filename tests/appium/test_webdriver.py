from instapy.drivers import AppiumWebDriver
from instapy.drivers.appium_endpoints.appium_user import AppiumUser
import argparse

# from instapy.drivers.appium_endpoints import user_actions
parser = argparse.ArgumentParser(description='Code for testing appium features.')
parser.add_argument('--username', help='instagram username for login', default='abc')
args = parser.parse_args()
insta_username = args.username

AppiumWebDriver.construct_webdriver(devicename="emulator-5554")
#user = AppiumUser(username=insta_username)
#print(user)
