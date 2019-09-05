"""
Class to define the specific actions for the User class to work with Appium
"""
from instapy.common.model import User
from .appium_common import AppiumCommon

class AppiumUser(User,AppiumCommon):
    """"
    Implementation class for User
    """
    def find_and_populate_user(self, driver,user):
        if Common.go_user(user.username):
            self.populate(get_post_count(driver),get_following_count(driver),
                            get_follower_count(driver),get_full_name(driver),get_bio(driver))


    def get_following_count(self):
        return int(self._driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_following_count").getText())

    def get_follower_count(self):
        return int(self._driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_followers_count").getText())

    def get_post_count(self):
        return int(self._driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_post_count").getText())


    def get_full_name(self):
        return self._driver.find_element_by_id("com.instagram.android:id/profile_header_full_name").getText()


    def get_bio(self):
        """

        :param driver:
        :return:
        """
        return self._driver.find_element_by_id("com.instagram.android:id/profile_header_bio_text").getText()
