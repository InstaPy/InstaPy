"""
Class to define the specific actions for the User class to work with Appium
"""
from instapy.drivers.appium_endpoints.appium_common_actions import AppiumCommonActions
from instapy.drivers.appium_webdriver import AppiumWebDriver

class AppiumUserActions():
    """"
    Implementation class for User
    """

    @classmethod
    def find_and_populate_user(cls, user):
        if AppiumCommonActions.go_user(user):
            user.populate(cls.get_post_count(),cls.get_following_count(),
                            cls.get_follower_count(),cls.get_full_name(),cls.get_bio())

        return user

    @classmethod
    def get_following_count(self):
        return int(AppiumWebDriver.driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_following_count").getText())

    @classmethod
    def get_follower_count(self):
        return int(AppiumWebDriver.driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_followers_count").getText())

    @classmethod
    def get_post_count(self):
        return int(AppiumWebDriver.driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_post_count").getText())

    @classmethod
    def get_full_name(self):
        return AppiumWebDriver.driver.find_element_by_id("com.instagram.android:id/profile_header_full_name").getText()

    @classmethod
    def get_bio(self):
        """

        :param driver:
        :return:
        """
        return AppiumWebDriver.driver.find_element_by_id("com.instagram.android:id/profile_header_bio_text").getText()
