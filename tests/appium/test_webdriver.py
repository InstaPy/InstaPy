from instapy.drivers import AppiumWebDriver
from instapy.drivers.appium_actions.appium_user_actions import AppiumUserActions
from instapy.common.model.user import User
import argparse

# from instapy.drivers.appium_endpoints import user_actions
parser = argparse.ArgumentParser(description='Code for testing appium features.')
parser.add_argument('--username', help='instagram username for login', default='abc')
args = parser.parse_args()
insta_username = args.username

AppiumWebDriver.construct_webdriver(devicename="emulator-5554")
user = User(username=insta_username)
user = AppiumUserActions.find_and_populate_user(user)
print(user)
