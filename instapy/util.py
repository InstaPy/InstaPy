""" Common utilities """
import time
import datetime
from math import ceil
from math import radians
from math import degrees as rad2deg
from math import cos
import random
import re
import regex
import signal
import os
import sys
from sys import exit as clean_exit
from platform import system
from platform import python_version
from subprocess import call
import csv
import sqlite3
import json
from contextlib import contextmanager
from tempfile import gettempdir
import emoji
from emoji.unicode_codes import UNICODE_EMOJI
from argparse import ArgumentParser

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

from .time_util import sleep
from .time_util import sleep_actual
from .database_engine import get_database
from .quota_supervisor import quota_supervisor
from .settings import Settings

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException

from .xpath import read_xpath
from .event import Event

default_profile_pic_instagram = [
    "https://instagram.flas1-2.fna.fbcdn.net/vp"
    "/a8539c22ed9fec8e1c43b538b1ebfd1d/5C5A1A7A/t51.2885-19"
    "/11906329_960233084022564_1448528159_a.jpg",
    "https://scontent-yyz1-1.cdninstagram.com/vp"
    "/a8539c22ed9fec8e1c43b538b1ebfd1d/5C5A1A7A/t51.2885-19"
    "/11906329_960233084022564_1448528159_a.jpg",
    "https://instagram.faep12-1.fna.fbcdn.net/vp"
    "/a8539c22ed9fec8e1c43b538b1ebfd1d/5C5A1A7A/t51.2885-19"
    "/11906329_960233084022564_1448528159_a.jpg",
    "https://instagram.fbts2-1.fna.fbcdn.net/vp"
    "/a8539c22ed9fec8e1c43b538b1ebfd1d/5C5A1A7A/t51.2885-19"
    "/11906329_960233084022564_1448528159_a.jpg",
    "https://scontent-mia3-1.cdninstagram.com/vp"
    "/a8539c22ed9fec8e1c43b538b1ebfd1d/5C5A1A7A/t51.2885-19"
    "/11906329_960233084022564_1448528159_a.jpg",
]

next_screenshot = 1


def is_private_profile(browser, logger, following=True):
    is_private = None
    try:
        is_private = browser.execute_script(
            "return window.__additionalData[Object.keys(window.__additionalData)[0]]."
            "data.graphql.user.is_private"
        )

    except WebDriverException:
        try:
            browser.execute_script("location.reload()")
            update_activity(browser, state=None)

            is_private = browser.execute_script(
                "return window._sharedData.entry_data."
                "ProfilePage[0].graphql.user.is_private"
            )

        except WebDriverException:
            return None

    # double check with xpath that should work only when we not follwoing a
    # user
    if is_private and not following:
        logger.info("Is private account you're not following.")
        body_elem = browser.find_element_by_tag_name("body")
        is_private = body_elem.find_element_by_xpath(
            read_xpath(is_private_profile.__name__, "is_private")
        )

    return is_private


# Evaluate a mandatory words list against a text
def evaluate_mandatory_words(text, mandatory_words_list, level=0):
    if level % 2 == 0:
        # this is an "or" level so at least one of the words of compound sub-conditions should match
        for word in mandatory_words_list:
            if isinstance(word, list):
                res = evaluate_mandatory_words(text, word, level + 1)
                if res:
                    return True
            elif word.lower() in text:
                return True
        return False
    else:
        # this is an "and" level so all of the words and compound sub-conditions must match
        for word in mandatory_words_list:
            if isinstance(word, list):
                res = evaluate_mandatory_words(text, word, level + 1)
                if not res:
                    return False
            elif word.lower() not in text:
                return False
        return True


def validate_username(
    browser,
    username_or_link,
    own_username,
    ignore_users,
    blacklist,
    potency_ratio,
    delimit_by_numbers,
    max_followers,
    max_following,
    min_followers,
    min_following,
    min_posts,
    max_posts,
    skip_private,
    skip_private_percentage,
    skip_no_profile_pic,
    skip_no_profile_pic_percentage,
    skip_business,
    skip_non_business,
    skip_business_percentage,
    skip_business_categories,
    dont_skip_business_categories,
    skip_bio_keyword,
    mandatory_bio_keywords,
    logger,
    logfolder,
):
    """Check if we can interact with the user"""

    # some features may not provide `username` and in those cases we will
    # get it from post's page.
    if "/" in username_or_link:
        link = username_or_link  # if there is a `/` in `username_or_link`,
        # then it is a `link`

        # check URL of the webpage, if it already is user's profile page,
        # then do not navigate to it again
        web_address_navigator(browser, link)

        try:
            username = browser.execute_script(
                "return window._sharedData.entry_data."
                "PostPage[0].graphql.shortcode_media.owner.username"
            )

        except WebDriverException:
            try:
                browser.execute_script("location.reload()")
                update_activity(browser, state=None)

                username = browser.execute_script(
                    "return window._sharedData.entry_data."
                    "PostPage[0].graphql.shortcode_media.owner.username"
                )

            except WebDriverException:
                logger.error(
                    "Username validation failed!\t~cannot get the post "
                    "owner's username"
                )
                inap_msg = (
                    "---> Sorry, this page isn't available!\t~either "
                    "link is broken or page is removed\n"
                )
                return False, inap_msg

    else:
        username = username_or_link  # if there is no `/` in
        # `username_or_link`, then it is a `username`

    if username == own_username:
        inap_msg = "---> Username '{}' is yours!\t~skipping user\n".format(own_username)
        return False, inap_msg

    if username in ignore_users:
        inap_msg = (
            "---> '{}' is in the `ignore_users` list\t~skipping "
            "user\n".format(username)
        )
        return False, inap_msg

    blacklist_file = "{}blacklist.csv".format(logfolder)
    blacklist_file_exists = os.path.isfile(blacklist_file)
    if blacklist_file_exists:
        with open("{}blacklist.csv".format(logfolder), "rt") as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                for field in row:
                    if field == username:
                        logger.info("Username in BlackList: {} ".format(username))
                        return (
                            False,
                            "---> {} is in blacklist  ~skipping "
                            "user\n".format(username),
                        )

    # Checks the potential of target user by relationship status in order
    # to delimit actions within the desired boundary
    if (
        potency_ratio
        or delimit_by_numbers
        and (max_followers or max_following or min_followers or min_following)
    ):

        relationship_ratio = None
        reverse_relationship = False

        # get followers & following counts
        followers_count, following_count = get_relationship_counts(
            browser, username, logger
        )

        if potency_ratio and potency_ratio < 0:
            potency_ratio *= -1
            reverse_relationship = True

        # division by zero is bad
        followers_count = 1 if followers_count == 0 else followers_count
        following_count = 1 if following_count == 0 else following_count

        if followers_count and following_count:
            relationship_ratio = (
                float(followers_count) / float(following_count)
                if not reverse_relationship
                else float(following_count) / float(followers_count)
            )

        logger.info(
            "User: '{}'  |> followers: {}  |> following: {}  |> relationship "
            "ratio: {}".format(
                username,
                followers_count if followers_count else "unknown",
                following_count if following_count else "unknown",
                truncate_float(relationship_ratio, 2)
                if relationship_ratio
                else "unknown",
            )
        )

        if followers_count or following_count:
            if potency_ratio and not delimit_by_numbers:
                if relationship_ratio and relationship_ratio < potency_ratio:
                    inap_msg = (
                        "'{}' is not a {} with the relationship ratio of {}  "
                        "~skipping user\n".format(
                            username,
                            "potential user"
                            if not reverse_relationship
                            else "massive follower",
                            truncate_float(relationship_ratio, 2),
                        )
                    )
                    return False, inap_msg

            elif delimit_by_numbers:
                if followers_count:
                    if max_followers:
                        if followers_count > max_followers:
                            inap_msg = (
                                "User '{}'s followers count exceeds maximum "
                                "limit  ~skipping user\n".format(username)
                            )
                            return False, inap_msg

                    if min_followers:
                        if followers_count < min_followers:
                            inap_msg = (
                                "User '{}'s followers count is less than "
                                "minimum limit  ~skipping user\n".format(username)
                            )
                            return False, inap_msg

                if following_count:
                    if max_following:
                        if following_count > max_following:
                            inap_msg = (
                                "User '{}'s following count exceeds maximum "
                                "limit  ~skipping user\n".format(username)
                            )
                            return False, inap_msg

                    if min_following:
                        if following_count < min_following:
                            inap_msg = (
                                "User '{}'s following count is less than "
                                "minimum limit  ~skipping user\n".format(username)
                            )
                            return False, inap_msg

                if potency_ratio:
                    if relationship_ratio and relationship_ratio < potency_ratio:
                        inap_msg = (
                            "'{}' is not a {} with the relationship ratio of "
                            "{}  ~skipping user\n".format(
                                username,
                                "potential user"
                                if not reverse_relationship
                                else "massive " "follower",
                                truncate_float(relationship_ratio, 2),
                            )
                        )
                        return False, inap_msg

    if min_posts or max_posts or skip_private or skip_no_profile_pic or skip_business:
        user_link = "https://www.instagram.com/{}/".format(username)
        web_address_navigator(browser, user_link)

    if min_posts or max_posts:
        # if you are interested in relationship number of posts boundaries
        try:
            number_of_posts = getUserData(
                "graphql.user.edge_owner_to_timeline_media.count", browser
            )
        except WebDriverException:
            logger.error("~cannot get number of posts for username")
            inap_msg = "---> Sorry, couldn't check for number of posts of " "username\n"
            return False, inap_msg
        if max_posts:
            if number_of_posts > max_posts:
                inap_msg = (
                    "Number of posts ({}) of '{}' exceeds the maximum limit "
                    "given {}\n".format(number_of_posts, username, max_posts)
                )
                return False, inap_msg
        if min_posts:
            if number_of_posts < min_posts:
                inap_msg = (
                    "Number of posts ({}) of '{}' is less than the minimum "
                    "limit given {}\n".format(number_of_posts, username, min_posts)
                )
                return False, inap_msg

    # Skip users

    # skip private
    if skip_private:
        try:
            browser.find_element_by_xpath(
                "//*[contains(text(), 'This Account is Private')]"
            )
            is_private = True
        except NoSuchElementException:
            is_private = False
        if is_private and (random.randint(0, 100) <= skip_private_percentage):
            return False, "{} is private account, by default skip\n".format(username)

    # skip no profile pic
    if skip_no_profile_pic:
        try:
            profile_pic = getUserData("graphql.user.profile_pic_url", browser)
        except WebDriverException:
            logger.error("~cannot get the post profile pic url")
            return False, "---> Sorry, couldn't get if user profile pic url\n"
        if (
            profile_pic in default_profile_pic_instagram
            or str(profile_pic).find("11906329_960233084022564_1448528159_a.jpg") > 0
        ) and (random.randint(0, 100) <= skip_no_profile_pic_percentage):
            return False, "{} has default instagram profile picture\n".format(username)

    # skip business
    if skip_business or skip_non_business:
        # if is business account skip under conditions
        try:
            is_business_account = getUserData(
                "graphql.user.is_business_account", browser
            )
        except WebDriverException:
            logger.error("~cannot get if user has business account active")
            return (
                False,
                "---> Sorry, couldn't get if user has business " "account active\n",
            )

        if skip_non_business and not is_business_account:
            return (
                False,
                "---> Skiping non business because skip_non_business set to True",
            )

        if is_business_account:
            try:
                category = getUserData("graphql.user.business_category_name", browser)
            except WebDriverException:
                logger.error("~cannot get category name for user")
                return False, "---> Sorry, couldn't get category name for " "user\n"

            if len(skip_business_categories) == 0:
                # skip if not in dont_include
                if category not in dont_skip_business_categories:
                    if len(dont_skip_business_categories) == 0 and (
                        random.randint(0, 100) <= skip_business_percentage
                    ):
                        return False, "'{}' has a business account\n".format(username)
                    else:
                        return (
                            False,
                            (
                                "'{}' has a business account in the "
                                "undesired category of '{}'\n".format(
                                    username, category
                                )
                            ),
                        )
            else:
                if category in skip_business_categories:
                    return (
                        False,
                        (
                            "'{}' has a business account in the "
                            "undesired category of '{}'\n".format(username, category)
                        ),
                    )

    if len(skip_bio_keyword) > 0 or len(mandatory_bio_keywords) > 0:
        # if contain stop words then skip
        try:
            profile_bio = getUserData("graphql.user.biography", browser).lower()
        except WebDriverException:
            logger.error("~cannot get user bio")
            return False, "---> Sorry, couldn't get get user bio " "account active\n"
        for bio_keyword in skip_bio_keyword:
            if bio_keyword.lower() in profile_bio:
                return (
                    False,
                    "{} has a bio keyword of {}, by default skip\n".format(
                        username, bio_keyword
                    ),
                )
        # the mandatory keywords applies to the username as well as the bio text
        if not evaluate_mandatory_words(
            username + " " + profile_bio, mandatory_bio_keywords
        ):
            return False, "Mandatory bio keywords not found"

    # if everything is ok
    return True, "Valid user"


def getUserData(
    query,
    browser,
    basequery="return window.__additionalData[Object.keys(window.__additionalData)[0]].data.",
):
    try:
        data = browser.execute_script(basequery + query)
        return data
    except WebDriverException:
        browser.execute_script("location.reload()")
        update_activity(browser, state=None)

        data = browser.execute_script(
            "return window._sharedData." "entry_data.ProfilePage[0]." + query
        )
        return data


def update_activity(
    browser=None, action="server_calls", state=None, logfolder=None, logger=None
):
    """
        1. Record every Instagram server call (page load, content load, likes,
        comments, follows, unfollow)
        2. Take rotative screenshots
        3. update connection state and record to .json file
    """
    # check action availability
    quota_supervisor("server_calls")

    # take screen shot
    if browser and logfolder and logger:
        take_rotative_screenshot(browser, logfolder)

    # update state to JSON file
    if state and logfolder and logger:
        try:
            path = "{}state.json".format(logfolder)
            data = {}
            # check if file exists and has content
            if os.path.isfile(path) and os.path.getsize(path) > 0:
                # load JSON file
                with open(path, "r") as json_file:
                    data = json.load(json_file)

            # update connection state
            connection_data = {}
            connection_data["connection"] = state
            data["state"] = connection_data

            # write to JSON file
            with open(path, "w") as json_file:
                json.dump(data, json_file, indent=4)
        except Exception:
            logger.warn("Unable to update JSON state file")

    # in case is just a state update and there is no server call
    if action is None:
        return

    # get a DB, start a connection and sum a server call
    db, id = get_database()
    conn = sqlite3.connect(db)

    with conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        # collect today data
        cur.execute(
            "SELECT * FROM recordActivity WHERE profile_id=:var AND "
            "STRFTIME('%Y-%m-%d %H', created) == STRFTIME('%Y-%m-%d "
            "%H', 'now', 'localtime')",
            {"var": id},
        )
        data = cur.fetchone()

        if data is None:
            # create a new record for the new day
            cur.execute(
                "INSERT INTO recordActivity VALUES "
                "(?, 0, 0, 0, 0, 1, STRFTIME('%Y-%m-%d %H:%M:%S', "
                "'now', 'localtime'))",
                (id,),
            )

        else:
            # sqlite3.Row' object does not support item assignment -> so,
            # convert it into a new dict
            data = dict(data)

            # update
            data[action] += 1
            quota_supervisor(action, update=True)

            if action != "server_calls":
                # always update server calls
                data["server_calls"] += 1
                quota_supervisor("server_calls", update=True)

            sql = (
                "UPDATE recordActivity set likes = ?, comments = ?, "
                "follows = ?, unfollows = ?, server_calls = ?, "
                "created = STRFTIME('%Y-%m-%d %H:%M:%S', 'now', "
                "'localtime') "
                "WHERE  profile_id=? AND STRFTIME('%Y-%m-%d %H', created) "
                "== "
                "STRFTIME('%Y-%m-%d %H', 'now', 'localtime')"
            )

            cur.execute(
                sql,
                (
                    data["likes"],
                    data["comments"],
                    data["follows"],
                    data["unfollows"],
                    data["server_calls"],
                    id,
                ),
            )

        # commit the latest changes
        conn.commit()


def add_user_to_blacklist(username, campaign, action, logger, logfolder):
    file_exists = os.path.isfile("{}blacklist.csv".format(logfolder))
    fieldnames = ["date", "username", "campaign", "action"]
    today = datetime.date.today().strftime("%m/%d/%y")

    try:
        with open("{}blacklist.csv".format(logfolder), "a+") as blacklist:
            writer = csv.DictWriter(blacklist, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(
                {
                    "date": today,
                    "username": username,
                    "campaign": campaign,
                    "action": action,
                }
            )
    except Exception as err:
        logger.error("blacklist dictWrite error {}".format(err))

    logger.info(
        "--> {} added to blacklist for {} campaign (action: {})".format(
            username, campaign, action
        )
    )


def get_active_users(browser, username, posts, boundary, logger):
    """Returns a list with usernames who liked the latest n posts"""

    user_link = "https://www.instagram.com/{}/".format(username)

    # check URL of the webpage, if it already is user's profile page,
    # then do not navigate to it again
    web_address_navigator(browser, user_link)

    try:
        total_posts = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].graphql.user.edge_owner_to_timeline_media.count"
        )
    except WebDriverException:
        try:
            topCount_elements = browser.find_elements_by_xpath(
                read_xpath(get_active_users.__name__, "topCount_elements")
            )

            if topCount_elements:  # prevent an empty string scenario
                total_posts = format_number(topCount_elements[0].text)
            else:
                logger.info(
                    "Failed to get posts count on your profile!  ~empty " "string"
                )
                total_posts = None
        except NoSuchElementException:
            logger.info("Failed to get posts count on your profile!")
            total_posts = None

    # if posts > total user posts, assume total posts
    posts = (
        posts if total_posts is None else total_posts if posts > total_posts else posts
    )

    active_users = []
    sc_rolled = 0
    start_time = time.time()
    too_many_requests = 0  # helps to prevent misbehaviours when requests
    # list of active users repeatedly within less than 10 min of breaks

    message = (
        "~collecting the entire usernames from posts without a boundary!\n"
        if boundary is None
        else "~collecting only the visible usernames from posts without scrolling "
        "at the boundary of zero..\n"
        if boundary == 0
        else "~collecting the usernames from posts with the boundary of {}"
        "\n".format(boundary)
    )
    # posts argument is the number of posts to collect usernames
    logger.info(
        "Getting active users who liked the latest {} posts:\n  {}".format(
            posts, message
        )
    )

    count = 1
    checked_posts = 0
    while count <= posts:
        # load next post
        try:
            latest_post = browser.find_element_by_xpath(
                read_xpath(get_active_users.__name__, "profile_posts").format(count)
            )
            # avoid no posts
            if latest_post:
                click_element(browser, latest_post)
        except (NoSuchElementException, WebDriverException):
            logger.warning("Failed to click on the latest post to grab active likers!")
            return []
        try:
            checked_posts += 1
            sleep_actual(2)

            try:
                likers_count = browser.find_element_by_xpath(
                    read_xpath(get_active_users.__name__, "likers_count")
                ).text
                if likers_count:  # prevent an empty string scenarios
                    likers_count = format_number(likers_count)
                    # liked by 'username' AND 165 others (166 in total)
                    likers_count += 1
                else:
                    logger.info(
                        "Failed to get likers count on your post {}  "
                        "~empty string".format(count)
                    )
                    likers_count = None
            except NoSuchElementException:
                logger.info("Failed to get likers count on your post {}".format(count))
                likers_count = None
            try:
                likes_button = browser.find_elements_by_xpath(
                    read_xpath(get_active_users.__name__, "likes_button")
                )

                if likes_button != []:
                    if likes_button[1] is not None:
                        likes_button = likes_button[1]
                    else:
                        likes_button = likes_button[0]
                    click_element(browser, likes_button)
                    sleep_actual(3)
                else:
                    raise NoSuchElementException

            except (IndexError, NoSuchElementException):
                # Video have no likes button / no posts in page
                logger.info("video found, try next post until we run out of posts")

                # edge case of account having only videos,  or last post is a video.
                if checked_posts >= total_posts:
                    break
                # if not reached posts(parameter) value, continue (but load next post)
                browser.back()
                # go to next post
                count += 1
                continue

            # get a reference to the 'Likes' dialog box
            dialog = browser.find_element_by_xpath(
                read_xpath("class_selectors", "likes_dialog_body_xpath")
            )

            scroll_it = True
            try_again = 0
            start_time = time.time()
            user_list = []

            if likers_count:
                amount = (
                    likers_count
                    if boundary is None
                    else None
                    if boundary == 0
                    else (boundary if boundary < likers_count else likers_count)
                )
            else:
                amount = None
            tmp_scroll_height = 0
            user_list_len = -1
            while scroll_it is not False and boundary != 0:
                scroll_height = browser.execute_script(
                    """
                    let main = document.getElementsByTagName('main')
                    return main[0].scrollHeight
                    """
                )
                # check if it should keep scrolling down or exit
                if (
                    scroll_height >= tmp_scroll_height
                    and len(user_list) > user_list_len
                ):
                    tmp_scroll_height = scroll_height
                    user_list_len = len(user_list)
                    scroll_it = True
                else:
                    scroll_it = False

                if scroll_it is True:
                    scroll_it = browser.execute_script("window.scrollBy(0, 1000)")
                    update_activity(browser, state=None)

                if sc_rolled > 91 or too_many_requests > 1:  # old value 100
                    print("\n")
                    logger.info("Too Many Requests sent! ~will sleep some :>\n")
                    sleep_actual(600)
                    sc_rolled = 0
                    too_many_requests = (
                        0 if too_many_requests >= 1 else too_many_requests
                    )

                else:
                    sleep_actual(1.2)  # old value 5.6
                    sc_rolled += 1

                user_list = get_users_from_dialog(user_list, dialog)

                # write & update records at Progress Tracker
                if amount:
                    progress_tracker(len(user_list), amount, start_time, None)

                if boundary is not None:
                    if len(user_list) >= boundary:
                        break

                if (
                    scroll_it is False
                    and likers_count
                    and likers_count - 1 > len(user_list)
                ):

                    if (
                        boundary is not None and likers_count - 1 > boundary
                    ) or boundary is None:

                        if try_again <= 1:  # can increase the amount of tries
                            logger.info(
                                "Failed to get the desired amount of "
                                "usernames but trying again.."
                                "\t|> post:{}  |> attempt: {}\n".format(
                                    posts, try_again + 1
                                )
                            )
                            try_again += 1
                            too_many_requests += 1
                            scroll_it = True
                            nap_it = 4 if try_again == 0 else 7
                            sleep_actual(nap_it)

            user_list = get_users_from_dialog(user_list, dialog)

            logger.info(
                "Post {}  |  Likers: found {}, catched {}\n\n".format(
                    count, likers_count, len(user_list)
                )
            )
        except NoSuchElementException as exc:
            logger.error(
                "Ku-ku! There is an error searching active users"
                "~\t{}\n\n".format(str(exc).encode("utf-8"))
            )

        for user in user_list:
            active_users.append(user)

        sleep_actual(1)

        # if not reached posts(parameter) value, continue
        if count != posts + 1:
            try:
                # click close button
                close_dialog_box(browser)
                browser.back()
            except Exception:
                logger.error("Unable to go to next profile post")
        count += 1

    real_time = time.time()
    diff_in_minutes = int((real_time - start_time) / 60)
    diff_in_seconds = int((real_time - start_time) % 60)

    # delete duplicated users
    active_users = list(set(active_users))

    logger.info(
        "Gathered total of {} unique active followers from the latest {} "
        "posts in {} minutes and {} seconds".format(
            len(active_users), posts, diff_in_minutes, diff_in_seconds
        )
    )

    return active_users


def delete_line_from_file(filepath, userToDelete, logger):
    """ Remove user's record from the followed pool file after unfollowing """
    if not os.path.isfile(filepath):
        # in case of there is no any followed pool file yet
        return 0

    try:
        file_path_old = filepath + ".old"
        file_path_Temp = filepath + ".temp"

        with open(filepath, "r") as f:
            lines = f.readlines()

        with open(file_path_Temp, "w") as f:
            for line in lines:
                entries = line.split(" ~ ")
                sz = len(entries)
                if sz == 1:
                    user = entries[0][:-2]
                elif sz == 2:
                    user = entries[1][:-2]
                else:
                    user = entries[1]

                if user == userToDelete:
                    slash_in_filepath = "/" if "/" in filepath else "\\"
                    filename = filepath.split(slash_in_filepath)[-1]
                    logger.info(
                        "\tRemoved '{}' from {} file".format(
                            line.split(",\n")[0], filename
                        )
                    )

                else:
                    f.write(line)

        # File leftovers that should not exist, but if so remove it
        while os.path.isfile(file_path_old):
            try:
                os.remove(file_path_old)

            except OSError as e:
                logger.error("Can't remove file_path_old {}".format(str(e)))
                sleep(5)

        # rename original file to _old
        os.rename(filepath, file_path_old)

        # rename new temp file to filepath
        while os.path.isfile(file_path_Temp):
            try:
                os.rename(file_path_Temp, filepath)

            except OSError as e:
                logger.error(
                    "Can't rename file_path_Temp to filepath {}".format(str(e))
                )
                sleep(5)

        # remove old and temp file
        os.remove(file_path_old)

    except BaseException as e:
        logger.error("delete_line_from_file error {}".format(str(e).encode("utf-8")))


def scroll_bottom(browser, element, range_int):
    # put a limit to the scrolling
    if range_int > 50:
        range_int = 50

    for _ in range(int(range_int / 2)):
        # scroll down the page by 1000 pixels every time
        browser.execute_script("window.scrollBy(0, 1000)")
        # update server calls
        update_activity(browser, state=None)
        sleep(1)

    return


def click_element(browser, element, tryNum=0):
    """
    There are three (maybe more) different ways to "click" an element/button.
    1. element.click()
    2. element.send_keys("\n")
    3. browser.execute_script("document.getElementsByClassName('" +
    element.get_attribute("class") + "')[0].click()")

    I'm guessing all three have their advantages/disadvantages
    Before committing over this code, you MUST justify your change
    and potentially adding an 'if' statement that applies to your
    specific case. See the following issue for more details
    https://github.com/timgrossmann/InstaPy/issues/1232

    explaination of the following recursive function:
      we will attempt to click the element given, if an error is thrown
      we know something is wrong (element not in view, element doesn't
      exist, ...). on each attempt try and move the screen around in
      various ways. if all else fails, programmically click the button
      using `execute_script` in the browser.
      """

    try:
        # use Selenium's built in click function
        element.click()

        # update server calls after a successful click by selenium
        update_activity(browser, state=None)

    except Exception:
        # click attempt failed
        # try something funky and try again

        if tryNum == 0:
            # try scrolling the element into view
            browser.execute_script(
                "document.getElementsByClassName('"
                + element.get_attribute("class")
                + "')[0].scrollIntoView({ inline: 'center' });"
            )

        elif tryNum == 1:
            # well, that didn't work, try scrolling to the top and then
            # clicking again
            browser.execute_script("window.scrollTo(0,0);")

        elif tryNum == 2:
            # that didn't work either, try scrolling to the bottom and then
            # clicking again
            browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")

        else:
            # try `execute_script` as a last resort
            # print("attempting last ditch effort for click, `execute_script`")
            browser.execute_script(
                "document.getElementsByClassName('"
                + element.get_attribute("class")
                + "')[0].click()"
            )
            # update server calls after last click attempt by JS
            update_activity(browser, state=None)
            # end condition for the recursive function
            return

        # update server calls after the scroll(s) in 0, 1 and 2 attempts
        update_activity(browser, state=None)

        # sleep for 1 second to allow window to adjust (may or may not be
        # needed)
        sleep_actual(1)

        tryNum += 1

        # try again!
        click_element(browser, element, tryNum)


def format_number(number):
    """
    Format number. Remove the unused comma. Replace the concatenation with
    relevant zeros. Remove the dot.

    :param number: str

    :return: int
    """
    formatted_num = number.replace(",", "")
    formatted_num = re.sub(
        r"(k)$", "00" if "." in formatted_num else "000", formatted_num
    )
    formatted_num = re.sub(
        r"(m)$", "00000" if "." in formatted_num else "000000", formatted_num
    )
    formatted_num = formatted_num.replace(".", "")
    return int(formatted_num)


def username_url_to_username(username_url):
    a = username_url.replace("https://www.instagram.com/", "")
    username = a.split("/")
    return username[0]


def get_number_of_posts(browser):
    """Get the number of posts from the profile screen"""
    try:
        num_of_posts = getUserData(
            "graphql.user.edge_owner_to_timeline_media.count", browser
        )
    except WebDriverException:
        try:
            num_of_posts_txt = browser.find_element_by_xpath(
                read_xpath(get_number_of_posts.__name__, "num_of_posts_txt")
            ).text

        except NoSuchElementException:
            num_of_posts_txt = browser.find_element_by_xpath(
                read_xpath(
                    get_number_of_posts.__name__, "num_of_posts_txt_no_such_element"
                )
            ).text

        num_of_posts_txt = num_of_posts_txt.replace(" ", "")
        num_of_posts_txt = num_of_posts_txt.replace(",", "")
        num_of_posts = int(num_of_posts_txt)

    return num_of_posts


def get_relationship_counts(browser, username, logger):
    """ Gets the followers & following counts of a given user """

    user_link = "https://www.instagram.com/{}/".format(username)

    # check URL of the webpage, if it already is user's profile page,
    # then do not navigate to it again
    web_address_navigator(browser, user_link)

    try:
        followers_count = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].graphql.user.edge_followed_by.count"
        )

    except WebDriverException:
        try:
            followers_count = format_number(
                browser.find_element_by_xpath(
                    str(read_xpath(get_relationship_counts.__name__, "followers_count"))
                ).text
            )
        except NoSuchElementException:
            try:
                browser.execute_script("location.reload()")
                update_activity(browser, state=None)

                followers_count = browser.execute_script(
                    "return window._sharedData.entry_data."
                    "ProfilePage[0].graphql.user.edge_followed_by.count"
                )

            except WebDriverException:
                try:
                    topCount_elements = browser.find_elements_by_xpath(
                        read_xpath(
                            get_relationship_counts.__name__, "topCount_elements"
                        )
                    )

                    if topCount_elements:
                        followers_count = format_number(topCount_elements[1].text)

                    else:
                        logger.info(
                            "Failed to get followers count of '{}'  ~empty "
                            "list".format(username.encode("utf-8"))
                        )
                        followers_count = None

                except NoSuchElementException:
                    logger.error(
                        "Error occurred during getting the followers count "
                        "of '{}'\n".format(username.encode("utf-8"))
                    )
                    followers_count = None

    try:
        following_count = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].graphql.user.edge_follow.count"
        )

    except WebDriverException:
        try:
            following_count = format_number(
                browser.find_element_by_xpath(
                    str(read_xpath(get_relationship_counts.__name__, "following_count"))
                ).text
            )

        except NoSuchElementException:
            try:
                browser.execute_script("location.reload()")
                update_activity(browser, state=None)

                following_count = browser.execute_script(
                    "return window._sharedData.entry_data."
                    "ProfilePage[0].graphql.user.edge_follow.count"
                )

            except WebDriverException:
                try:
                    topCount_elements = browser.find_elements_by_xpath(
                        read_xpath(
                            get_relationship_counts.__name__, "topCount_elements"
                        )
                    )

                    if topCount_elements:
                        following_count = format_number(topCount_elements[2].text)

                    else:
                        logger.info(
                            "Failed to get following count of '{}'  ~empty "
                            "list".format(username.encode("utf-8"))
                        )
                        following_count = None

                except (NoSuchElementException, IndexError):
                    logger.error(
                        "\nError occurred during getting the following count "
                        "of '{}'\n".format(username.encode("utf-8"))
                    )
                    following_count = None

    Event().profile_data_updated(username, followers_count, following_count)
    return followers_count, following_count


def web_address_navigator(browser, link):
    """Checks and compares current URL of web page and the URL to be
    navigated and if it is different, it does navigate"""
    current_url = get_current_url(browser)
    total_timeouts = 0
    page_type = None  # file or directory

    # remove slashes at the end to compare efficiently
    if current_url is not None and current_url.endswith("/"):
        current_url = current_url[:-1]

    if link.endswith("/"):
        link = link[:-1]
        page_type = "dir"  # slash at the end is a directory

    new_navigation = current_url != link

    if current_url is None or new_navigation:
        link = link + "/" if page_type == "dir" else link  # directory links
        # navigate faster

        while True:
            try:
                browser.get(link)
                # update server calls
                update_activity(browser, state=None)
                sleep(2)
                break

            except TimeoutException as exc:
                if total_timeouts >= 7:
                    raise TimeoutException(
                        "Retried {} times to GET '{}' webpage "
                        "but failed out of a timeout!\n\t{}".format(
                            total_timeouts,
                            str(link).encode("utf-8"),
                            str(exc).encode("utf-8"),
                        )
                    )
                total_timeouts += 1
                sleep(2)


@contextmanager
def interruption_handler(
    threaded=False,
    SIG_type=signal.SIGINT,
    handler=signal.SIG_IGN,
    notify=None,
    logger=None,
):
    """ Handles external interrupt, usually initiated by the user like
    KeyboardInterrupt with CTRL+C """
    if notify is not None and logger is not None:
        logger.warning(notify)

    if not threaded:
        original_handler = signal.signal(SIG_type, handler)

    try:
        yield

    finally:
        if not threaded:
            signal.signal(SIG_type, original_handler)


def highlight_print(
    username=None, message=None, priority=None, level=None, logger=None
):
    """ Print headers in a highlighted style """
    # can add other highlighters at other priorities enriching this function

    # find the number of chars needed off the length of the logger message
    output_len = 28 + len(username) + 3 + len(message) if logger else len(message)
    show_logs = Settings.show_logs

    if priority in ["initialization", "end"]:
        # OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
        # E.g.:          Session started!
        # oooooooooooooooooooooooooooooooooooooooooooooooo
        upper_char = "O"
        lower_char = "o"

    elif priority == "login":
        # ................................................
        # E.g.:        Logged in successfully!
        # ''''''''''''''''''''''''''''''''''''''''''''''''
        upper_char = "."
        lower_char = "'"

    elif priority == "feature":  # feature highlighter
        # ________________________________________________
        # E.g.:    Starting to interact by users..
        # """"""""""""""""""""""""""""""""""""""""""""""""
        upper_char = "_"
        lower_char = '"'

    elif priority == "user iteration":
        # ::::::::::::::::::::::::::::::::::::::::::::::::
        # E.g.:            User: [1/4]
        upper_char = ":"
        lower_char = None

    elif priority == "post iteration":
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # E.g.:            Post: [2/10]
        upper_char = "~"
        lower_char = None

    elif priority == "workspace":
        # ._. ._. ._. ._. ._. ._. ._. ._. ._. ._. ._. ._.
        # E.g.: |> Workspace in use: "C:/Users/El/InstaPy"
        upper_char = " ._. "
        lower_char = None

    if upper_char and (show_logs or priority == "workspace"):
        print("{}".format(upper_char * int(ceil(output_len / len(upper_char)))))

    if level == "info":
        if logger:
            logger.info(message)
        else:
            print(message)

    elif level == "warning":
        if logger:
            logger.warning(message)
        else:
            print(message)

    elif level == "critical":
        if logger:
            logger.critical(message)
        else:
            print(message)

    if lower_char and (show_logs or priority == "workspace"):
        print("{}".format(lower_char * int(ceil(output_len / len(lower_char)))))


def remove_duplicates(container, keep_order, logger):
    """ Remove duplicates from all kinds of data types easily """
    # add support for data types as needed in future
    # currently only 'list' data type is supported
    if isinstance(container, list):
        if keep_order is True:
            result = sorted(set(container), key=container.index)

        else:
            result = set(container)

    else:
        if not logger:
            logger = Settings.logger

        logger.warning(
            "The given data type- '{}' is not supported "
            "in `remove_duplicates` function, yet!".format(type(container))
        )
        result = container

    return result


def dump_record_activity(profile_name, logger, logfolder):
    """ Dump the record activity data to a local human-readable JSON """

    try:
        # get a DB and start a connection
        db, id = get_database()
        conn = sqlite3.connect(db)

        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(
                "SELECT * FROM recordActivity WHERE profile_id=:var", {"var": id}
            )
            user_data = cur.fetchall()

        if user_data:
            ordered_user_data = {}
            current_data = {}

            # get the existing data
            filename = "{}recordActivity.json".format(logfolder)
            if os.path.isfile(filename):
                with open(filename) as recordActFile:
                    current_data = json.load(recordActFile)

            # re-order live user data in the required structure
            for hourly_data in user_data:
                hourly_data = tuple(hourly_data)
                day = hourly_data[-1][:10]
                hour = hourly_data[-1][-8:-6]

                if day not in ordered_user_data.keys():
                    ordered_user_data.update({day: {}})

                ordered_user_data[day].update(
                    {
                        hour: {
                            "likes": hourly_data[1],
                            "comments": hourly_data[2],
                            "follows": hourly_data[3],
                            "unfollows": hourly_data[4],
                            "server_calls": hourly_data[5],
                        }
                    }
                )

            # update user data with live data whilst preserving all other
            # data (keys)
            current_data.update({profile_name: ordered_user_data})

            # dump the fresh record data to a local human readable JSON
            with open(filename, "w") as recordActFile:
                json.dump(current_data, recordActFile)

    except Exception as exc:
        logger.error(
            "Pow! Error occurred while dumping record activity data to a "
            "local JSON:\n\t{}".format(str(exc).encode("utf-8"))
        )

    finally:
        if conn:
            # close the open connection
            conn.close()


def ping_server(host, logger):
    """
    Return True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if
    the host name is valid.
    """
    logger.info("Pinging '{}' to check the connectivity...".format(str(host)))

    # ping command count option as function of OS
    param = "-n" if system().lower() == "windows" else "-c"
    # building the command. Ex: "ping -c 1 google.com"
    command = " ".join(["ping", param, "1", str(host)])
    need_sh = False if system().lower() == "windows" else True

    # pinging
    ping_attempts = 2
    connectivity = None

    while connectivity is not True and ping_attempts > 0:
        connectivity = call(command, shell=need_sh) == 0

        if connectivity is False:
            logger.warning(
                "Pinging the server again!\t~total attempts left: {}".format(
                    ping_attempts
                )
            )
            ping_attempts -= 1
            sleep(5)

    if connectivity is False:
        logger.critical("There is no connection to the '{}' server!".format(host))
        return False

    return True


def emergency_exit(browser, username, logger):
    """ Raise emergency if the is no connection to server OR if user is not
    logged in """
    server_address = "instagram.com"
    connection_state = ping_server(server_address, logger)
    if connection_state is False:
        return True, "not connected"

    # check if the user is logged in
    auth_method = "activity counts"
    login_state = check_authorization(browser, username, auth_method, logger)
    if login_state is False:
        return True, "not logged in"

    return False, "no emergency"


def load_user_id(username, person, logger, logfolder):
    """ Load the user ID at reqeust from local records """
    pool_name = "{0}{1}_followedPool.csv".format(logfolder, username)
    user_id = "undefined"

    try:
        with open(pool_name, "r+") as followedPoolFile:
            reader = csv.reader(followedPoolFile)

            for row in reader:
                entries = row[0].split(" ~ ")
                if len(entries) < 3:
                    # old entry which does not contain an ID
                    pass

                user_name = entries[1]
                if user_name == person:
                    user_id = entries[2]
                    break

        followedPoolFile.close()

    except BaseException as exc:
        logger.exception(
            "Failed to load the user ID of '{}'!\n{}".format(
                person, str(exc).encode("utf-8")
            )
        )

    return user_id


def check_authorization(browser, username, method, logger, notify=True):
    """ Check if user is NOW logged in """
    if notify is True:
        logger.info("Checking if '{}' is logged in...".format(username))

    # different methods can be added in future
    if method == "activity counts":

        # navigate to owner's profile page only if it is on an unusual page
        current_url = get_current_url(browser)
        if (
            not current_url
            or "https://www.instagram.com" not in current_url
            or "https://www.instagram.com/graphql/" in current_url
        ):
            profile_link = "https://www.instagram.com/{}/".format(username)
            web_address_navigator(browser, profile_link)

        # if user is not logged in, `activity_counts` will be `None`- JS `null`
        try:
            activity_counts = browser.execute_script(
                "return window._sharedData.activity_counts"
            )

        except WebDriverException:
            try:
                browser.execute_script("location.reload()")
                update_activity(browser, state=None)

                activity_counts = browser.execute_script(
                    "return window._sharedData.activity_counts"
                )

            except WebDriverException:
                activity_counts = None

        # if user is not logged in, `activity_counts_new` will be `None`- JS
        # `null`
        try:
            activity_counts_new = browser.execute_script(
                "return window._sharedData.config.viewer"
            )

        except WebDriverException:
            try:
                browser.execute_script("location.reload()")
                activity_counts_new = browser.execute_script(
                    "return window._sharedData.config.viewer"
                )

            except WebDriverException:
                activity_counts_new = None

        if activity_counts is None and activity_counts_new is None:
            if notify is True:
                logger.critical("--> '{}' is not logged in!\n".format(username))
            return False

    return True


def get_username(browser, track, logger):
    """ Get the username of a user from the loaded profile page """
    if track == "profile":
        query = "return window._sharedData.entry_data. \
                    ProfilePage[0].graphql.user.username"

    elif track == "post":
        query = "return window._sharedData.entry_data. \
                    PostPage[0].graphql.shortcode_media.owner.username"

    try:
        username = browser.execute_script(query)

    except WebDriverException:
        try:
            browser.execute_script("location.reload()")
            update_activity(browser, state=None)

            username = browser.execute_script(query)

        except WebDriverException:
            current_url = get_current_url(browser)
            logger.info(
                "Failed to get the username from '{}' page".format(
                    current_url or "user" if track == "profile" else "post"
                )
            )
            username = None

    # in future add XPATH ways of getting username

    return username


def find_user_id(browser, track, username, logger):
    """  Find the user ID from the loaded page """
    logger.info(
        "Attempting to find user ID: Track: {}, Username {}".format(track, username)
    )
    if track in ["dialog", "profile"]:
        query = "return window.__additionalData[Object.keys(window.__additionalData)[0]].data.graphql.user.id"

    elif track == "post":
        query = "return window._sharedData.entry_data.ProfilePage[0].graphql.user.id"
        meta_XP = read_xpath(find_user_id.__name__, "meta_XP")

    failure_message = "Failed to get the user ID of '{}' from {} page!".format(
        username, track
    )

    try:
        user_id = browser.execute_script(query)

    except WebDriverException:
        try:
            browser.execute_script("location.reload()")
            update_activity(browser, state=None)

            user_id = browser.execute_script(
                "return window._sharedData."
                "entry_data.ProfilePage[0]."
                "graphql.user.id"
            )

        except WebDriverException:
            if track == "post":
                try:
                    user_id = browser.find_element_by_xpath(meta_XP).get_attribute(
                        "content"
                    )
                    if user_id:
                        user_id = format_number(user_id)

                    else:
                        logger.error("{}\t~empty string".format(failure_message))
                        user_id = None

                except NoSuchElementException:
                    logger.error(failure_message)
                    user_id = None

            else:
                logger.error(failure_message)
                user_id = None

    return user_id


@contextmanager
def new_tab(browser):
    """ USE once a host tab must remain untouched and yet needs extra data-
    get from guest tab """
    try:
        # add a guest tab
        browser.execute_script("window.open()")
        sleep(1)
        # switch to the guest tab
        browser.switch_to.window(browser.window_handles[1])
        sleep(2)
        yield

    finally:
        # close the guest tab
        browser.execute_script("window.close()")
        sleep(1)
        # return to the host tab
        browser.switch_to.window(browser.window_handles[0])
        sleep(2)


def explicit_wait(browser, track, ec_params, logger, timeout=35, notify=True):
    """
    Explicitly wait until expected condition validates

    :param browser: webdriver instance
    :param track: short name of the expected condition
    :param ec_params: expected condition specific parameters - [param1, param2]
    :param logger: the logger instance
    """
    # list of available tracks:
    # <https://seleniumhq.github.io/selenium/docs/api/py/webdriver_support/
    # selenium.webdriver.support.expected_conditions.html>

    if not isinstance(ec_params, list):
        ec_params = [ec_params]

    # find condition according to the tracks
    if track == "VOEL":
        elem_address, find_method = ec_params
        ec_name = "visibility of element located"

        find_by = (
            By.XPATH
            if find_method == "XPath"
            else By.CSS_SELECTOR
            if find_method == "CSS"
            else By.CLASS_NAME
        )
        locator = (find_by, elem_address)
        condition = ec.visibility_of_element_located(locator)

    elif track == "TC":
        expect_in_title = ec_params[0]
        ec_name = "title contains '{}' string".format(expect_in_title)

        condition = ec.title_contains(expect_in_title)

    elif track == "PFL":
        ec_name = "page fully loaded"
        condition = lambda browser: browser.execute_script(
            "return document.readyState"
        ) in ["complete" or "loaded"]

    elif track == "SO":
        ec_name = "staleness of"
        element = ec_params[0]

        condition = ec.staleness_of(element)

    # generic wait block
    try:
        wait = WebDriverWait(browser, timeout)
        result = wait.until(condition)

    except TimeoutException:
        if notify is True:
            logger.info(
                "Timed out with failure while explicitly waiting until {}!\n".format(
                    ec_name
                )
            )
        return False

    return result


def get_current_url(browser):
    """ Get URL of the loaded webpage """
    try:
        current_url = browser.execute_script("return window.location.href")

    except WebDriverException:
        try:
            current_url = browser.current_url

        except WebDriverException:
            current_url = None

    return current_url


def get_username_from_id(browser, user_id, logger):
    """ Convert user ID to username """
    # method using graphql 'Account media' endpoint
    logger.info("Trying to find the username from the given user ID by loading a post")

    query_hash = "42323d64886122307be10013ad2dcc44"  # earlier-
    # "472f257a40c653c64c666ce877d59d2b"
    graphql_query_URL = (
        "https://www.instagram.com/graphql/query/?query_hash" "={}".format(query_hash)
    )
    variables = {"id": str(user_id), "first": 1}
    post_url = "{}&variables={}".format(graphql_query_URL, str(json.dumps(variables)))

    web_address_navigator(browser, post_url)
    try:
        pre = browser.find_element_by_tag_name("pre").text
    except NoSuchElementException:
        logger.info("Encountered an error to find `pre` in page, skipping username.")
        return None
    user_data = json.loads(pre)["data"]["user"]

    if user_data:
        user_data = user_data["edge_owner_to_timeline_media"]

        if user_data["edges"]:
            post_code = user_data["edges"][0]["node"]["shortcode"]
            post_page = "https://www.instagram.com/p/{}".format(post_code)

            web_address_navigator(browser, post_page)
            username = get_username(browser, "post", logger)
            if username:
                return username

        else:
            if user_data["count"] == 0:
                logger.info("Profile with ID {}: no pics found".format(user_id))

            else:
                logger.info(
                    "Can't load pics of a private profile to find username ("
                    "ID: {})".format(user_id)
                )

    else:
        logger.info(
            "No profile found, the user may have blocked you (ID: {})".format(user_id)
        )
        return None

    """  method using private API
    #logger.info("Trying to find the username from the given user ID by a
    quick API call")

    #req = requests.get(u"https://i.instagram.com/api/v1/users/{}/info/"
    #                   .format(user_id))
    #if req:
    #    data = json.loads(req.text)
    #    if data["user"]:
    #        username = data["user"]["username"]
    #        return username
    """

    """ Having a BUG (random log-outs) with the method below, use it only in
    the external sessions
    # method using graphql 'Follow' endpoint
    logger.info("Trying to find the username from the given user ID "
                "by using the GraphQL Follow endpoint")

    user_link_by_id = ("https://www.instagram.com/web/friendships/{}/follow/"
                       .format(user_id))

    web_address_navigator(browser, user_link_by_id)
    username = get_username(browser, "profile", logger)
    """

    return None


def is_page_available(browser, logger):
    """ Check if the page is available and valid """
    expected_keywords = ["Page Not Found", "Content Unavailable"]
    page_title = get_page_title(browser, logger)

    if any(keyword in page_title for keyword in expected_keywords):
        reload_webpage(browser)
        page_title = get_page_title(browser, logger)

        if any(keyword in page_title for keyword in expected_keywords):
            if "Page Not Found" in page_title:
                logger.warning(
                    "The page isn't available!\t~the link may be broken, "
                    "or the page may have been removed..."
                )

            elif "Content Unavailable" in page_title:
                logger.warning(
                    "The page isn't available!\t~the user may have blocked " "you..."
                )

            return False

    return True


@contextmanager
def smart_run(session, threaded=False):
    try:
        session.login()
        yield
    except NoSuchElementException:
        # The problem is with a change in IG page layout
        log_file = "{}.html".format(time.strftime("%Y%m%d-%H%M%S"))
        file_path = os.path.join(gettempdir(), log_file)

        with open(file_path, "wb") as fp:
            fp.write(session.browser.page_source.encode("utf-8"))

        print(
            "{0}\nIf raising an issue, "
            "please also upload the file located at:\n{1}\n{0}".format(
                "*" * 70, file_path
            )
        )
    except KeyboardInterrupt:
        clean_exit("You have exited successfully.")
    finally:
        session.end(threaded_session=threaded)


def reload_webpage(browser):
    """ Reload the current webpage """
    browser.execute_script("location.reload()")
    update_activity(browser, state=None)
    sleep(2)

    return True


def get_page_title(browser, logger):
    """ Get the title of the webpage """
    # wait for the current page fully load to get the correct page's title
    explicit_wait(browser, "PFL", [], logger, 10)

    try:
        page_title = browser.title

    except WebDriverException:
        try:
            page_title = browser.execute_script("return document.title")

        except WebDriverException:
            try:
                page_title = browser.execute_script(
                    "return document.getElementsByTagName('title')[0].text"
                )

            except WebDriverException:
                logger.info("Unable to find the title of the page :(")
                return None

    return page_title


def click_visibly(browser, element):
    """ Click as the element become visible """
    if element.is_displayed():
        click_element(browser, element)

    else:
        browser.execute_script(
            "arguments[0].style.visibility = 'visible'; "
            "arguments[0].style.height = '10px'; "
            "arguments[0].style.width = '10px'; "
            "arguments[0].style.opacity = 1",
            element,
        )
        # update server calls
        update_activity(browser, state=None)

        click_element(browser, element)

    return True


def get_action_delay(action):
    """ Get the delay time to sleep after doing actions """
    defaults = {"like": 2, "comment": 2, "follow": 3, "unfollow": 10, "story": 3}
    config = Settings.action_delays

    if (
        not config
        or action not in config
        or config["enabled"] is not True
        or config[action] is None
        or isinstance(config[action], (int, float)) is not True
    ):
        return defaults[action]

    else:
        custom_delay = config[action]

    # randomize the custom delay in user-defined range
    if (
        config["randomize"] is True
        and isinstance(config["random_range"], tuple)
        and len(config["random_range"]) == 2
        and all(
            (isinstance(i, (type(None), int, float)) for i in config["random_range"])
        )
        and any(not isinstance(i, type(None)) for i in config["random_range"])
    ):
        min_range = config["random_range"][0]
        max_range = config["random_range"][1]

        if not min_range or min_range < 0:
            min_range = 100

        if not max_range or max_range < 0:
            max_range = 100

        if min_range > max_range:
            a = min_range
            min_range = max_range
            max_range = a

        custom_delay = random.uniform(
            custom_delay * min_range / 100, custom_delay * max_range / 100
        )

    if custom_delay < defaults[action] and config["safety_match"] is not False:
        return defaults[action]

    return custom_delay


def deform_emojis(text):
    """ Convert unicode emojis into their text form """
    new_text = ""
    emojiless_text = ""
    data = regex.findall(r"\X", text)
    emojis_in_text = []

    for word in data:
        if any(char in UNICODE_EMOJI for char in word):
            word_emoji = emoji.demojize(word).replace(":", "").replace("_", " ")
            if word_emoji not in emojis_in_text:  # do not add an emoji if
                # already exists in text
                emojiless_text += " "
                new_text += " ({}) ".format(word_emoji)
                emojis_in_text.append(word_emoji)
            else:
                emojiless_text += " "
                new_text += " "  # add a space [instead of an emoji to be
                # duplicated]

        else:
            new_text += word
            emojiless_text += word

    emojiless_text = remove_extra_spaces(emojiless_text)
    new_text = remove_extra_spaces(new_text)

    return new_text, emojiless_text


def extract_text_from_element(elem):
    """ As an element is valid and contains text, extract it and return """
    if elem and hasattr(elem, "text") and elem.text:
        text = elem.text
    else:
        text = None

    return text


def truncate_float(number, precision, round=False):
    """ Truncate (shorten) a floating point value at given precision """

    # don't allow a negative precision [by mistake?]
    precision = abs(precision)

    if round:
        # python 2.7+ supported method [recommended]
        short_float = round(number, precision)

        # python 2.6+ supported method
        """short_float = float("{0:.{1}f}".format(number, precision))
        """

    else:
        operate_on = 1  # returns the absolute number (e.g. 11.0 from 11.456)

        for _ in range(precision):
            operate_on *= 10

        short_float = float(int(number * operate_on)) / operate_on

    return short_float


def get_time_until_next_month():
    """ Get total seconds remaining until the next month """
    now = datetime.datetime.now()
    next_month = now.month + 1 if now.month < 12 else 1
    year = now.year if now.month < 12 else now.year + 1
    date_of_next_month = datetime.datetime(year, next_month, 1)

    remaining_seconds = (date_of_next_month - now).total_seconds()

    return remaining_seconds


def remove_extra_spaces(text):
    """ Find and remove redundant spaces more than 1 in text """
    new_text = re.sub(r" {2,}", " ", text)

    return new_text


def has_any_letters(text):
    """ Check if the text has any letters in it """
    # result = re.search("[A-Za-z]", text)   # works only with english letters
    result = any(
        c.isalpha() for c in text
    )  # works with any letters - english or non-english

    return result


def save_account_progress(browser, username, logger):
    """
    Check account current progress and update database

    Args:
        :browser: web driver
        :username: Account to be updated
        :logger: library to log actions
    """
    logger.info("Saving account progress...")
    followers, following = get_relationship_counts(browser, username, logger)

    # save profile total posts
    posts = getUserData("graphql.user.edge_owner_to_timeline_media.count", browser)

    try:
        # DB instance
        db, id = get_database()
        conn = sqlite3.connect(db)
        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            sql = (
                "INSERT INTO accountsProgress (profile_id, followers, "
                "following, total_posts, created, modified) "
                "VALUES (?, ?, ?, ?, strftime('%Y-%m-%d %H:%M:%S'), "
                "strftime('%Y-%m-%d %H:%M:%S'))"
            )
            cur.execute(sql, (id, followers, following, posts))
            conn.commit()
    except Exception:
        logger.exception("message")


def get_epoch_time_diff(time_stamp, logger):
    try:
        # time diff in seconds from input to now
        log_time = datetime.datetime.strptime(time_stamp, "%Y-%m-%d %H:%M")

        former_epoch = (log_time - datetime.datetime(1970, 1, 1)).total_seconds()
        cur_epoch = (
            datetime.datetime.now() - datetime.datetime(1970, 1, 1)
        ).total_seconds()

        return cur_epoch - former_epoch
    except ValueError:
        logger.error("Error occurred while reading timestamp value from database")
        return None


def is_follow_me(browser, person=None):
    # navigate to profile page if not already in it
    if person:
        user_link = "https://www.instagram.com/{}/".format(person)
        web_address_navigator(browser, user_link)

    return getUserData("graphql.user.follows_viewer", browser)


def get_users_from_dialog(old_data, dialog):
    """
    Prepared to work specially with the dynamic data load in the 'Likes'
    dialog box
    """

    user_blocks = dialog.find_elements_by_tag_name("a")
    loaded_users = [
        extract_text_from_element(u)
        for u in user_blocks
        if extract_text_from_element(u)
    ]
    new_data = old_data + loaded_users
    new_data = remove_duplicates(new_data, True, None)

    return new_data


def progress_tracker(current_value, highest_value, initial_time, logger):
    """ Provide a progress tracker to keep value updated until finishes """
    if current_value is None or highest_value is None or highest_value == 0:
        return

    try:
        real_time = time.time()
        progress_percent = int((current_value / highest_value) * 100)
        show_logs = Settings.show_logs

        elapsed_time = real_time - initial_time
        elapsed_formatted = truncate_float(elapsed_time, 2)
        elapsed = (
            "{} seconds".format(elapsed_formatted)
            if elapsed_formatted < 60
            else "{} minutes".format(truncate_float(elapsed_formatted / 60, 2))
        )

        eta_time = abs(
            (elapsed_time * 100) / (progress_percent if progress_percent != 0 else 1)
            - elapsed_time
        )
        eta_formatted = truncate_float(eta_time, 2)
        eta = (
            "{} seconds".format(eta_formatted)
            if eta_formatted < 60
            else "{} minutes".format(truncate_float(eta_formatted / 60, 2))
        )

        tracker_line = "-----------------------------------"
        filled_index = int(progress_percent / 2.77)
        progress_container = (
            "[" + tracker_line[:filled_index] + "+" + tracker_line[filled_index:] + "]"
        )
        progress_container = (
            progress_container[: filled_index + 1].replace("-", "=")
            + progress_container[filled_index + 1 :]
        )

        total_message = (
            "\r  {}/{} {}  {}%    "
            "|> Elapsed: {}    "
            "|> ETA: {}      ".format(
                current_value,
                highest_value,
                progress_container,
                progress_percent,
                elapsed,
                eta,
            )
        )

        if show_logs is True:
            sys.stdout.write(total_message)
            sys.stdout.flush()

    except Exception as exc:
        if not logger:
            logger = Settings.logger

        logger.info(
            "Error occurred with Progress Tracker:\n{}".format(str(exc).encode("utf-8"))
        )


def close_dialog_box(browser):
    """ Click on the close button spec. in the 'Likes' dialog box """

    try:
        close = browser.find_element_by_xpath(
            read_xpath("class_selectors", "likes_dialog_close_xpath")
        )

        click_element(browser, close)

    except NoSuchElementException:
        pass


def parse_cli_args():
    """ Parse arguments passed by command line interface """

    AP_kwargs = dict(
        prog="InstaPy",
        description="Parse InstaPy constructor's arguments",
        epilog="And that's how you'd pass arguments by CLI..",
        conflict_handler="resolve",
    )
    if python_version() < "3.5":
        parser = CustomizedArgumentParser(**AP_kwargs)
    else:
        AP_kwargs.update(allow_abbrev=False)
        parser = ArgumentParser(**AP_kwargs)

    """ Flags that REQUIRE a value once added
    ```python quickstart.py --username abc```
    """
    parser.add_argument("-u", "--username", help="Username", type=str, metavar="abc")
    parser.add_argument("-p", "--password", help="Password", type=str, metavar="123")
    parser.add_argument(
        "-pd", "--page-delay", help="Implicit wait", type=int, metavar=25
    )
    parser.add_argument(
        "-pa", "--proxy-address", help="Proxy address", type=str, metavar="192.168.1.1"
    )
    parser.add_argument(
        "-pp", "--proxy-port", help="Proxy port", type=int, metavar=8080
    )

    """ Auto-booleans: adding these flags ENABLE themselves automatically
    ```python quickstart.py --use-firefox```
    """
    parser.add_argument(
        "-uf", "--use-firefox", help="Use Firefox", action="store_true", default=None
    )
    parser.add_argument(
        "-hb",
        "--headless-browser",
        help="Headless browser",
        action="store_true",
        default=None,
    )
    parser.add_argument(
        "-dil",
        "--disable-image-load",
        help="Disable image load",
        action="store_true",
        default=None,
    )
    parser.add_argument(
        "-bsa",
        "--bypass-suspicious-attempt",
        help="Bypass suspicious attempt",
        action="store_true",
        default=None,
    )
    parser.add_argument(
        "-bwm",
        "--bypass-with-mobile",
        help="Bypass with mobile phone",
        action="store_true",
        default=None,
    )
    parser.add_argument(
        "-sdb",
        "--split-db",
        help="Split sqlite-db as instapy_{username}.db",
        action="store_true",
        default=None,
    )
    parser.add_argument(
        "-wcb",
        "--want_check_browser",
        help="Check connectivity before connecting to Instagram",
        default=None,
    )

    """ Style below can convert strings into booleans:
    ```parser.add_argument("--is-debug",
                           default=False,
                           type=lambda x: (str(x).capitalize() == "True"))```

    So that, you can pass bool values explicitly from CLI,
    ```python quickstart.py --is-debug True```

    NOTE: This style is the easiest of it and currently not being used.
    """

    args, _ = parser.parse_known_args()
    # Once added custom arguments if you use a reserved name of core flags
    # and don't parse it, e.g.,
    # `-ufa` will misbehave cos it has `-uf` reserved flag in it.
    # But if you parse it, it's okay.

    return args


def get_cord_location(browser, location):
    base_url = "https://www.instagram.com/explore/locations/"
    query_url = "{}{}{}".format(base_url, location, "?__a=1")
    browser.get(query_url)
    json_text = browser.find_element_by_xpath(
        read_xpath(get_cord_location.__name__, "json_text")
    ).text
    data = json.loads(json_text)

    lat = data["graphql"]["location"]["lat"]
    lon = data["graphql"]["location"]["lng"]

    return lat, lon


def get_bounding_box(
    latitude_in_degrees, longitude_in_degrees, half_side_in_miles, logger
):
    if half_side_in_miles == 0:
        logger.error("Check your Radius its lower then 0")
        return {}
    if latitude_in_degrees < -90.0 or latitude_in_degrees > 90.0:
        logger.error("Check your latitude should be between -90/90")
        return {}
    if longitude_in_degrees < -180.0 or longitude_in_degrees > 180.0:
        logger.error("Check your longtitude should be between -180/180")
        return {}
    half_side_in_km = half_side_in_miles * 1.609344
    lat = radians(latitude_in_degrees)
    lon = radians(longitude_in_degrees)

    radius = 6371
    # Radius of the parallel at given latitude
    parallel_radius = radius * cos(lat)

    lat_min = lat - half_side_in_km / radius
    lat_max = lat + half_side_in_km / radius
    lon_min = lon - half_side_in_km / parallel_radius
    lon_max = lon + half_side_in_km / parallel_radius

    lat_min = rad2deg(lat_min)
    lon_min = rad2deg(lon_min)
    lat_max = rad2deg(lat_max)
    lon_max = rad2deg(lon_max)

    bbox = {
        "lat_min": lat_min,
        "lat_max": lat_max,
        "lon_min": lon_min,
        "lon_max": lon_max,
    }

    return bbox


def take_rotative_screenshot(browser, logfolder):
    """
        Make a sequence of screenshots, based on hour:min:secs
    """
    global next_screenshot

    if next_screenshot == 1:
        browser.save_screenshot("{}screenshot_1.png".format(logfolder))
    elif next_screenshot == 2:
        browser.save_screenshot("{}screenshot_2.png".format(logfolder))
    else:
        browser.save_screenshot("{}screenshot_3.png".format(logfolder))
        next_screenshot = 0
        # sum +1 next

    # update next
    next_screenshot += 1


def get_query_hash(browser, logger):
    """ Load Instagram JS file and find query hash code """
    link = "https://www.instagram.com/static/bundles/es6/Consumer.js/1f67555edbd3.js"
    web_address_navigator(browser, link)
    page_source = browser.page_source
    # locate pattern value from JS file
    # sequence of 32 words and/or numbers just before ,n=" value
    hash = re.findall('[a-z0-9]{32}(?=",n=")', page_source)
    if hash:
        return hash[0]
    else:
        logger.warn("Query Hash not found")


def file_handling(file):
    """ Extracts text file's elements """
    elements = []
    try:
        with open(file, "r") as f:
            # extract file's lines in list
            for line in f.readlines():
                if line != "\n":
                    # remove leading whitespaces, newline and tab characters
                    element = line.lstrip().strip("\n")
                    elements.append(element)
    except FileNotFoundError:
        return ["FileNotFoundError"]

    return elements


class CustomizedArgumentParser(ArgumentParser):
    """
     Subclass ArgumentParser in order to turn off
    the abbreviation matching on older pythons.

    `allow_abbrev` parameter was added by Python 3.5 to do it.
    Thanks to @paul.j3 - https://bugs.python.org/msg204678 for this solution.
    """

    def _get_option_tuples(self, option_string):
        """
         Default of this method searches through all possible prefixes
        of the option string and all actions in the parser for possible
        interpretations.

        To view the original source of this method, running,
        ```
        import inspect; import argparse; inspect.getsourcefile(argparse)
        ```
        will give the location of the 'argparse.py' file that have this method.
        """
        return []
