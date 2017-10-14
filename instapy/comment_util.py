# -*- coding: utf-8 -*-
"""Module which handles the commenting features"""
from random import choice
from .time_util import sleep
import emoji


def comment_image(browser, comments):
    """Checks if it should comment on the image"""
    rand_comment = (choice(comments))
    rand_comment = emoji.demojize(rand_comment)
    rand_comment = emoji.emojize(rand_comment, use_aliases=True)

    comment_input = browser.find_elements_by_xpath(
        '//textarea[@placeholder = "Add a comment…"]')
    if len(comment_input) <= 0:
        comment_input = browser.find_elements_by_xpath(
            '//input[@placeholder = "Add a comment…"]')

    if len(comment_input) > 0:
        browser.execute_script(
            "arguments[0].value = '" + rand_comment + " ';", comment_input[0])
        # An extra space is added here and then deleted.
        # This forces the input box to update the reactJS core
        comment_input[0].send_keys("\b")
        comment_input[0].submit()
    else:
        print('--> Warning: Comment Action Likely Failed:'
              ' Comment Element not found')

    print("--> Commented: {}".format(rand_comment.encode('utf-8')))
    sleep(2)

    return 1
