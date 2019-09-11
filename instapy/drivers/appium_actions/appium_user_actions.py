"""
Class to define the specific actions for the User class to work with Appium
"""
from .appium_common_actions import AppiumCommonActions
from ..appium_webdriver import AppiumWebDriver
from .appium_post_actions import AppiumPostActions


class AppiumUserActions:
    """"
    Implementation class for User
    """

    @classmethod
    def find_and_populate_user(cls, username):
        if AppiumCommonActions.go_user(username):
            user = User(username,
                        cls.get_post_count(),
                        cls.get_following_count(),
                        cls.get_follower_count(),
                        cls.get_full_name(),
                        cls.get_bio()
                        )
        return user

    @classmethod
    def get_following_count(cls):
        return cls._cleanup_count(
            AppiumWebDriver.find_element_by_id(
                "com.instagram.android:id/row_profile_header_textview_following_count"
            ).text
        )


    @classmethod
    def get_follower_count(cls):
        return cls._cleanup_count(
            AppiumWebDriver.find_element_by_id(
                "com.instagram.android:id/row_profile_header_textview_followers_count"
            ).text
        )


    @classmethod
    def get_post_count(cls):
        return cls._cleanup_count(
            AppiumWebDriver.find_element_by_id(
                "com.instagram.android:id/row_profile_header_textview_post_count"
            ).text
        )


    @classmethod
    def get_full_name(cls):
        return AppiumWebDriver.find_element_by_id(
            "com.instagram.android:id/profile_header_full_name"
        ).text

    @classmethod
    def get_bio(cls):
        """

        :param driver:
        :return:
        """
        return AppiumWebDriver.find_element_by_id(
            "com.instagram.android:id/profile_header_bio_text"
        ).text

    @classmethod
    def get_posts_likers(cls, username, post_grab_amount, likers_per_post_amount, randomize):
        """"

        :param username: the username to find and load
        :param post_grab_amount amount of posts to grab
        :param likers_per_post_amount amount of likers per post to grab
        :param randomize: if true takes randomly, otherwise return the post_grab_amount latest post
        :return: posts
        """

        users=[]
        todo = post_grab_amount
        if AppiumCommonActions.go_user(username):
            AppiumCommonActions.swipe(1200)

            if randomize is False:
                # then we should just take the first posts
                while todo > 0:
                    elems=AppiumWebDriver.find_elements_by_xpath("")

                    if len(elems) > post_grab_amount:
                        elems = elems[:post_grab_amount]

                    for elem in elems:
                        # go into the post
                        elem.click()
                        users.add(AppiumPostActions.get_likers(likers_per_post_amount))

                    todo -= len(elems)
                    AppiumCommonActions.swipe(200)


            else:
                # TODO: find a nice way to randomly select posts
                Logger.error("not implemented yet")

            return users

        else:
            Logger.error("User {} does not exist".format(username))

        return users

