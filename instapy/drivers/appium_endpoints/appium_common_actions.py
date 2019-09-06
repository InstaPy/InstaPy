"""
Class to define the specific actions for the Common class to work with Appium
"""

from instapy.common.model import CommonActions

class AppiumCommonActions(CommonActions):
    """
    class for all the common actions (not related to user, comment, post, story)
    """

    @classmethod
    def go_profile(cls,driver):
        """

        :param driver:
        :return:
        """
        profile = driver.find_elements_by_xpath("//android.widget.FrameLayout[@content-desc='Profile' and @index=4]")
        driver.click(profile[0])

    @classmethod
    def go_user(cls,driver,user):

        try:
            cls._go_search()
        except:
            print("error")
            return False

        elem = driver.find_element_by_id("com.instagram.android:id/action_bar_search_edit_text")
        elem.set_value(user.username)

        found_users = driver.find_elements_by_xpath("//android.widget.TextView[@resource-id='com.instagram.android:id/row_search_user_username']")

        for f_user in found_users:
            if f_user.getText() == user.username:
                f_user.click()
                return True
        print('Unable to find user: {} did you request the right name?'.format(user.username))
        return False

        # searching on the app is the way to move from one user to another
        # if the list is not null then we should click on it to go to that user


    @classmethod
    def _go_search(cls,driver):
        print('here')
        elem = driver.find_elements_by_xpath("//android.widget.FrameLayout[@content-desc='Search and Explore' and @index=1]")
        print(elem[0])
        driver.click(elem[0])
