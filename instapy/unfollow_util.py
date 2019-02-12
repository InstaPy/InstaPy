""" Module which handles the follow features like unfollowing and following """
import time
from datetime import datetime
import os
import random
import json
import csv
import sqlite3
from math import ceil

from .time_util import sleep
from .util import delete_line_from_file
from .util import scroll_bottom
from .util import format_number
from .util import update_activity
from .util import add_user_to_blacklist
from .util import click_element
from .util import web_address_navigator
from .util import get_relationship_counts
from .util import emergency_exit
from .util import load_user_id
from .util import find_user_id
from .util import explicit_wait
from .util import get_username_from_id
from .util import is_page_available
from .util import reload_webpage
from .util import click_visibly
from .util import get_action_delay
from .util import truncate_float
from .util import progress_tracker
from .print_log_writer import log_followed_pool
from .print_log_writer import log_uncertain_unfollowed_pool
from .print_log_writer import log_record_all_unfollowed
from .print_log_writer import get_log_time
from .relationship_tools import get_followers
from .relationship_tools import get_nonfollowers
from .database_engine import get_database
from .quota_supervisor import quota_supervisor

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException


def set_automated_followed_pool(username, unfollow_after, logger, logfolder):
    """ Generare a user list based on the InstaPy followed usernames """
    pool_name = "{0}{1}_followedPool.csv".format(logfolder, username)
    automatedFollowedPool = {"all": {}, "eligible": {}}
    time_stamp = None
    user_id = "undefined"  # 'undefined' rather than None is *intentional

    try:
        with open(pool_name, 'r+') as followedPoolFile:
            reader = csv.reader(followedPoolFile)

            for row in reader:
                entries = row[0].split(' ~ ')
                sz = len(entries)
                """
                Data entry styles [historically]:
                    user,   # oldest
                    datetime ~ user,   # after `unfollow_after` was introduced
                    datetime ~ user ~ user_id,   # after `user_id` was added
                """
                if sz == 1:
                    time_stamp = None
                    user = entries[0]

                elif sz == 2:
                    time_stamp = entries[0]
                    user = entries[1]

                elif sz == 3:
                    time_stamp = entries[0]
                    user = entries[1]
                    user_id = entries[2]

                automatedFollowedPool["all"].update({user: {"id": user_id}})
                # get eligible list
                if unfollow_after is not None and time_stamp:
                    try:
                        log_time = datetime.strptime(time_stamp,
                                                     '%Y-%m-%d %H:%M')
                    except ValueError:
                        continue

                    former_epoch = (log_time - datetime(1970, 1,
                                                        1)).total_seconds()
                    cur_epoch = (datetime.now() - datetime(1970, 1,
                                                           1)).total_seconds()

                    if cur_epoch - former_epoch > unfollow_after:
                        automatedFollowedPool["eligible"].update(
                            {user: {"id": user_id}})

                else:
                    automatedFollowedPool["eligible"].update(
                        {user: {"id": user_id}})

        followedPoolFile.close()

    except BaseException as exc:
        logger.error(
            "Error occurred while generating a user list from the followed "
            "pool!\n\t{}".format(str(exc).encode("utf-8")))

    return automatedFollowedPool


def get_following_status(browser, track, username, person, person_id, logger,
                         logfolder):
    """ Verify if you are following the user in the loaded page """

    if person == username:
        return "OWNER", None

    if track == "profile":
        ig_homepage = "https://www.instagram.com/"
        web_address_navigator(browser, ig_homepage + person)

    follow_button_XP = ("//button[text()='Following' or \
                                  text()='Requested' or \
                                  text()='Follow' or \
                                  text()='Follow Back' or \
                                  text()='Unblock']"
                        )
    failure_msg = "--> Unable to detect the following status of '{}'!"
    user_inaccessible_msg = (
        "Couldn't access the profile page of '{}'!\t~might have changed the"
        " username".format(person))

    # check if the page is available
    valid_page = is_page_available(browser, logger)
    if not valid_page:
        logger.warning(user_inaccessible_msg)
        person_new = verify_username_by_id(browser,
                                           username,
                                           person,
                                           None,
                                           logger,
                                           logfolder)
        if person_new:
            web_address_navigator(browser, ig_homepage + person_new)
            valid_page = is_page_available(browser, logger)
            if not valid_page:
                logger.error(failure_msg.format(person_new.encode("utf-8")))
                return "UNAVAILABLE", None

        else:
            logger.error(failure_msg.format(person.encode("utf-8")))
            return "UNAVAILABLE", None

    # wait until the follow button is located and visible, then get it
    follow_button = explicit_wait(browser, "VOEL", [follow_button_XP, "XPath"],
                                  logger, 7, False)
    if not follow_button:
        browser.execute_script("location.reload()")
        update_activity()

        follow_button = explicit_wait(browser, "VOEL",
                                      [follow_button_XP, "XPath"], logger, 14,
                                      False)
        if not follow_button:
            # cannot find the any of the expected buttons
            logger.error(failure_msg.format(person.encode("utf-8")))
            return None, None

    # get follow status
    following_status = follow_button.text

    return following_status, follow_button


def unfollow(browser,
             username,
             amount,
             customList,
             InstapyFollowed,
             nonFollowers,
             allFollowing,
             style,
             automatedFollowedPool,
             relationship_data,
             dont_include,
             white_list,
             sleep_delay,
             jumps,
             logger,
             logfolder):
    """ Unfollows the given amount of users"""

    if (customList is not None and
            type(customList) in [tuple, list] and
            len(customList) == 3 and
            customList[0] is True and
            type(customList[1]) in [list, tuple, set] and
            len(customList[1]) > 0 and
            customList[2] in ["all", "nonfollowers"]):
        customList_data = customList[1]
        if type(customList_data) != list:
            customList_data = list(customList_data)
        unfollow_track = customList[2]
        customList = True
    else:
        customList = False

    if (InstapyFollowed is not None and
            type(InstapyFollowed) in [tuple, list] and
            len(InstapyFollowed) == 2 and
            InstapyFollowed[0] is True and
            InstapyFollowed[1] in ["all", "nonfollowers"]):
        unfollow_track = InstapyFollowed[1]
        InstapyFollowed = True
    else:
        InstapyFollowed = False

    unfollowNum = 0

    user_link = "https://www.instagram.com/{}/".format(username)

    # check URL of the webpage, if it already is the one to be navigated
    # then do not navigate to it again
    web_address_navigator(browser, user_link)

    # check how many poeple we are following
    allfollowers, allfollowing = get_relationship_counts(browser, username,
                                                         logger)

    if allfollowing is None:
        logger.warning(
            "Unable to find the count of users followed  ~leaving unfollow "
            "feature")
        return 0
    elif allfollowing == 0:
        logger.warning(
            "There are 0 people to unfollow  ~leaving unfollow feature")
        return 0

    if amount > allfollowing:
        logger.info(
            "There are less users to unfollow than you have requested:  "
            "{}/{}  ~using available amount\n".format(allfollowing, amount))
        amount = allfollowing

    if (customList is True or
            InstapyFollowed is True or
            nonFollowers is True):

        if customList is True:
            logger.info("Unfollowing from the list of pre-defined usernames\n")
            unfollow_list = customList_data

        elif InstapyFollowed is True:
            logger.info("Unfollowing the users followed by InstaPy\n")
            unfollow_list = list(automatedFollowedPool["eligible"].keys())

        elif nonFollowers is True:
            logger.info("Unfollowing the users who do not follow back\n")
            """  Unfollow only the users who do not follow you back """
            unfollow_list = get_nonfollowers(browser,
                                             username,
                                             relationship_data,
                                             False,
                                             True,
                                             logger,
                                             logfolder)

        # pick only the users in the right track- ["all" or "nonfollowers"]
        # for `customList` and
        #  `InstapyFollowed` unfollow methods
        if customList is True or InstapyFollowed is True:
            if unfollow_track == "nonfollowers":
                all_followers = get_followers(browser,
                                              username,
                                              "full",
                                              relationship_data,
                                              False,
                                              True,
                                              logger,
                                              logfolder)
                loyal_users = [user for user in unfollow_list if
                               user in all_followers]
                logger.info(
                    "Found {} loyal followers!  ~will not unfollow "
                    "them".format(
                        len(loyal_users)))
                unfollow_list = [user for user in unfollow_list if
                                 user not in loyal_users]

            elif unfollow_track != "all":
                logger.info(
                    "Unfollow track is not specified! ~choose \"all\" or "
                    "\"nonfollowers\"")
                return 0

        # re-generate unfollow list according to the `unfollow_after`
        # parameter for `customList` and
        #  `nonFollowers` unfollow methods
        if customList is True or nonFollowers is True:
            not_found = []
            non_eligible = []
            for person in unfollow_list:
                if person not in automatedFollowedPool["all"].keys():
                    not_found.append(person)
                elif (person in automatedFollowedPool["all"].keys() and
                      person not in automatedFollowedPool["eligible"].keys()):
                    non_eligible.append(person)

            unfollow_list = [user for user in unfollow_list if
                             user not in non_eligible]
            logger.info("Total {} users available to unfollow"
                        "  ~not found in 'followedPool.csv': {}  |  didn't "
                        "pass `unfollow_after`: {}\n".format(
                len(unfollow_list), len(not_found), len(non_eligible)))

        elif InstapyFollowed is True:
            non_eligible = [user for user in
                            automatedFollowedPool["all"].keys() if
                            user not in automatedFollowedPool[
                                "eligible"].keys()]
            logger.info(
                "Total {} users available to unfollow  ~didn't pass "
                "`unfollow_after`: {}\n"
                    .format(len(unfollow_list), len(non_eligible)))

        if len(unfollow_list) < 1:
            logger.info("There are no any users available to unfollow")
            return 0

        # choose the desired order of the elements
        if style == "LIFO":
            unfollow_list = list(reversed(unfollow_list))
        elif style == "RANDOM":
            random.shuffle(unfollow_list)

        if amount > len(unfollow_list):
            logger.info(
                "You have requested more amount: {} than {} of users "
                "available to unfollow"
                "~using available amount\n".format(amount, len(unfollow_list)))
            amount = len(unfollow_list)

        # unfollow loop
        try:
            sleep_counter = 0
            sleep_after = random.randint(8, 12)
            index = 0

            for person in unfollow_list:
                if unfollowNum >= amount:
                    logger.warning(
                        "--> Total unfollows reached it's amount given {}\n"
                            .format(unfollowNum))
                    break

                if jumps["consequent"]["unfollows"] >= jumps["limit"][
                    "unfollows"]:
                    logger.warning(
                        "--> Unfollow quotient reached its peak!\t~leaving "
                        "Unfollow-Users activity\n")
                    break

                if sleep_counter >= sleep_after and sleep_delay not in [0,
                                                                        None]:
                    delay_random = random.randint(ceil(sleep_delay * 0.85),
                                                  ceil(sleep_delay * 1.14))
                    logger.info(
                        "Unfollowed {} new users  ~sleeping about {}\n".format(
                            sleep_counter,
                            '{} seconds'.format(
                                delay_random) if delay_random < 60 else
                            '{} minutes'.format(
                                truncate_float(
                                    delay_random / 60, 2))))
                    sleep(delay_random)
                    sleep_counter = 0
                    sleep_after = random.randint(8, 12)
                    pass

                if person not in dont_include:
                    logger.info(
                        "Ongoing Unfollow [{}/{}]: now unfollowing '{}'..."
                            .format(unfollowNum + 1,
                                    amount,
                                    person.encode('utf-8')))

                    person_id = (automatedFollowedPool["all"][person]["id"] if
                                 person in automatedFollowedPool[
                                     "all"].keys() else False)

                    try:
                        unfollow_state, msg = unfollow_user(browser,
                                                            "profile",
                                                            username,
                                                            person,
                                                            person_id,
                                                            None,
                                                            relationship_data,
                                                            logger,
                                                            logfolder)
                    except BaseException as e:
                        logger.error(
                            "Unfollow loop error:  {}\n".format(str(e)))

                    post_unfollow_actions(browser, person, logger)

                    if unfollow_state is True:
                        unfollowNum += 1
                        sleep_counter += 1
                        # reset jump counter after a successful unfollow
                        jumps["consequent"]["unfollows"] = 0

                    elif msg == "jumped":
                        # will break the loop after certain consecutive jumps
                        jumps["consequent"]["unfollows"] += 1

                    elif msg in ["temporary block", "not connected",
                                 "not logged in"]:
                        # break the loop in extreme conditions to prevent
                        # misbehaviours
                        logger.warning(
                            "There is a serious issue: '{}'!\t~leaving "
                            "Unfollow-Users activity".format(
                                msg))
                        break

                else:
                    # if the user in dont include (should not be) we shall
                    # remove him from the follow list
                    # if he is a white list user (set at init and not during
                    # run time)
                    if person in white_list:
                        delete_line_from_file(
                            '{0}{1}_followedPool.csv'.format(logfolder,
                                                             username),
                            person, logger)
                        list_type = 'whitelist'
                    else:
                        list_type = 'dont_include'
                    logger.info(
                        "Not unfollowed '{}'!\t~user is in the list {}"
                        "\n".format(
                            person, list_type))
                    index += 1
                    continue
        except BaseException as e:
            logger.error("Unfollow loop error:  {}\n".format(str(e)))
    elif allFollowing is True:
        logger.info("Unfollowing the users you are following")
        # unfollow from profile
        try:
            following_link = browser.find_elements_by_xpath(
                '//section//ul//li[3]')

            click_element(browser, following_link[0])
            # update server calls
            update_activity()
        except BaseException as e:
            logger.error("following_link error {}".format(str(e)))
            return 0

        # scroll down the page to get sufficient amount of usernames
        get_users_through_dialog(browser, None, username, amount,
                                 allfollowing, False, None, None,
                                 None, {"enabled": False, "percentage": 0},
                                 "Unfollow", jumps, logger, logfolder)

        # find dialog box
        dialog = browser.find_element_by_xpath(
            "//div[text()='Following']/../../../following-sibling::div")

        sleep(3)

        # get persons, unfollow buttons, and length of followed pool
        person_list_a = dialog.find_elements_by_tag_name("a")
        person_list = []

        for person in person_list_a:

            if person and hasattr(person, 'text') and person.text:
                person_list.append(person.text)

        follow_buttons = dialog.find_elements_by_tag_name('button')

        # re-generate person list to unfollow according to the
        # `unfollow_after` parameter
        user_info = list(zip(follow_buttons, person_list))
        non_eligible = []
        not_found = []

        for button, person in user_info:
            if person not in automatedFollowedPool["all"].keys():
                not_found.append(person)
            elif (person in automatedFollowedPool["all"].keys() and
                  person not in automatedFollowedPool["eligible"].keys()):
                non_eligible.append(person)

        user_info = [pair for pair in user_info if pair[1] not in non_eligible]
        logger.info("Total {} users available to unfollow"
                    "  ~not found in 'followedPool.csv': {}  |  didn't pass "
                    "`unfollow_after`: {}".format(
            len(user_info), len(not_found), len(non_eligible)))

        if len(user_info) < 1:
            logger.info("There are no any users to unfollow")
            return 0
        elif len(user_info) < amount:
            logger.info(
                "Could not grab requested amount of usernames to unfollow:  "
                "{}/{}  ~using available amount".format(len(user_info),
                                                        amount))
            amount = len(user_info)

        if style == "LIFO":
            user_info = list(reversed(user_info))
        elif style == "RANDOM":
            random.shuffle(user_info)

        # unfollow loop
        try:
            hasSlept = False

            for button, person in user_info:
                if unfollowNum >= amount:
                    logger.info(
                        "--> Total unfollowNum reached it's amount given: {}"
                            .format(unfollowNum))
                    break

                if jumps["consequent"]["unfollows"] >= jumps["limit"][
                    "unfollows"]:
                    logger.warning(
                        "--> Unfollow quotient reached its peak!\t~leaving "
                        "Unfollow-Users activity\n")
                    break

                if (unfollowNum != 0 and
                        hasSlept is False and
                        unfollowNum % 10 == 0 and
                        sleep_delay not in [0, None]):
                    logger.info("sleeping for about {} min\n"
                                .format(int(sleep_delay / 60)))
                    sleep(sleep_delay)
                    hasSlept = True
                    pass

                if person not in dont_include:
                    logger.info(
                        "Ongoing Unfollow [{}/{}]: now unfollowing '{}'..."
                            .format(unfollowNum + 1,
                                    amount,
                                    person.encode('utf-8')))

                    person_id = (automatedFollowedPool["all"][person]["id"] if
                                 person in automatedFollowedPool[
                                     "all"].keys() else False)

                    try:
                        unfollow_state, msg = unfollow_user(browser,
                                                            "dialog",
                                                            username,
                                                            person,
                                                            person_id,
                                                            button,
                                                            relationship_data,
                                                            logger,
                                                            logfolder)
                    except Exception as exc:
                        logger.error("Unfollow loop error:\n\n{}\n\n".format(
                            str(exc).encode('utf-8')))

                    if unfollow_state is True:
                        unfollowNum += 1
                        # reset jump counter after a successful unfollow
                        jumps["consequent"]["unfollows"] = 0

                    elif msg == "jumped":
                        # will break the loop after certain consecutive jumps
                        jumps["consequent"]["unfollows"] += 1

                    elif msg in ["temporary block", "not connected",
                                 "not logged in"]:
                        # break the loop in extreme conditions to prevent
                        # misbehaviours
                        logger.warning(
                            "There is a serious issue: '{}'!\t~leaving "
                            "Unfollow-Users activity".format(
                                msg))
                        break

                    # To only sleep once until there is the next unfollow
                    if hasSlept:
                        hasSlept = False

                else:
                    logger.info(
                        "Not unfollowing '{}'!  ~user is in the "
                        "whitelist\n".format(
                            person))

        except Exception as exc:
            logger.error("Unfollow loop error:\n\n{}\n\n".format(
                str(exc).encode('utf-8')))

    else:
        logger.info(
            "Please select a proper unfollow method!  ~leaving unfollow "
            "activity\n")

    return unfollowNum


def follow_user(browser, track, login, user_name, button, blacklist, logger,
                logfolder):
    """ Follow a user either from the profile page or post page or dialog
    box """
    # list of available tracks to follow in: ["profile", "post" "dialog"]

    # check action availability
    if quota_supervisor("follows") == "jump":
        return False, "jumped"

    if track in ["profile", "post"]:
        if track == "profile":
            # check URL of the webpage, if it already is user's profile
            # page, then do not navigate to it again
            user_link = "https://www.instagram.com/{}/".format(user_name)
            web_address_navigator(browser, user_link)

        # find out CURRENT following status
        following_status, follow_button = get_following_status(browser,
                                                               track,
                                                               login,
                                                               user_name,
                                                               None,
                                                               logger,
                                                               logfolder)
        if following_status in ["Follow", "Follow Back"]:
            click_visibly(browser, follow_button)  # click to follow
            follow_state, msg = verify_action(browser, "follow", track, login,
                                              user_name, None, logger,
                                              logfolder)
            if follow_state is not True:
                return False, msg

        elif following_status in ["Following", "Requested"]:
            if following_status == "Following":
                logger.info("--> Already following '{}'!\n".format(user_name))

            elif following_status == "Requested":
                logger.info("--> Already requested '{}' to follow!\n".format(
                    user_name))

            sleep(1)
            return False, "already followed"

        elif following_status in ["Unblock", "UNAVAILABLE"]:
            if following_status == "Unblock":
                failure_msg = "user is in block"

            elif following_status == "UNAVAILABLE":
                failure_msg = "user is inaccessible"

            logger.warning(
                "--> Couldn't follow '{}'!\t~{}".format(user_name,
                                                        failure_msg))
            return False, following_status

        elif following_status is None:
            sirens_wailing, emergency_state = emergency_exit(browser, login,
                                                             logger)
            if sirens_wailing is True:
                return False, emergency_state

            else:
                logger.warning(
                    "--> Couldn't unfollow '{}'!\t~unexpected failure".format(
                        user_name))
                return False, "unexpected failure"
    elif track == "dialog":
        click_element(browser, button)
        sleep(3)

    # general tasks after a successful follow
    logger.info("--> Followed '{}'!".format(user_name.encode("utf-8")))
    update_activity('follows')

    # get user ID to record alongside username
    user_id = get_user_id(browser, track, user_name, logger)

    logtime = datetime.now().strftime('%Y-%m-%d %H:%M')
    log_followed_pool(login, user_name, logger, logfolder, logtime, user_id)

    follow_restriction("write", user_name, None, logger)

    if blacklist['enabled'] is True:
        action = 'followed'
        add_user_to_blacklist(user_name,
                              blacklist['campaign'],
                              action,
                              logger,
                              logfolder)

    # get the post-follow delay time to sleep
    naply = get_action_delay("follow")
    sleep(naply)

    return True, "success"


def scroll_to_bottom_of_followers_list(browser, element):
    browser.execute_script(
        "arguments[0].children[1].scrollIntoView()", element)
    sleep(1)
    return


def get_users_through_dialog(browser,
                             login,
                             user_name,
                             amount,
                             users_count,
                             randomize,
                             dont_include,
                             blacklist,
                             follow_times,
                             simulation,
                             channel,
                             jumps,
                             logger,
                             logfolder):
    sleep(2)
    real_amount = amount
    if randomize and amount >= 3:
        # expanding the population for better sampling distribution
        amount = amount * 3

    if amount > int(
            users_count * 0.85):  # taking 85 percent of possible amounts is
        # a safe study
        amount = int(users_count * 0.85)
    try_again = 0
    sc_rolled = 0

    # find dialog box
    dialog_address = "//body/div[2]/div/div[2]"
    dialog = browser.find_element_by_xpath(dialog_address)

    # scroll to end of follower list to initiate first load which hides the
    # suggestions
    scroll_to_bottom_of_followers_list(browser, dialog)

    buttons = get_buttons_from_dialog(dialog, channel)

    abort = False
    person_list = []
    total_list = len(buttons)
    simulated_list = []
    simulator_counter = 0
    start_time = time.time()
    pts_printed = False

    # scroll down if the generated list of user to follow is not enough to
    # follow amount set
    while (total_list < amount) and not abort:
        before_scroll = total_list
        for i in range(4):
            scroll_bottom(browser, dialog, 2)
            sc_rolled += 1
            simulator_counter += 1
            buttons = get_buttons_from_dialog(dialog, channel)
            total_list = len(buttons)
            progress_tracker(total_list, amount, start_time, logger)

        abort = (before_scroll == total_list)
        if abort:
            if total_list < real_amount:
                print('')
                logger.info("Failed to load desired amount of users!\n")

        if sc_rolled > 85:  # you may want to use up to 100
            if total_list < amount:
                print('')
                logger.info(
                    "Too many requests sent!  attempt: {}  |  gathered "
                    "links: {}"
                    "\t~sleeping a bit".format(try_again + 1, total_list))
                sleep(random.randint(600, 655))
                try_again += 1
                sc_rolled = 0

        # Will follow a little bit of users in order to simulate real
        # interaction
        if (simulation["enabled"] is True and
                simulation["percentage"] >= random.randint(1, 100) and
                (simulator_counter > random.randint(5, 17) or
                 abort is True or
                 total_list >= amount or
                 sc_rolled == random.randint(3, 5)) and
                len(buttons) > 0):

            quick_amount = 1 if not total_list >= amount else random.randint(1,
                                                                             4)

            for i in range(0, quick_amount):
                quick_index = random.randint(0, len(buttons) - 1)
                quick_button = buttons[quick_index]
                quick_username = dialog_username_extractor(quick_button)

                if quick_username and quick_username[0] not in simulated_list:
                    if not pts_printed:
                        print('\n')
                        if total_list >= amount:
                            pts_printed = True

                    logger.info("Simulated follow : {}".format(
                        len(simulated_list) + 1))

                    quick_follow = follow_through_dialog(browser,
                                                         login,
                                                         quick_username,
                                                         quick_button,
                                                         quick_amount,
                                                         dont_include,
                                                         blacklist,
                                                         follow_times,
                                                         jumps,
                                                         logger,
                                                         logfolder)
                    if ((quick_amount == 1
                        or i != (quick_amount - 1))
                        and (not pts_printed
                             or not abort)):
                        print('')
                    simulated_list.extend(quick_follow)

            simulator_counter = 0

    print('')
    person_list = dialog_username_extractor(buttons)

    if randomize:
        random.shuffle(person_list)

    person_list = person_list[:(real_amount - len(simulated_list))]

    for user in simulated_list:  # add simulated users to the `person_list`
        # in random index
        if user not in person_list:
            person_list.insert(random.randint(0, abs(len(person_list) - 1)),
                               user)

    return person_list, simulated_list


def dialog_username_extractor(buttons):
    """ Extract username of a follow button from a dialog box """

    if not isinstance(buttons, list):
        buttons = [buttons]

    person_list = []
    for person in buttons:
        if person and hasattr(person, 'text') and person.text:
            try:
                person_list.append(person.find_element_by_xpath("../../../*")
                                   .find_elements_by_tag_name("a")[1].text)
            except IndexError:
                pass  # Element list is too short to have a [1] element

    return person_list


def follow_through_dialog(browser,
                          login,
                          person_list,
                          buttons,
                          amount,
                          dont_include,
                          blacklist,
                          follow_times,
                          jumps,
                          logger,
                          logfolder):
    """ Will follow username directly inside a dialog box """
    if not isinstance(person_list, list):
        person_list = [person_list]

    if not isinstance(buttons, list):
        buttons = [buttons]

    person_followed = []
    followNum = 0

    try:
        for person, button in zip(person_list, buttons):
            if followNum >= amount:
                logger.info("--> Total follow number reached: {}"
                            .format(followNum))
                break

            elif jumps["consequent"]["follows"] >= jumps["limit"]["follows"]:
                logger.warning(
                    "--> Follow quotient reached its peak!\t~leaving "
                    "Follow-Through-Dialog activity\n")
                break

            if (person not in dont_include and
                    not follow_restriction("read", person, follow_times,
                                           logger)):
                follow_state, msg = follow_user(browser,
                                                "dialog",
                                                login,
                                                person,
                                                button,
                                                blacklist,
                                                logger,
                                                logfolder)
                if follow_state is True:
                    # register this session's followed user for further
                    # interaction
                    person_followed.append(person)
                    followNum += 1
                    # reset jump counter after a successful follow
                    jumps["consequent"]["follows"] = 0

                elif msg == "jumped":
                    # will break the loop after certain consecutive jumps
                    jumps["consequent"]["follows"] += 1

            else:
                logger.info(
                    "Not followed '{}'  ~inappropriate user".format(person))

    except BaseException as e:
        logger.error(
            "Error occurred while following through dialog box:\n{}".format(
                str(e)))

    return person_followed


def get_given_user_followers(browser,
                             login,
                             user_name,
                             amount,
                             dont_include,
                             randomize,
                             blacklist,
                             follow_times,
                             simulation,
                             jumps,
                             logger,
                             logfolder):
    """
    For the given username, follow their followers.

    :param browser: webdriver instance
    :param login:
    :param user_name: given username of account to follow
    :param amount: the number of followers to follow
    :param dont_include: ignore these usernames
    :param randomize: randomly select from users' followers
    :param blacklist:
    :param follow_times:
    :param logger: the logger instance
    :param logfolder: the logger folder
    :return: list of user's followers also followed
    """
    user_name = user_name.strip().lower()

    user_link = "https://www.instagram.com/{}/".format(user_name)
    web_address_navigator(browser, user_link)

    if not is_page_available(browser, logger):
        return [], []

    # check how many people are following this user.
    allfollowers, allfollowing = get_relationship_counts(browser, user_name,
                                                         logger)

    # skip early for no followers
    if not allfollowers:
        logger.info("'{}' has no followers".format(user_name))
        return [], []

    elif allfollowers < amount:
        logger.warning(
            "'{}' has less followers- {}, than the given amount of {}".format(
                user_name, allfollowers, amount))

    # locate element to user's followers
    try:
        followers_link = browser.find_elements_by_xpath(
            '//a[@href="/{}/followers/"]'.format(user_name))
        click_element(browser, followers_link[0])
        # update server calls
        update_activity()

    except NoSuchElementException:
        logger.error(
            'Could not find followers\' link for {}'.format(user_name))
        return [], []

    except BaseException as e:
        logger.error("`followers_link` error {}".format(str(e)))
        return [], []

    channel = "Follow"
    person_list, simulated_list = get_users_through_dialog(browser, login,
                                                           user_name, amount,
                                                           allfollowers,
                                                           randomize,
                                                           dont_include,
                                                           blacklist,
                                                           follow_times,
                                                           simulation,
                                                           channel, jumps,
                                                           logger, logfolder)

    return person_list, simulated_list


def get_given_user_following(browser,
                             login,
                             user_name,
                             amount,
                             dont_include,
                             randomize,
                             blacklist,
                             follow_times,
                             simulation,
                             jumps,
                             logger,
                             logfolder):
    user_name = user_name.strip().lower()

    user_link = "https://www.instagram.com/{}/".format(user_name)
    web_address_navigator(browser, user_link)

    if not is_page_available(browser, logger):
        return [], []

    #  check how many poeple are following this user.
    #  throw RuntimeWarning if we are 0 people following this user
    try:
        allfollowing = format_number(
            browser.find_element_by_xpath("//a[contains"
                                          "(@href,'following')]/span").text)

    except NoSuchElementException:
        try:
            allfollowing = browser.execute_script(
                "return window._sharedData.entry_data."
                "ProfilePage[0].graphql.user.edge_follow.count")

        except WebDriverException:
            try:
                browser.execute_script("location.reload()")
                update_activity()

                allfollowing = browser.execute_script(
                    "return window._sharedData.entry_data."
                    "ProfilePage[0].graphql.user.edge_follow.count")

            except WebDriverException:
                try:
                    topCount_elements = browser.find_elements_by_xpath(
                        "//span[contains(@class,'g47SY')]")

                    if topCount_elements:
                        allfollowing = format_number(topCount_elements[2].text)
                    else:
                        logger.info(
                            "Failed to get following count of '{}'  ~empty "
                            "list".format(
                                user_name))
                        allfollowing = None

                except (NoSuchElementException, IndexError):
                    logger.error(
                        "\nError occured during getting the following count "
                        "of '{}'\n".format(
                            user_name))
                    return [], []

    # skip early for no followers
    if not allfollowing:
        logger.info("'{}' has no any following".format(user_name))
        return [], []

    elif allfollowing < amount:
        logger.warning(
            "'{}' has less following- {} than the desired amount of {}".format(
                user_name, allfollowing, amount))

    try:
        following_link = browser.find_elements_by_xpath(
            '//a[@href="/{}/following/"]'.format(user_name))
        click_element(browser, following_link[0])
        # update server calls
        update_activity()

    except NoSuchElementException:
        logger.error(
            'Could not find following\'s link for {}'.format(user_name))
        return [], []

    except BaseException as e:
        logger.error("`following_link` error {}".format(str(e)))
        return [], []

    channel = "Follow"
    person_list, simulated_list = get_users_through_dialog(browser, login,
                                                           user_name, amount,
                                                           allfollowing,
                                                           randomize,
                                                           dont_include,
                                                           blacklist,
                                                           follow_times,
                                                           simulation,
                                                           channel, jumps,
                                                           logger, logfolder)

    return person_list, simulated_list


def dump_follow_restriction(profile_name, logger, logfolder):
    """ Dump follow restriction data to a local human-readable JSON """

    try:
        # get a DB and start a connection
        db, id = get_database()
        conn = sqlite3.connect(db)

        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(
                "SELECT * FROM followRestriction WHERE profile_id=:var",
                {"var": id})
            data = cur.fetchall()

        if data:
            # get the existing data
            filename = "{}followRestriction.json".format(logfolder)
            if os.path.isfile(filename):
                with open(filename) as followResFile:
                    current_data = json.load(followResFile)
            else:
                current_data = {}

            # pack the new data
            follow_data = {user_data[1]: user_data[2] for user_data in
                           data or []}
            current_data[profile_name] = follow_data

            # dump the fresh follow data to a local human readable JSON
            with open(filename, 'w') as followResFile:
                json.dump(current_data, followResFile)

    except Exception as exc:
        logger.error(
            "Pow! Error occurred while dumping follow restriction data to a "
            "local JSON:\n\t{}".format(
                str(exc).encode("utf-8")))

    finally:
        if conn:
            # close the open connection
            conn.close()


def follow_restriction(operation, username, limit, logger):
    """ Keep track of the followed users and help avoid excessive follow of
    the same user """

    try:
        # get a DB and start a connection
        db, id = get_database()
        conn = sqlite3.connect(db)

        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(
                "SELECT * FROM followRestriction WHERE profile_id=:id_var "
                "AND username=:name_var",
                {"id_var": id, "name_var": username})
            data = cur.fetchone()
            follow_data = dict(data) if data else None

            if operation == "write":
                if follow_data is None:
                    # write a new record
                    cur.execute(
                        "INSERT INTO followRestriction (profile_id, "
                        "username, times) VALUES (?, ?, ?)",
                        (id, username, 1))
                else:
                    # update the existing record
                    follow_data["times"] += 1
                    sql = "UPDATE followRestriction set times = ? WHERE " \
                          "profile_id=? AND username = ?"
                    cur.execute(sql, (follow_data["times"], id, username))

                # commit the latest changes
                conn.commit()

            elif operation == "read":
                if follow_data is None:
                    return False

                elif follow_data["times"] < limit:
                    return False

                else:
                    exceed_msg = "" if follow_data[
                                           "times"] == limit else "more than "
                    logger.info("---> {} has already been followed {}{} times"
                                .format(username, exceed_msg, str(limit)))
                    return True

    except Exception as exc:
        logger.error(
            "Dap! Error occurred with follow Restriction:\n\t{}".format(
                str(exc).encode("utf-8")))

    finally:
        if conn:
            # close the open connection
            conn.close()


def unfollow_user(browser, track, username, person, person_id, button,
                  relationship_data, logger, logfolder):
    """ Unfollow a user either from the profile or post page or dialog box """
    # list of available tracks to unfollow in: ["profile", "post" "dialog"]

    # check action availability
    if quota_supervisor("unfollows") == "jump":
        return False, "jumped"

    if track in ["profile", "post"]:
        """ Method of unfollowing from a user's profile page or post page """
        if track == "profile":
            user_link = "https://www.instagram.com/{}/".format(person)
            web_address_navigator(browser, user_link)

        # find out CURRENT follow status
        following_status, follow_button = get_following_status(browser,
                                                               track,
                                                               username,
                                                               person,
                                                               person_id,
                                                               logger,
                                                               logfolder)

        if following_status in ["Following", "Requested"]:
            click_element(browser, follow_button)  # click to unfollow
            sleep(4)  # TODO: use explicit wait here
            confirm_unfollow(browser)
            unfollow_state, msg = verify_action(browser, "unfollow", track,
                                                username,
                                                person, person_id, logger,
                                                logfolder)
            if unfollow_state is not True:
                return False, msg

        elif following_status in ["Follow", "Follow Back"]:
            logger.info(
                "--> Already unfollowed '{}'! or a private user that "
                "rejected your req".format(
                    person))
            post_unfollow_cleanup(["successful", "uncertain"], username,
                                  person, relationship_data, person_id, logger,
                                  logfolder)
            return False, "already unfollowed"

        elif following_status in ["Unblock", "UNAVAILABLE"]:
            if following_status == "Unblock":
                failure_msg = "user is in block"

            elif following_status == "UNAVAILABLE":
                failure_msg = "user is inaccessible"

            logger.warning(
                "--> Couldn't unfollow '{}'!\t~{}".format(person, failure_msg))
            post_unfollow_cleanup("uncertain", username, person,
                                  relationship_data, person_id, logger,
                                  logfolder)
            return False, following_status

        elif following_status is None:
            sirens_wailing, emergency_state = emergency_exit(browser, username,
                                                             logger)
            if sirens_wailing is True:
                return False, emergency_state

            else:
                logger.warning(
                    "--> Couldn't unfollow '{}'!\t~unexpected failure".format(
                        person))
                return False, "unexpected failure"
    elif track == "dialog":
        """  Method of unfollowing from a dialog box """
        click_element(browser, button)
        sleep(4)  # TODO: use explicit wait here
        confirm_unfollow(browser)

    # general tasks after a successful unfollow
    logger.info("--> Unfollowed '{}'!".format(person))
    update_activity('unfollows')
    post_unfollow_cleanup("successful", username, person, relationship_data,
                          person_id, logger, logfolder)

    # get the post-unfollow delay time to sleep
    naply = get_action_delay("unfollow")
    sleep(naply)

    return True, "success"


def confirm_unfollow(browser):
    """ Deal with the confirmation dialog boxes during an unfollow """
    attempt = 0

    while attempt < 3:
        try:
            attempt += 1
            button_xp = "//button[text()='Unfollow']"  # "//button[contains(
            # text(), 'Unfollow')]"
            unfollow_button = browser.find_element_by_xpath(button_xp)

            if unfollow_button.is_displayed():
                click_element(browser, unfollow_button)
                sleep(2)
                break

        except (ElementNotVisibleException, NoSuchElementException) as exc:
            # prob confirm dialog didn't pop up
            if isinstance(exc, ElementNotVisibleException):
                break

            elif isinstance(exc, NoSuchElementException):
                sleep(1)
                pass


def post_unfollow_cleanup(state, username, person, relationship_data,
                          person_id, logger, logfolder):
    """ Casual local data cleaning after an unfollow """
    if not isinstance(state, list):
        state = [state]

    delete_line_from_file("{0}{1}_followedPool.csv"
                          .format(logfolder, username), person, logger)

    if "successful" in state:
        if person in relationship_data[username]["all_following"]:
            relationship_data[username]["all_following"].remove(person)

    if "uncertain" in state:
        # this user was found in our unfollow list but currently is not
        # being followed
        logtime = get_log_time()
        log_uncertain_unfollowed_pool(username, person, logger, logfolder,
                                      logtime, person_id)
        # take a generic 3 seconds of sleep per each uncertain unfollow
        sleep(3)

    # save any unfollowed person
    log_record_all_unfollowed(username, person, logger, logfolder)
    print('')


def get_buttons_from_dialog(dialog, channel):
    """ Gets buttons from the `Followers` or `Following` dialog boxes"""

    if channel == "Follow":
        # get follow buttons. This approach will find the follow buttons and
        # ignore the Unfollow/Requested buttons.
        buttons = dialog.find_elements_by_xpath(
            "//button[text()='Follow']")

    elif channel == "Unfollow":
        buttons = dialog.find_elements_by_xpath(
            "//button[text() = 'Following']")

    return buttons


def get_user_id(browser, track, username, logger):
    """ Get user's ID either from a profile page or post page """
    user_id = "unknown"

    if track != "dialog":  # currently do not get the user ID for follows
        # from 'dialog'
        user_id = find_user_id(browser, track, username, logger)

    return user_id


def verify_username_by_id(browser, username, person, person_id, logger,
                          logfolder):
    """ Check if the given user has changed username after the time of
    followed """
    # try to find the user by ID
    if person_id is None:
        person_id = load_user_id(username, person, logger, logfolder)

    if person_id and person_id not in [None, "unknown", "undefined"]:
        # get the [new] username of the user from the stored user ID
        person_new = get_username_from_id(browser, person_id, logger)
        if person_new:
            if person_new != person:
                logger.info(
                    "User '{}' has changed username and now is called '{}' :S"
                        .format(person, person_new))
            return person_new

        else:
            logger.info(
                "The user with the ID of '{}' is unreachable".format(person))

    else:
        logger.info(
            "The user ID of '{}' doesn't exist in local records".format(
                person))

    return None


def verify_action(browser, action, track, username, person, person_id, logger,
                  logfolder):
    """ Verify if the action has succeeded """
    # currently supported actions are follow & unfollow

    if action in ["follow", "unfollow"]:
        if action == "follow":
            post_action_text = "//button[text()='Following' or text(" \
                               ")='Requested']"

        elif action == "unfollow":
            post_action_text = "//button[text()='Follow' or text()='Follow " \
                               "Back']"

        button_change = explicit_wait(browser, "VOEL",
                                      [post_action_text, "XPath"], logger, 7,
                                      False)
        if not button_change:
            reload_webpage(browser)
            following_status, follow_button = get_following_status(browser,
                                                                   track,
                                                                   username,
                                                                   person,
                                                                   person_id,
                                                                   logger,
                                                                   logfolder)
            # find action state *.^
            if following_status in ["Following", "Requested"]:
                action_state = False if action == "unfollow" else True

            elif following_status in ["Follow", "Follow Back"]:
                action_state = True if action == "unfollow" else False

            else:
                action_state = None

            # handle it!
            if action_state is True:
                logger.info(
                    "Last {} is verified after reloading the page!".format(
                        action))

            elif action_state is False:
                # try to do the action one more time!
                click_visibly(browser, follow_button)

                if action == "unfollow":
                    sleep(4)  # TODO: use explicit wait here
                    confirm_unfollow(browser)

                button_change = explicit_wait(browser, "VOEL",
                                              [post_action_text, "XPath"],
                                              logger, 9, False)
                if not button_change:
                    logger.warning("Phew! Last {0} is not verified."
                                   "\t~'{1}' might be temporarily blocked "
                                   "from {0}ing\n"
                                   .format(action, username))
                    sleep(210)
                    return False, "temporary block"

            elif action_state is None:
                logger.error(
                    "Hey! Last {} is not verified out of an unexpected "
                    "failure!".format(action))
                return False, "unexpected"

    return True, "success"


def post_unfollow_actions(browser, person, logger):
    pass


def get_follow_requests(browser, amount, sleep_delay, logger, logfolder):
    """ Get follow requests from instagram access tool list """

    user_link = "https://www.instagram.com/accounts/access_tool" \
                "/current_follow_requests"
    web_address_navigator(browser, user_link)

    list_of_users = []
    view_more_button_exist = True
    view_more_clicks = 0

    while len(
            list_of_users) < amount and view_more_clicks < 750 and \
            view_more_button_exist:
        sleep(4)
        list_of_users = browser.find_elements_by_xpath("//section/div")

        if len(list_of_users) == 0:
            logger.info("There are not outgoing follow requests")
            break

        try:
            view_more_button = browser.find_element_by_xpath(
                "//button[text()='View More']")
        except NoSuchElementException:
            view_more_button_exist = False

        if view_more_button_exist:
            logger.info(
                "Found '{}' outgoing follow requests, Going to ask for more..."
                .format(len(list_of_users))
            )
            click_element(browser, view_more_button)
            view_more_clicks += 1

    users_to_unfollow = []

    for user in list_of_users:
        users_to_unfollow.append(user.text)
        if len(users_to_unfollow) == amount:
            break

    logger.info(
        "Found '{}' outgoing follow requests '{}'"
        .format(len(users_to_unfollow), users_to_unfollow))

    return users_to_unfollow
