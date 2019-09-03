"""
Class to define the specific actions for the User class to work with Appium
"""
from .common.model import user as usr
from ..appium_webdriver import driver

def go_to_search_page(driver):

    elem = driver.find_elements_by_xpath("//android.widget.FrameLayout[@content-desc='Search and Explore' and @index=1]")
    driver.click(elem)

def search_user(username,driver):

    elem = driver.find_element_by_id("com.instagram.android:id/action_bar_search_edit_text")
    elem.set_value(username)

    found_users = driver.find_elements_by_xpath("//android.widget.TextView[@resource-id='com.instagram.android:id/row_search_user_username']")
    return go_to_profile_from_search(found_users)

def go_to_profile_from_search(found_users):

    for f_user in found_users:
        if f_user.getText() == user.username:
            f_user.click()
            return True
    print('Unable to find user: {} did you request the right name?'.format(user.username))
    return False

def populate_user(driver,user):
    user.populate_user(get_number_posts(driver),get_number_following(driver),
                        get_number_followers(driver),get_header(driver),get_description(driver))

def find_and_populate_user(driver,user):
    if search_user(user.username):
        populate(driver,user)

def get_number_following(driver):
    return int(driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_following_count").getText())

def get_number_followers(driver):
    return int(driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_followers_count").getText())

def get_number_posts(driver):
    return int(driver.find_element_by_id("com.instagram.android:id/row_profile_header_textview_post_count").getText())

def get_header(driver):
    return driver.find_element_by_id("com.instagram.android:id/profile_header_full_name").getText()

def get_description(driver):
    return driver.find_element_by_id("com.instagram.android:id/profile_header_bio_text").getText()

def go_to_home_profile(driver):
    profile = driver.find_elements_by_xpath("//android.widget.FrameLayout[@content-desc='Profile' and @index=4]")
    driver.click(profile[0])
    return
