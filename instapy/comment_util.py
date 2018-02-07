# -*- coding: utf-8 -*-
"""Module which handles the commenting features"""
from random import choice
from .time_util import sleep
from .util import update_activity
from .util import add_user_to_blacklist
from selenium.common.exceptions import WebDriverException
import emoji


def get_comment_input(browser):
    comment_input = browser.find_elements_by_xpath(
        '//textarea[@placeholder = "Add a comment…"]')
    if len(comment_input) <= 0:
        comment_input = browser.find_elements_by_xpath(
            '//input[@placeholder = "Add a comment…"]')
    return comment_input


def open_comment_section(browser):
    missing_comment_elem_warning = (
        '--> Warning: Comment Button Not Found:'
        ' May cause issues with browser windows of smaller widths')
    comment_elem = browser.find_elements_by_xpath(
        "//a[@role='button']/span[text()='Comment']/..")
    if len(comment_elem) > 0:
        try:
            browser.execute_script(
                "arguments[0].click();", comment_elem[0])
        except WebDriverException:
            print(missing_comment_elem_warning)
    else:
        print(missing_comment_elem_warning)


def comment_image(browser, username, comments, blacklist, logger, logfolder, insta_username):
    """Checks if it should comment on the image"""
    rand_comment = (choice(comments).format(username))
    rand_comment = emoji.demojize(rand_comment)
    rand_comment = emoji.emojize(rand_comment, use_aliases=True)

    open_comment_section(browser)
    comment_input = get_comment_input(browser)

    if len(comment_input) > 0:
        comment_input[0].clear()
        comment_input = get_comment_input(browser)

        browser.execute_script(
            "arguments[0].value = '" + rand_comment + " ';", comment_input[0])
        # An extra space is added here and then deleted.
        # This forces the input box to update the reactJS core
        comment_input[0].send_keys("\b")
        comment_input = get_comment_input(browser)
        comment_input[0].submit()
        update_activity('comments', insta_username=insta_username)
        if blacklist['enabled'] is True:
            action = 'commented'
            add_user_to_blacklist(
                browser, username, blacklist['campaign'], action, logger, logfolder
            )
    else:
        logger.warning('--> Warning: Comment Action Likely Failed:'
                       ' Comment Element not found')

    logger.info("--> Commented: {}".format(rand_comment.encode('utf-8')))
    sleep(2)

    return 1
