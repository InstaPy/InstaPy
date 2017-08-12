import re

"""Module that handles the like features"""
from math import ceil
from re import findall
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from .time_util import sleep
import random

LIKE_TAG_CLASS = 'coreSpriteHeartOpen'


def get_like_on_feed(browser, amount, scrollLimit=None ):
    '''
        browser - the selenium browser element
        amount - total amount of likes to perform
        scroll_limit - limit the number of scrolls performed

        --------------------------------------
        The function takes in the total amount of likes to perform
        and then sends buttons to be liked, if it has run out of like
        buttons it will perform a scroll
    '''

    # get like buttons
    likes_performed = 0

    while likes_performed <= amount:
        # get the like buttons
        like_buttons = []

        abort = False
        try:
            like_buttons = browser.find_elements_by_class_name(LIKE_TAG_CLASS)
        except selenium.common.exceptions.NoSuchElementException:
            print('Unale to find the like buttons, Aborting')
            abort = True

        if abort:
            break

        if scrollLimit is not None:
            if scrollLimit > 0:
                scrollLimit-=1
            else:
                break

        for button in like_buttons:
            likes_performed += 1
            if not (likes_performed <= amount):
                print('Performed the required number of likes')
                break
            yield button

        print('---> Total Likes uptil now ->', likes_performed)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

