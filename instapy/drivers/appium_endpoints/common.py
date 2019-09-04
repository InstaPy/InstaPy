class Common():
    """
    class for all the common actions (not related to user, comment, post, story)
    """

    @staticmethod
    def go_profile(driver):
        """

        :param driver:
        :return:
        """
        profile = driver.find_elements_by_xpath("//android.widget.FrameLayout[@content-desc='Profile' and @index=4]")
        driver.click(profile[0])

    @staticmethod
    def go_user(username,driver):

        try:
            _go_search_page(driver)
        except:
            print("error")
            return False

        elem = driver.find_element_by_id("com.instagram.android:id/action_bar_search_edit_text")
        elem.set_value(username)

        found_users = driver.find_elements_by_xpath("//android.widget.TextView[@resource-id='com.instagram.android:id/row_search_user_username']")

        for f_user in found_users:
            if f_user.getText() == user.username:
                f_user.click()
                return True
        print('Unable to find user: {} did you request the right name?'.format(user.username))
        return False

        # searching on the app is the way to move from one user to another
        # if the list is not null then we should click on it to go to that user

    @staticmethod
    def _go_search_page(driver):

        elem = driver.find_elements_by_xpath("//android.widget.FrameLayout[@content-desc='Search and Explore' and @index=1]")
        driver.click(elem)

