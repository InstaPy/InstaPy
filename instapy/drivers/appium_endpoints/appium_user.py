"""
Class to define the specific actions for the User class to work with Appium
"""
from instapy.common.model import User
from .common import Common

class AppiumUser(User,Common):
    """"
    Implementation class for User
    """

    def go_to_profile_from_search(self, found_users):

        for f_user in found_users:
            if f_user.getText() == user.username:
                f_user.click()
                return True
        print('Unable to find user: {} did you request the right name?'.format(user.username))
        return False

    #not needed, we can call directly user.populate
    #def populate(self,driver,user):
    #    self.populate(get_post_count(driver),get_following_count(driver),
    #                        get_follower_count(driver),get_full_name(driver),get_bio(driver))

    def find_and_populate_user(self, driver,user):
        if Common.search_user(user.username):
            self.populate(get_post_count(driver),get_following_count(driver),
                            get_follower_count(driver),get_full_name(driver),get_bio(driver))

    @staticmethod
    def get_following_count(driver):
        return int(driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_following_count").getText())

    @staticmethod
    def get_follower_count(driver):
        return int(driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_followers_count").getText())

    @staticmethod
    def get_post_count(driver):
        return int(driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_post_count").getText())

    @staticmethod
    def get_full_name(driver):
        return driver.find_element_by_id("com.instagram.android:id/profile_header_full_name").getText()

    @staticmethod
    def get_bio(driver):
        """

        :param driver:
        :return:
        """
        return driver.find_element_by_id("com.instagram.android:id/profile_header_bio_text").getText()



