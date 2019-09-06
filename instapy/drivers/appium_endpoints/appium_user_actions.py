"""
Class to define the specific actions for the User class to work with Appium
"""
from .appium_common_actions import AppiumCommonActions

class AppiumUserActions():
    """"
    Implementation class for User
    """

    def find_and_populate_user(self, driver,user):
        if AppiumCommonActions.go_user(user.username):
            user.populate(self.get_post_count(driver),self.get_following_count(driver),
                            self.get_follower_count(driver),self.get_full_name(driver),self.get_bio(driver))


    def get_following_count(self,drive):
        return int(driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_following_count").getText())

    def get_follower_count(self,driver):
        return int(driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_followers_count").getText())

    def get_post_count(self,driver):
        return int(driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_post_count").getText())


    def get_full_name(self,driver):
        return driver.find_element_by_id("com.instagram.android:id/profile_header_full_name").getText()


    def get_bio(self,driver):
        """

        :param driver:
        :return:
        """
        return driver.find_element_by_id("com.instagram.android:id/profile_header_bio_text").getText()
