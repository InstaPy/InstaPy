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

    # Probably not right place for this
    @classmethod
    def _cleanup_count(cls,count: str=None):
        if ',' in count:
            return count.replace(',','')
        else:
            minus_one = False
            if '.' in count:
                minus_one = True
                count = count.replace('.','')
            if 'K' in count:
                if minus_one:
                    count = count.replace('K','00')
                else:
                    count = count.replace('K','000')
                return count
            elif 'M' in count:
                if minus_one:
                    count = count.replace('M','00000')
                else:
                    count = count.replace('K','000000')
                return count
            return count

    @classmethod
    def get_following_count(cls):
        return int(cls._cleanup_count(AppiumWebDriver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_following_count").text))

    @classmethod
    def get_follower_count(cls):
        return int(cls._cleanup_count(AppiumWebDriver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_followers_count").text))

    @classmethod
    def get_post_count(cls):
        return int(cls._cleanup_count(AppiumWebDriver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_post_count").text))
    @classmethod
    def get_full_name(cls):
        return AppiumWebDriver.find_element_by_id("com.instagram.android:id/profile_header_full_name").text

    @classmethod
    def get_bio(cls):
        """

        :param driver:
        :return:
        """
        return AppiumWebDriver.find_element_by_id("com.instagram.android:id/profile_header_bio_text").text
