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
from .event import Event
from .quota_supervisor import quota_supervisor
from .xpath import read_xpath

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import InvalidElementStateException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def get_comment_input(browser):
    comment_input = browser.find_elements_by_xpath(
        read_xpath(get_comment_input.__name__, "comment_input")
    )

    if len(comment_input) <= 0:
        comment_input = browser.find_elements_by_xpath(
            read_xpath(get_comment_input.__name__, "placeholder")
        )

    return comment_input


def open_comment_section(browser, logger):
    missing_comment_elem_warning = (
        "--> Comment Button Not Found!"
        "\t~may cause issues with browser windows of smaller widths"
    )

    comment_elem = browser.find_elements_by_xpath(
        read_xpath(open_comment_section.__name__, "comment_elem")
    )

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
    if quota_supervisor("comments") == "jump":
        return False, "jumped"

    rand_comment = random.choice(comments).format(username)
    rand_comment = emoji.demojize(rand_comment)
    rand_comment = emoji.emojize(rand_comment, use_aliases=True)

    open_comment_section(browser, logger)
    # wait, to avoid crash
    sleep(3)
    comment_input = get_comment_input(browser)

    try:
        if len(comment_input) > 0:
            # wait, to avoid crash
            sleep(2)
            comment_input = get_comment_input(browser)
            # below, an extra space is added to force
            # the input box to update the reactJS core
            comment_to_be_sent = rand_comment

            # wait, to avoid crash
            sleep(2)
            # click on textarea/comment box and enter comment
            (
                ActionChains(browser)
                .move_to_element(comment_input[0])
                .click()
                .send_keys(comment_to_be_sent)
                .perform()
            )
            # wait, to avoid crash
            sleep(2)
            # post comment / <enter>
            (
                ActionChains(browser)
                .move_to_element(comment_input[0])
                .send_keys(Keys.ENTER)
                .perform()
            )

            update_activity(
                browser,
                action="comments",
                state=None,
                logfolder=logfolder,
                logger=logger,
            )

            if blacklist["enabled"] is True:
                action = "commented"
                add_user_to_blacklist(
                    username, blacklist["campaign"], action, logger, logfolder
                )
        else:
            logger.warning(
                "--> Comment Action Likely Failed!" "\t~comment Element was not found"
            )
            return False, "commenting disabled"

    except InvalidElementStateException:
        logger.warning(
            "--> Comment Action Likely Failed!"
            "\t~encountered `InvalidElementStateException` :/"
        )
        return False, "invalid element state"

    logger.info("--> Commented: {}".format(rand_comment.encode("utf-8")))
    Event().commented(username)

    # get the post-comment delay time to sleep
    naply = get_action_delay("comment")
    sleep(naply)

    return True, "success"


def verify_commenting(browser, maximum, minimum, logger):
    """
     Get the amount of existing existing comments and
    compare it against maximum & minimum values defined by user
    """

    commenting_state, msg = is_commenting_enabled(browser, logger)
    if commenting_state is not True:
        disapproval_reason = "--> Not commenting! {}".format(msg)
        return False, disapproval_reason

    comments_count, msg = get_comments_count(browser, logger)
    if comments_count is None:
        disapproval_reason = "--> Not commenting! {}".format(msg)
        return False, disapproval_reason

    if maximum is not None and comments_count > maximum:
        disapproval_reason = (
            "Not commented on this post! ~more comments exist"
            " off maximum limit at {}".format(comments_count)
        )
        return False, disapproval_reason

    elif minimum is not None and comments_count < minimum:
        disapproval_reason = (
            "Not commented on this post! ~less comments exist"
            " off minumum limit at {}".format(comments_count)
        )
        return False, disapproval_reason

    return True, "Approval"


# Evaluate a mandatory words list against a text
def evaluate_mandatory_words(text, mandatory_words_list):
    for word in mandatory_words_list:
        if isinstance(word, list):
            # this is a list so we apply an 'AND' condition to all of them
            if all(w.lower() in text for w in word):
                return True
        else:
            if word.lower() in text:
                return True
    return False


def verify_mandatory_words(
    mand_words, comments, browser, logger,
):
    if len(mand_words) > 0 or isinstance(comments[0], dict):
        try:
            post_desc = browser.execute_script(
                "return window.__additionalData[Object.keys(window.__additionalData)[0]].data."
                "graphql.shortcode_media."
                "edge_media_to_caption.edges[0]['node']['text']"
            ).lower()

        except Exception:
            post_desc = None

        try:
            first_comment = browser.execute_script(
                "return window.__additionalData[Object.keys(window.__additionalData)[0]].data."
                "graphql.shortcode_media."
                "edge_media_to_parent_comment.edges[0]['node']['text']"
            ).lower()

        except Exception:
            first_comment = None

        if post_desc is None and first_comment is None:
            return False, [], "couldn't get post description and comments"

        text = (
            post_desc
            if post_desc is not None
            else "" + " " + first_comment
            if first_comment is not None
            else ""
        )

        if len(mand_words) > 0:
            if not evaluate_mandatory_words(text, mand_words):
                return False, [], "mandatory words not in post desc"

        if isinstance(comments[0], dict):
            # The comments definition is a compound definition of conditions and comments
            for compund_comment in comments:
                if evaluate_mandatory_words(text, compund_comment["mandatory_words"]):
                    return True, compund_comment["comments"], "Approval"
            return (
                False,
                [],
                "Coulnd't match the mandatory words in any comment definition",
            )

    return True, comments, "Approval"


def get_comments_on_post(
    browser, owner, poster, amount, post_link, ignore_users, randomize, logger
):
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

    # efficient location
    comments_block_XPath = read_xpath(get_comments_on_post.__name__, "comments_block")
    # path
    like_button_full_XPath = read_xpath(
        get_comments_on_post.__name__, "like_button_full_XPath"
    )
    unlike_button_full_XPath = read_xpath(
        get_comments_on_post.__name__, "unlike_button_full_XPath"
    )

    comments = []
    commenters = []
    # wait for page fully load [IMPORTANT!]
    explicit_wait(browser, "PFL", [], logger, 10)

    try:
        all_comment_like_buttons = browser.find_elements_by_xpath(
            like_button_full_XPath
        )
        if all_comment_like_buttons:
            comments_block = browser.find_elements_by_xpath(comments_block_XPath)
            for comment_line in comments_block:
                commenter_elem = comment_line.find_element_by_xpath(
                    read_xpath(get_comments_on_post.__name__, "commenter_elem")
                )
                commenter = extract_text_from_element(commenter_elem)
                if (
                    commenter
                    and commenter not in [owner, poster, ignore_users]
                    and commenter not in commenters
                ):
                    commenters.append(commenter)
                else:
                    continue

                comment_elem = comment_line.find_elements_by_tag_name("span")[0]
                comment = extract_text_from_element(comment_elem)
                if comment:
                    comments.append(comment)
                else:
                    commenters.remove(commenters[-1])
                    continue

        else:
            comment_unlike_buttons = browser.find_elements_by_xpath(
                unlike_button_full_XPath
            )
            if comment_unlike_buttons:
                logger.info(
                    "There are {} comments on this post and all "
                    "of them are already liked.".format(len(comment_unlike_buttons))
                )
            else:
                logger.info("There are no any comments available on this post.")
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
            logger.info(
                "Could grab only {} usable comments from this post..".format(
                    len(comment_data)
                )
            )
        else:
            logger.info(
                "Grabbed {} usable comments from this post..".format(len(comment_data))
            )

        return comment_data


def is_commenting_enabled(browser, logger):
    """ Find out if commenting on the post is enabled """

    try:
        comments_disabled = browser.execute_script(
            "return window.__additionalData[Object.keys(window.__additionalData)[0]].data"
            ".graphql.shortcode_media.comments_disabled"
        )

    except WebDriverException:
        try:
            browser.execute_script("location.reload()")
            update_activity(browser, state=None)

            comments_disabled = browser.execute_script(
                "return window.__additionalData[Object.keys(window.__additionalData)[0]].data"
                ".graphql.shortcode_media.comments_disabled"
            )

        except Exception as e:
            msg = "Failed to check comments' status for verification!\n\t{}".format(
                str(e).encode("utf-8")
            )
            return False, msg

    if comments_disabled is True:
        msg = "Comments are disabled for this post."
        return False, msg

    return True, "Success"


def get_comments_count(browser, logger):
    """ Get the number of total comments in the post """
    try:
        comments_count = browser.execute_script(
            "return window.__additionalData[Object.keys(window.__additionalData)[0]].data"
            ".graphql.shortcode_media.edge_media_preview_comment.count"
        )

        # media_edge_string = get_media_edge_comment_string(media)
        # comments_count = media[media_edge_string]["count"]

    except Exception as e:
        try:
            comments_count = browser.execute_script(
                "return window.__additionalData[Object.keys(window.__additionalData)[0]].data"
                ".graphql.shortcode_media.edge_media_preview_comment.count"
            )

        except Exception as e:
            msg = "Failed to get comments' count!\n\t{}".format(str(e).encode("utf-8"))
            return None, msg

    # if not comments_count:
    #     if comments_count == 0:
    #         msg = "There are no any comments in the post."
    #         return 0, msg
    #     else:
    #         msg = "Couldn't get comments' count."
    #         return None, msg

    return comments_count, "Success"


def process_comments(
    comments,
    clarifai_comments,
    delimit_commenting,
    max_comments,
    min_comments,
    comments_mandatory_words,
    user_name,
    blacklist,
    browser,
    logger,
    logfolder,
):

    # comments
    if delimit_commenting:
        (commenting_approved, disapproval_reason,) = verify_commenting(
            browser, max_comments, min_comments, logger,
        )
        if not commenting_approved:
            logger.info(disapproval_reason)
            return False

    (
        commenting_approved,
        selected_comments,
        disapproval_reason,
    ) = verify_mandatory_words(comments_mandatory_words, comments, browser, logger,)
    if not commenting_approved:
        logger.info(disapproval_reason)
        return False

    if len(clarifai_comments) > 0:
        selected_comments = clarifai_comments

    # smart commenting
    if comments:
        comment_state, msg = comment_image(
            browser, user_name, selected_comments, blacklist, logger, logfolder,
        )
        return comment_state
