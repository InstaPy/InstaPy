""" Module that handles the like features """
from .util import update_activity

from selenium.common.exceptions import NoSuchElementException

LIKE_TAG_CLASS = "coreSpriteHeartOpen"


def get_like_on_feed(browser, amount):
    """
    browser - the selenium browser element
    amount - total amount of likes to perform

    --------------------------------------
    The function takes in the total amount of likes to perform
    and then sends buttons to be liked, if it has run out of like
    buttons it will perform a scroll
    """
    assert 1 <= amount

    likes_performed = 0
    while likes_performed != amount:
        try:
            like_buttons = browser.find_elements_by_class_name(LIKE_TAG_CLASS)
        except NoSuchElementException:
            print("Unable to find the like buttons, aborting")
            break
        else:
            for button in like_buttons:
                likes_performed += 1
                if amount < likes_performed:
                    print("Performed the required number of likes")
                    break
                yield button

            print("---> Total Likes uptil now ->", likes_performed)

            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            update_activity(browser, state=None)
