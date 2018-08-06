# -*- coding: utf-8 -*-
"""Module which handles the commenting features"""
from random import choice
from .time_util import sleep
from .util import update_activity
from .util import add_user_to_blacklist
from .util import format_number
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import InvalidElementStateException
from selenium.common.exceptions import NoSuchElementException
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


def comment_image(browser, username, comments, blacklist, logger, logfolder):
    """Checks if it should comment on the image"""
    rand_comment = (choice(comments).format(username))
    rand_comment = emoji.demojize(rand_comment)
    rand_comment = emoji.emojize(rand_comment, use_aliases=True)

    open_comment_section(browser)
    comment_input = get_comment_input(browser)

    try:
        if len(comment_input) > 0:
            comment_input[0].clear()
            comment_input = get_comment_input(browser)

            browser.execute_script(
                "arguments[0].value = arguments[1];", comment_input[0], rand_comment+' ')
            # An extra space is added here and then deleted.
            # This forces the input box to update the reactJS core
            comment_input[0].send_keys("\b")
            comment_input = get_comment_input(browser)
            comment_input[0].submit()
            update_activity('comments')
            if blacklist['enabled'] is True:
                action = 'commented'
                add_user_to_blacklist(
                    username, blacklist['campaign'], action, logger, logfolder
                )
        else:
            logger.warning('--> Warning: Comment Action Likely Failed:'
                           ' Comment Element not found')
    except InvalidElementStateException:
        logger.warning('--> Warning: Comment Action Likely Failed: Probably InvalidElementStateException')

    logger.info("--> Commented: {}".format(rand_comment.encode('utf-8')))
    sleep(2)

    return 1


def verify_commenting(browser, max, min, logger):
        """ Get the amount of existing existing comments and compare it against max & min values defined by user """
        try:
            comments_disabled = browser.execute_script(
                "return window._sharedData.entry_data."
                "PostPage[0].graphql.shortcode_media.comments_disabled")
        except WebDriverException:
            try:
                browser.execute_script("location.reload()")
                comments_disabled = browser.execute_script(
                    "return window._sharedData.entry_data."
                    "PostPage[0].graphql.shortcode_media.comments_disabled")            
            except Exception as e:
                logger.info("Failed to check comments' status for verification!\n\t{}".format(str(e).encode("utf-8"))) 
                return True, 'Verification failure'

        if comments_disabled == True:
            disapproval_reason = "Not commenting ~comments are disabled for this post"
            return False, disapproval_reason
        try:
            comments_count = browser.execute_script(
                "return window._sharedData.entry_data."
                "PostPage[0].graphql.shortcode_media.edge_media_to_comment.count")
        except Exception as e:
            logger.info("Failed to check comments' count for verification!\n\t{}".format(str(e).encode("utf-8"))) 
            return True, 'Verification failure'

        if max is not None and comments_count > max:
            disapproval_reason = "Not commented on this post! ~more comments exist off maximum limit at {}".format(comments_count)
            return False, disapproval_reason
        elif min is not None and comments_count < min:
            disapproval_reason = "Not commented on this post! ~less comments exist off minumum limit at {}".format(comments_count)
            return False, disapproval_reason

        return True, 'Approval'