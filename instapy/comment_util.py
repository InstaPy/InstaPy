# -*- coding: utf-8 -*-
""" Module which handles the commenting features """

import random
import emoji

from .time_util import sleep
from .util import update_activity
from .util import add_user_to_blacklist
from .util import click_element
from .util import get_action_delay
from .util import explicit_wait
from .util import extract_text_from_element
from .util import web_address_navigator
from .quota_supervisor import quota_supervisor

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import InvalidElementStateException
from selenium.common.exceptions import NoSuchElementException


def get_comment_input(browser):
    comment_input = browser.find_elements_by_xpath(
        '//textarea[@placeholder = "Add a comment…"]')

    if len(comment_input) <= 0:
        comment_input = browser.find_elements_by_xpath(
            '//input[@placeholder = "Add a comment…"]')

    return comment_input


def open_comment_section(browser, logger):
    missing_comment_elem_warning = (
        "--> Comment Button Not Found!"
        "\t~may cause issues with browser windows of smaller widths")

    comment_elem = browser.find_elements_by_xpath(
        "//button/span[@aria-label='Comment']")

    if len(comment_elem) > 0:
        try:
            click_element(browser, comment_elem[0])

        except WebDriverException:
            logger.warning(missing_comment_elem_warning)

    else:
        logger.warning(missing_comment_elem_warning)


def comment_image(browser, username, comments, blacklist, logger, logfolder):
    """Checks if it should comment on the image"""
    # check action availability
    if quota_supervisor('comments') == 'jump':
        return False, "jumped"

    rand_comment = (random.choice(comments).format(username))
    rand_comment = emoji.demojize(rand_comment)
    rand_comment = emoji.emojize(rand_comment, use_aliases=True)

    open_comment_section(browser, logger)
    comment_input = get_comment_input(browser)

    try:
        if len(comment_input) > 0:
            comment_input[0].clear()
            comment_input = get_comment_input(browser)
            # below, an extra space is added to force
            # the input box to update the reactJS core
            comment_to_be_sent = rand_comment + ' '

            browser.execute_script(
                "arguments[0].value = arguments[1];",
                comment_input[0], comment_to_be_sent)
            # below, it also will remove that extra space added above
            # COS '\b' is a backspace char in ASCII
            comment_input[0].send_keys('\b')
            comment_input = get_comment_input(browser)
            comment_input[0].submit()
            update_activity('comments')

            if blacklist['enabled'] is True:
                action = 'commented'
                add_user_to_blacklist(username,
                                      blacklist['campaign'],
                                      action,
                                      logger,
                                      logfolder)
        else:
            logger.warning("--> Comment Action Likely Failed!"
                           "\t~comment Element was not found")
            return False, "commenting disabled"

    except InvalidElementStateException:
        logger.warning("--> Comment Action Likely Failed!"
                       "\t~encountered `InvalidElementStateException` :/")
        return False, "invalid element state"

    logger.info("--> Commented: {}".format(rand_comment.encode('utf-8')))

    # get the post-comment delay time to sleep
    naply = get_action_delay("comment")
    sleep(naply)

    return True, "success"


def verify_commenting(browser, max, min, mand_words, logger):
    """
     Get the amount of existing existing comments and
    compare it against max & min values defined by user
    """

    commenting_state, msg = is_commenting_enabled(browser, logger)
    if commenting_state is not True:
        disapproval_reason = "--> Not commenting! {}".format(msg)
        return False, disapproval_reason

    comments_count, msg = get_comments_count(browser, logger)
    if not comments_count:
        disapproval_reason = "--> Not commenting! {}".format(msg)
        return False, disapproval_reason

    if max is not None and comments_count > max:
        disapproval_reason = (
            "Not commented on this post! ~more comments exist"
            " off maximum limit at {}"
            .format(comments_count))
        return False, disapproval_reason

    elif min is not None and comments_count < min:
        disapproval_reason = (
            "Not commented on this post! ~less comments exist"
            " off minumum limit at {}"
            .format(comments_count))
        return False, disapproval_reason

    if len(mand_words) != 0:
        try:
            post_desc = browser.execute_script(
                "return window._sharedData.entry_data."
                "PostPage[0].graphql.shortcode_media."
                "edge_media_to_caption.edges[0]['node']['text']"
            ).lower()

        except Exception:
            post_desc = None

        try:
            first_comment = browser.execute_script(
                "return window._sharedData.entry_data."
                "PostPage[0].graphql.shortcode_media."
                "edge_media_to_comment.edges[0]['node']['text']"
            ).lower()

        except Exception:
            first_comment = None

        if ((post_desc is not None and not any(mand_word.lower() in
                                               post_desc for mand_word in
                                               mand_words)) or
                (first_comment is not None and not any(
                    mand_word.lower() in first_comment for
                    mand_word in mand_words))):
            return False, 'mandantory words not in post desc'

    return True, 'Approval'


def get_comments_on_post(browser,
                         owner,
                         poster,
                         amount,
                         post_link,
                         ignore_users,
                         randomize,
                         logger):
    """ Fetch comments data on posts """

    web_address_navigator(browser, post_link)

    orig_amount = amount
    if randomize is True:
        amount = amount * 3

    # check if commenting on the post is enabled
    commenting_state, msg = is_commenting_enabled(browser, logger)
    if commenting_state is not True:
        logger.info(msg)
        return None

    # check if there are any comments in the post
    comments_count, msg = get_comments_count(browser, logger)
    if not comments_count:
        logger.info(msg)
        return None

    # get comments & commenters information
    comments_block_XPath = "//div/div/h3/../../../.."  # efficient location
    # path
    like_button_full_XPath = "//div/span/button/span[@aria-label='Like']"
    unlike_button_full_XPath = "//div/span/button/span[@aria-label='Unlike']"

    comments = []
    commenters = []
    # wait for page fully load [IMPORTANT!]
    explicit_wait(browser, "PFL", [], logger, 10)

    try:
        all_comment_like_buttons = browser.find_elements_by_xpath(
            like_button_full_XPath)
        if all_comment_like_buttons:
            comments_block = browser.find_elements_by_xpath(
                comments_block_XPath)
            for comment_line in comments_block:
                commenter_elem = comment_line.find_element_by_xpath('//h3/a')
                commenter = extract_text_from_element(commenter_elem)
                if (commenter and
                        commenter not in [owner, poster, ignore_users] and
                        commenter not in commenters):
                    commenters.append(commenter)
                else:
                    continue

                comment_elem = comment_line.find_elements_by_tag_name(
                    "span")[0]
                comment = extract_text_from_element(comment_elem)
                if comment:
                    comments.append(comment)
                else:
                    commenters.remove(commenters[-1])
                    continue

        else:
            comment_unlike_buttons = browser.find_elements_by_xpath(
                unlike_button_full_XPath)
            if comment_unlike_buttons:
                logger.info("There are {} comments on this post and all "
                            "of them are already liked."
                            .format(len(comment_unlike_buttons)))
            else:
                logger.info(
                    "There are no any comments available on this post.")
            return None

    except NoSuchElementException:
        logger.info("Failed to get comments on this post.")
        return None

    if not comments:
        logger.info("Could not grab any usable comments from this post..")
        return None

    else:
        comment_data = list(zip(commenters, comments))
        if randomize is True:
            random.shuffle(comment_data)

        if len(comment_data) < orig_amount:
            logger.info("Could grab only {} usable comments from this post.."
                        .format(len(comment_data)))
        else:
            logger.info("Grabbed {} usable comments from this post.."
                        .format(len(comment_data)))

        return comment_data


def is_commenting_enabled(browser, logger):
    """ Find out if commenting on the post is enabled """

    try:
        comments_disabled = browser.execute_script(
            "return window._sharedData.entry_data."
            "PostPage[0].graphql.shortcode_media.comments_disabled")

    except WebDriverException:
        try:
            browser.execute_script("location.reload()")
            update_activity()

            comments_disabled = browser.execute_script(
                "return window._sharedData.entry_data."
                "PostPage[0].graphql.shortcode_media.comments_disabled")

        except Exception as e:
            msg = ("Failed to check comments' status for verification!\n\t{}"
                   .format(str(e).encode("utf-8")))
            return False, "Failure"

    if comments_disabled is True:
        msg = "Comments are disabled for this post."
        return False, msg

    return True, "Success"


def get_comments_count(browser, logger):
    """ Get the number of total comments in the post """
    try:
        comments_count = browser.execute_script(
            "return window._sharedData.entry_data."
            "PostPage[0].graphql.shortcode_media."
            "edge_media_to_comment.count")

    except Exception as e:
        msg = ("Failed to get comments' count!\n\t{}"
               .format(str(e).encode("utf-8")))
        return None, msg

    if not comments_count:
        if comments_count == 0:
            msg = "There are no any comments in the post."
            return 0, msg
        else:
            msg = "Couldn't get comments' count."
            return None, msg

    return comments_count, "Success"
