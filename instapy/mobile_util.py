from time import sleep
from instapy.login_util import dismiss_notification_offer
from .xpath import read_xpath
import pyautogui


def create_ig_post(browser, logger, post_description, image_file_path):
    """ Post on Instagram in mobile mode """

    # close modal screen
    dismiss_notification_offer(browser, logger)
    try:
        logger.info('Creating new post...')
        # click new post button
        browser.find_element_by_xpath(
            read_xpath(create_ig_post.__name__, "new_post_button")).click()
        # fill form input with local file path
        input_file_element = browser.find_element_by_xpath(
            read_xpath(create_ig_post.__name__, "form_input_element"))
        input_file_element.send_keys(image_file_path)
        sleep(3)
        # ESC to close the Dialog window
        pyautogui.press('esc')
        # confirm step
        browser.find_element_by_xpath(
            read_xpath(create_ig_post.__name__, "confirm_post_creation")).click()
        # set post description
        browser.find_element_by_xpath(
            read_xpath(create_ig_post.__name__, "post_description_textarea")
            ).send_keys(post_description)
        sleep(1)
        browser.find_element_by_xpath(
            read_xpath(create_ig_post.__name__, "final_post_creation_step")).click()
        sleep(3)
        return True
    except Exception:
        return False
