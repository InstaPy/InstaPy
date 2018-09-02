""" Module which handles the follow features like unfollowing and following """
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
from .util import get_username
from .util import find_user_id
from .util import new_tab
from .util import explicit_wait
from .print_log_writer import log_followed_pool
from .print_log_writer import log_uncertain_unfollowed_pool
from .print_log_writer import log_record_all_unfollowed
from .relationship_tools import get_followers
from .relationship_tools import get_nonfollowers
from .database_engine import get_database
from .quota_supervisor import quota_supervisor

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotVisibleException




def set_automated_followed_pool(username, unfollow_after, logger, logfolder):
    """ Generare a user list based on the InstaPy followed usernames """
    pool_name = "{0}{1}_followedPool.csv".format(logfolder, username)
    automatedFollowedPool = {"all": {}, "eligible": {}}
    time_stamp = None
    user_id = False   # `False` rather than `None` is *intentional

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
                            log_time = datetime.strptime(time_stamp, '%Y-%m-%d %H:%M')
                        except ValueError:
                            continue

                        former_epoch = (log_time - datetime(1970, 1, 1)).total_seconds()
                        cur_epoch = (datetime.now() - datetime(1970, 1, 1)).total_seconds()

                        if cur_epoch - former_epoch > unfollow_after:
                            automatedFollowedPool["eligible"].update({user: {"id": user_id}})

                else:
                    automatedFollowedPool["eligible"].update({user: {"id": user_id}})

        followedPoolFile.close()

    except BaseException as exc:
        logger.error("Error occured while generating a user list from the followed pool!\n\t{}"
                        .format(str(exc).encode("utf-8")))

    return automatedFollowedPool



def get_following_status(browser, person, logger):
    """ Verify if you are following the user in the loaded page """
    following = None
    follow_button = None

    try:
        follow_button = browser.find_element_by_xpath(
            "//*[contains(text(), 'Follow')]")

        if follow_button.text == 'Following':
            following = True

        else:
            if follow_button.text in ['Follow', 'Follow Back']:
                following = False

            else:
                follow_button = browser.find_element_by_xpath(
                    "//*[contains(text(), 'Requested')]")

                if follow_button.text == "Requested":
                    following = "Requested"

    except NoSuchElementException:
        logger.error("--> Unfollow issue with '{}'!"
                      "\t~unable to detect the following status"
                          .format(person.encode("utf-8")))

    return following, follow_button



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
                customList[0] == True and
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
                InstapyFollowed[0] == True and
                    InstapyFollowed[1] in ["all", "nonfollowers"]):
        unfollow_track = InstapyFollowed[1]
        InstapyFollowed = True
    else:
        InstapyFollowed = False

    unfollowNum = 0

    user_link = "https://www.instagram.com/{}/".format(username)

    # check URL of the webpage, if it already is the one to be navigated then do not navigate to it again
    web_address_navigator(browser, user_link)

    # check how many poeple we are following
    allfollowers, allfollowing = get_relationship_counts(browser, username, logger)

    if allfollowing is None:
        logger.warning("Unable to find the count of users followed  ~leaving unfollow feature")
        return 0
    elif allfollowing == 0:
        logger.warning("There are 0 people to unfollow  ~leaving unfollow feature")
        return 0

    if amount > allfollowing:
        logger.info("There are less users to unfollow than you have requested:  "
            "{}/{}  ~using available amount\n".format(allfollowing, amount))
        amount = allfollowing

    if (customList == True or
            InstapyFollowed == True or
                nonFollowers == True):

        if customList == True:
            logger.info("Unfollowing from the list of pre-defined usernames\n")
            unfollow_list = customList_data

        elif InstapyFollowed == True:
            logger.info("Unfollowing the users followed by InstaPy\n")
            unfollow_list = automatedFollowedPool["eligible"].keys()

        elif nonFollowers == True:
            logger.info("Unfollowing the users who do not follow back\n")
            """  Unfollow only the users who do not follow you back """
            unfollow_list = get_nonfollowers(browser,
                                              username,
                                               relationship_data,
                                                False,
                                                 True,
                                                  logger,
                                                   logfolder)

        # pick only the users in the right track- ["all" or "nonfollowers"] for `customList` and
        #  `InstapyFollowed` unfollow methods
        if customList == True or InstapyFollowed == True:
            if unfollow_track == "nonfollowers":
                all_followers = get_followers(browser,
                                               username,
                                                "full",
                                                 relationship_data,
                                                  False,
                                                   True,
                                                    logger,
                                                    logfolder)
                loyal_users = [user for user in unfollow_list if user in all_followers]
                logger.info("Found {} loyal followers!  ~will not unfollow them".format(len(loyal_users)))
                unfollow_list = [user for user in unfollow_list if user not in loyal_users]

            elif unfollow_track != "all":
                logger.info("Unfollow track is not specified! ~choose \"all\" or \"nonfollowers\"")
                return 0

        # re-generate unfollow list according to the `unfollow_after` parameter for `customList` and
        #  `nonFollowers` unfollow methods
        if customList == True or nonFollowers == True:
            not_found = []
            non_eligible = []
            for person in unfollow_list:
                if person not in automatedFollowedPool["all"].keys():
                    not_found.append(person)
                elif (person in automatedFollowedPool["all"].keys() and
                        person not in automatedFollowedPool["eligible"].keys()):
                    non_eligible.append(person)

            unfollow_list = [user for user in unfollow_list if user not in non_eligible]
            logger.info("Total {} users available to unfollow"
                            "  ~not found in 'followedPool.csv': {}  |  didn't pass `unfollow_after`: {}\n".format(
                                len(unfollow_list), len(not_found), len(non_eligible)))

        elif InstapyFollowed == True:
            non_eligible = [user for user in automatedFollowedPool["all"].keys() if
                            user not in automatedFollowedPool["eligible"].keys()]
            logger.info("Total {} users available to unfollow  ~didn't pass `unfollow_after`: {}\n"
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
            logger.info("You have requested more amount: {} than {} of users available to unfollow"
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

                if jumps["consequent"]["unfollows"] >= jumps["limit"]["unfollows"]:
                    logger.warning("--> Unfollow quotient reached its peak!\t~leaving Unfollow-Users activity\n")
                    break

                if sleep_counter >= sleep_after:
                    delay_random = random.randint(ceil(sleep_delay*0.85), ceil(sleep_delay*1.14))
                    logger.info("Unfollowed {} new users  ~sleeping about {}\n".format(sleep_counter,
                                    '{} seconds'.format(delay_random) if delay_random < 60 else
                                    '{} minutes'.format(float("{0:.2f}".format(delay_random/60)))))
                    sleep(delay_random)
                    sleep_counter = 0
                    sleep_after = random.randint(8, 12)
                    pass

                if person not in dont_include:
                    logger.info(
                        "Ongoing Unfollow [{}/{}]: now unfollowing '{}'..."
                        .format(unfollowNum+1, amount, person.encode('utf-8')))

                    person_id = (automatedFollowedPool["all"][person]["id"] if
                                person in automatedFollowedPool["all"].keys() else False)

                    unfollow_state, msg = unfollow_user(browser,
                                                         "profile",
                                                          username,
                                                          person,
                                                           person_id,
                                                            None,
                                                             relationship_data,
                                                              logger,
                                                              logfolder)
                    if unfollow_state == True:
                        unfollowNum += 1
                        sleep_counter += 1
                        # reset jump counter after a successful unfollow
                        jumps["consequent"]["unfollows"] = 0

                    elif msg == "jumped":
                        # will break the loop after certain consecutive jumps
                        jumps["consequent"]["unfollows"] += 1

                    elif msg in ["shadow ban", "not connected", "not logged in"]:
                        # break the loop in extreme conditions to prevent misbehaviours
                        logger.warning("There is a serious issue: '{}'!\t~leaving Unfollow-Users activity".format(msg))
                        break

                else:
                    # if the user in dont include (should not be) we shall remove him from the follow list
                    # if he is a white list user (set at init and not during run time)
                    if person in white_list:
                        delete_line_from_file('{0}{1}_followedPool.csv'.format(logfolder, username),
                                              person, logger)
                        list_type = 'whitelist'
                    else:
                        list_type = 'dont_include'
                    logger.info("Not unfollowed '{}'!\t~user is in the list {}\n".format(person, list_type))
                    index += 1
                    continue
        except BaseException as e:
            logger.error("Unfollow loop error:  {}\n".format(str(e)))

    elif allFollowing == True:
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
            "//div[text()='Following']/../../following-sibling::div")

        sleep(3)

        # get persons, unfollow buttons, and length of followed pool
        person_list_a = dialog.find_elements_by_tag_name("a")
        person_list = []

        for person in person_list_a:

            if person and hasattr(person, 'text') and person.text:
                person_list.append(person.text)

        follow_buttons = dialog.find_elements_by_tag_name('button')

        # re-generate person list to unfollow according to the `unfollow_after` parameter
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
            "  ~not found in 'followedPool.csv': {}  |  didn't pass `unfollow_after`: {}".format(
                len(user_info), len(not_found), len(non_eligible)))

        if len(user_info) < 1:
            logger.info("There are no any users to unfollow")
            return 0
        elif len(user_info) < amount:
            logger.info("Could not grab requested amount of usernames to unfollow:  "
                "{}/{}  ~using available amount".format(len(user_info), amount))
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

                if jumps["consequent"]["unfollows"] >= jumps["limit"]["unfollows"]:
                    logger.warning("--> Unfollow quotient reached its peak!\t~leaving Unfollow-Users activity\n")
                    break

                if (unfollowNum != 0 and
                        hasSlept is False and
                            unfollowNum % 10 == 0):
                    logger.info("sleeping for about {} min\n"
                                .format(int(sleep_delay/60)))
                    sleep(sleep_delay)
                    hasSlept = True
                    pass

                if person not in dont_include:
                    logger.info(
                        "Ongoing Unfollow [{}/{}]: now unfollowing '{}'..."
                        .format(unfollowNum+1, amount, person.encode('utf-8')))

                    person_id = (automatedFollowedPool["all"][person]["id"] if
                                person in automatedFollowedPool["all"].keys() else False)

                    unfollow_state, msg = unfollow_user(browser,
                                                "dialog",
                                                 username,
                                                 person,
                                                  person_id,
                                                   button,
                                                    relationship_data,
                                                     logger,
                                                     logfolder)
                    if unfollow_state == True:
                        unfollowNum += 1
                        # reset jump counter after a successful unfollow
                        jumps["consequent"]["unfollows"] = 0

                    elif msg == "jumped":
                        # will break the loop after certain consecutive jumps
                        jumps["consequent"]["unfollows"] += 1

                    elif msg in ["shadow ban", "not connected", "not logged in"]:
                        # break the loop in extreme conditions to prevent misbehaviours
                        logger.warning("There is a serious issue: '{}'!\t~leaving Unfollow-Users activity".format(msg))
                        break

                    # To only sleep once until there is the next unfollow
                    if hasSlept:
                        hasSlept = False

                else:
                    logger.info("Not unfollowing '{}'!  ~user is in the whitelist\n".format(person))

        except Exception as exc:
            logger.error("Unfollow loop error:\n\n{}\n\n".format(str(exc).encode('utf-8')))

    else:
        logger.info("Please select a proper unfollow method!  ~leaving unfollow activity\n")

    return unfollowNum



def follow_user(browser, track, login, user_name, button, blacklist, logger, logfolder):
    """ Follows the user from either its 'profile' page, a 'post' page or the users 'dialog' box """
    # check action availability
    if quota_supervisor("follows") == "jump":
        return False, "jumped"

    # available tracks are to follow in `profile`, `post` and `dialog`
    if track in ["profile", "post"]:
        if track == "profile":
            # check URL of the webpage, if it already is user's profile page, then do not navigate to it again
            user_link = "https://www.instagram.com/{}/".format(user_name)
            web_address_navigator(browser, user_link)

        try:
            sleep(2)
            follow_xpath = "//button[text()='Follow' or text()='Follow Back']"
            follow_button = browser.find_element_by_xpath(follow_xpath)

            if follow_button.is_displayed():
                click_element(browser, follow_button)

            else:
                browser.execute_script("arguments[0].style.visibility = 'visible'; "
                                       "arguments[0].style.height = '10px'; "
                                       "arguments[0].style.width = '10px'; "
                                       "arguments[0].style.opacity = 1",
                                            follow_button)

                click_element(browser, follow_button)

                # verify the last follow
                following, follow_button = get_following_status(browser,
                                                                 user_name,
                                                                  logger)
                if not following:
                    browser.execute_script("location.reload()")
                    sleep(2)
                    following, follow_button = get_following_status(browser,
                                                                     user_name,
                                                                      logger)
                    if following is None:
                        sirens_wailing, emergency_state = emergency_exit(browser,
                                                                          user_name,
                                                                           logger)
                        if sirens_wailing == True:
                            logger.warning("There is a serious issue: '{}'!\n".format(emergency_state))
                            return False, emergency_state

                        else:
                            logger.error("Unexpected failure happened after last follow!\n")
                            return False "unexpected failure"

                    if following == False:
                        logger.warning("Last follow is not verified!\t~smells of a shadow ban\n")
                        sleep(600)
                        return False, "shadow ban"

                    else:
                        logger.info("Last follow is verified after reloading the page!\n")

        except NoSuchElementException:
            logger.info("--> '{}' is already followed".format(user_name))
            sleep(1)

            return False, "already followed"

        except StaleElementReferenceException:
            # https://stackoverflow.com/questions/16166261/selenium-webdriver-how-to-resolve-stale-element-reference-exception
            # 1. An element that is found on a web page referenced as a WebElement in WebDriver then the DOM changes
            # (probably due to JavaScript functions) that WebElement goes stale.
            # 2. The element has been deleted entirely.
            logger.error('--> element that is found on a web page referenced while the DOM changes')
            sleep(1)

            return False, "stale element"


    elif track == "dialog":
        click_element(browser, button)
        sleep(3)


    ## general tasks after a successful follow

    logger.info("--> Followed '{}'!".format(user_name.encode("utf-8")))
    update_activity('follows')

    # get user ID to record alongside username
    user_id = get_user_id(browser, track, user_name, logger)

    logtime = datetime.now().strftime('%Y-%m-%d %H:%M')
    log_followed_pool(login, user_name, logger, logfolder, logtime, user_id)

    follow_restriction("write", user_name, None, logger)

    if blacklist['enabled'] == True:
        action = 'followed'
        add_user_to_blacklist(user_name,
                               blacklist['campaign'],
                                action,
                                 logger,
                                  logfolder)
    sleep(3)

    return True, "success"



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
    person_followed = []
    real_amount = amount
    if randomize and amount >= 3:
        # expanding the popultaion for better sampling distribution
        amount = amount * 3

    if amount > int(users_count*0.85):   # taking 85 percent of possible amounts is a safe study
        amount = int(users_count*0.85)
    try_again = 0
    sc_rolled = 0

    # find dialog box
    dialog_address = "//div[text()='Followers' or text()='Following']/../../following-sibling::div"
    dialog = browser.find_element_by_xpath(dialog_address)

    buttons = get_buttons_from_dialog(dialog, channel)

    abort = False
    person_list = []
    total_list = len(buttons)
    simulated_list = []
    simulator_counter = 0

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
        abort = (before_scroll == total_list)
        if abort:
            if total_list < real_amount:
                logger.info("Failed to load desired amount of users!\n")

        if sc_rolled > 85:   # you may want to use up to 100
            if total_list < amount:
                logger.info("Too many requests sent!  attempt: {}  |  gathered links: {}"
                            "\t~sleeping a bit".format(try_again+1, total_list))
                sleep(random.randint(600, 655))
                try_again += 1
                sc_rolled = 0

        # Will follow a little bit of users in order to simulate real interaction
        if (simulation["enabled"] == True and
                simulation["percentage"] >= random.randint(1, 100) and
                   (simulator_counter > random.randint(5, 17) or
                        abort == True or
                            total_list >= amount or
                                sc_rolled == random.randint(3, 5)) and
                                    len(buttons) > 0):

            quick_amount = 1 if not total_list >= amount else random.randint(1, 4)

            for i in range(0, quick_amount):
                buttons = get_buttons_from_dialog(dialog, channel)
                quick_index = random.randint(0, len(buttons)-1)
                quick_button = buttons[quick_index]
                quick_username = dialog_username_extractor(quick_button)

                if quick_username and quick_username[0] not in simulated_list:
                    logger.info("Simulated follow : {}".format(len(simulated_list)+1))

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
                    print('')
                    simulated_list.extend(quick_follow)
                    # declare the dialog box once again after the DOM change
                    explicit_wait(browser, "VOEL", [dialog_address, "XPath"], logger)
                    dialog = browser.find_element_by_xpath(dialog_address)

            simulator_counter = 0

    # get buttons for last time
    buttons = get_buttons_from_dialog(dialog, channel)
    person_list = dialog_username_extractor(buttons)

    if randomize:
        random.shuffle(person_list)

    person_list = person_list[:(real_amount-len(simulated_list))]

    for user in simulated_list:   # add simulated users to the `person_list` in random index
        if user not in person_list:
            person_list.insert(random.randint(0, abs(len(person_list)-1)), user)

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
                logger.warning("--> Follow quotient reached its peak!\t~leaving Follow-Through-Dialog activity\n")
                break

            if (person not in dont_include and
                not follow_restriction("read", person, follow_times, logger)):
                follow_state, msg = follow_user(browser,
                                          "dialog",
                                           login,
                                            person,
                                             button,
                                              blacklist,
                                               logger,
                                                logfolder)
                if follow_state == True:
                    # register this session's followed user for further interaction
                    person_followed.append(person)
                    followNum += 1
                    # reset jump counter after a successful follow
                    jumps["consequent"]["follows"] = 0

                elif msg == "jumped":
                    # will break the loop after certain consecutive jumps
                    jumps["consequent"]["follows"] += 1

            else:
                logger.info("Not followed '{}'  ~inappropriate user".format(person))

    except BaseException as e:
        logger.error("Error occured while following through dialog box:\n{}".format(str(e)))

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
    user_name = user_name.strip()

    user_link = "https://www.instagram.com/{}/".format(user_name)
    web_address_navigator(browser, user_link)

    # check how many people are following this user.
    try:
        allfollowers = format_number(browser.find_element_by_xpath("//a[contains"
                                "(@href,'followers')]/span").text)
    except NoSuchElementException:
        try:
            allfollowers = browser.execute_script(
                "return window._sharedData.entry_data."
                "ProfilePage[0].graphql.user.edge_followed_by.count")
        except WebDriverException:
            try:
                browser.execute_script("location.reload()")
                allfollowers = browser.execute_script(
                    "return window._sharedData.entry_data."
                    "ProfilePage[0].graphql.user.edge_followed_by.count")
            except WebDriverException:
                try:
                    topCount_elements = browser.find_elements_by_xpath(
                        "//span[contains(@class,'g47SY')]")
                    if topCount_elements:
                        allfollowers = format_number(topCount_elements[1].text)
                    else:
                        logger.info("Failed to get followers count of '{}'  ~empty list".format(user_name))
                        allfollowers = None
                except NoSuchElementException:
                    logger.error("Error occured during getting the followers count of '{}'\n".format(user_name))
                    return [], []

    # skip early for no followers
    if not allfollowers:
        logger.info("'{}' has no followers".format(user_name))
        return [], []

    elif allfollowers < amount:
        logger.warning("'{}' has less followers- {}, than the given amount of {}".format(
            user_name, allfollowers, amount))

    # locate element to user's followers
    try:
        followers_link = browser.find_elements_by_xpath(
            '//a[@href="/{}/followers/"]'.format(user_name))
        click_element(browser, followers_link[0])
        # update server calls
        update_activity()

    except NoSuchElementException:
        logger.error('Could not find followers\' link for {}'.format(user_name))
        return [], []

    except BaseException as e:
        logger.error("`followers_link` error {}".format(str(e)))
        return [], []

    channel = "Follow"
    person_list, simulated_list = get_users_through_dialog(browser, login, user_name, amount,
                                                 allfollowers, randomize, dont_include,
                                                  blacklist, follow_times, simulation,
                                                   channel, jumps, logger, logfolder)

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
    user_name = user_name.strip()

    user_link = "https://www.instagram.com/{}/".format(user_name)
    web_address_navigator(browser, user_link)

    #  check how many poeple are following this user.
    #  throw RuntimeWarning if we are 0 people following this user
    try:
        allfollowing = format_number(browser.find_element_by_xpath("//a[contains"
                                "(@href,'following')]/span").text)
    except NoSuchElementException:
        try:
            allfollowing = browser.execute_script(
                "return window._sharedData.entry_data."
                "ProfilePage[0].graphql.user.edge_follow.count")
        except WebDriverException:
            try:
                browser.execute_script("location.reload()")
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
                        logger.info("Failed to get following count of '{}'  ~empty list".format(user_name))
                        allfollowing = None
                except NoSuchElementException:
                    logger.error("\nError occured during getting the following count of '{}'\n".format(user_name))
                    return [], []

    # skip early for no followers
    if not allfollowing:
        logger.info("'{}' has no any following".format(user_name))
        return [], []

    elif allfollowing < amount:
        logger.warning("'{}' has less following- {} than the desired amount of {}".format(
            user_name, allfollowing, amount))

    try:
        following_link = browser.find_elements_by_xpath(
            '//a[@href="/{}/following/"]'.format(user_name))
        click_element(browser, following_link[0])
        # update server calls
        update_activity()

    except NoSuchElementException:
        logger.error('Could not find following\'s link for {}'.format(user_name))
        return [], []

    except BaseException as e:
        logger.error("`following_link` error {}".format(str(e)))
        return [], []

    channel = "Follow"
    person_list, simulated_list = get_users_through_dialog(browser, login, user_name, amount,
                                                 allfollowing, randomize, dont_include,
                                                  blacklist, follow_times, simulation,
                                                   channel, jumps, logger, logfolder)

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

            cur.execute("SELECT * FROM followRestriction WHERE profile_id=:var", {"var": id})
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
            follow_data = {user_data[1]: user_data[2] for user_data in data or []}
            current_data[profile_name] = follow_data

            # dump the fresh follow data to a local human readable JSON
            with open(filename, 'w') as followResFile:
                json.dump(current_data, followResFile)

    except Exception as exc:
        logger.error("Pow! Error occured while dumping follow restriction data to a local JSON:\n\t{}".format(str(exc).encode("utf-8")))

    finally:
        if conn:
            # close the open connection
            conn.close()



def follow_restriction(operation, username, limit, logger):
    """ Keep track of the followed users and help avoid excessive follow of the same user """

    try:
        # get a DB and start a connection
        db, id = get_database()
        conn = sqlite3.connect(db)

        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute("SELECT * FROM followRestriction WHERE profile_id=:id_var AND username=:name_var",
                            {"id_var": id, "name_var": username})
            data = cur.fetchone()
            follow_data = dict(data) if data else None

            if operation == "write":
                if follow_data is None:
                    # write a new record
                    cur.execute("INSERT INTO followRestriction (profile_id, username, times) VALUES (?, ?, ?)",
                                            (id, username, 1))
                else:
                    # update the existing record
                    follow_data["times"] += 1
                    sql = "UPDATE followRestriction set times = ? WHERE profile_id=? AND username = ?"
                    cur.execute(sql, (follow_data["times"], id, username))

                # commit the latest changes
                conn.commit()

            elif operation == "read":
                if follow_data is None:
                    return False

                elif follow_data["times"] < limit:
                    return False

                else:
                    exceed_msg = "" if follow_data["times"] == limit else "more than "
                    logger.info("---> {} has already been followed {}{} times"
                                .format(username, exceed_msg, str(limit)))
                    return True

    except Exception as exc:
        logger.error("Dap! Error occured with follow Restriction:\n\t{}".format(str(exc).encode("utf-8")))

    finally:
        if conn:
            # close the open connection
            conn.close()



def unfollow_user(browser, track, username, person, person_id, button, relationship_data, logger, logfolder):
    """ Unfollow user from either `profile' or a 'post' page or from a 'dialog' box """
    # check action availability
    if quota_supervisor("unfollows") == "jump":
        return False, "jumped"

    # available tracks to unfollow in are `profile`, `post` and `dialog`
    if track in ["profile", "post"]:
        if track == "profile":
            user_link = "https://www.instagram.com/{}/".format(person)
            web_address_navigator(browser, user_link)

        # find out following status
        following, follow_button = get_following_status(browser, person, logger)

        if following is None:
            # check out if the loop has to be broken immidiately
            sirens_wailing, emergency_state = emergency_exit(browser, username, logger)
            if sirens_wailing == True:
                return False, emergency_state

            else:   # there is no any serious issue- loop should continue
                logger.warning("Maybe '{}' has changed the username!\t~verifying through the user ID"
                                    .format(person.encode('utf-8')))
                # try to find the user by ID
                if person_id is None:
                    person_id = load_user_id(username, person, logger, logfolder)

                if person_id:
                    user_link_by_id = ("https://www.instagram.com/web/friendships/{}/follow/"
                                            .format(person_id))
                    web_address_navigator(browser, user_link_by_id)
                    # re-check the following status
                    following, follow_button = get_following_status(browser, person, logger)

                    if following is None:
                        logger.warning("--> Couldn't access the profile page of '{}'!"
                                       "\t~user has either closed the profile or blocked you"
                                            .format(person.encode('utf-8')))
                        post_unfollow_cleanup("uncertain", username, person, relationship_data, logger, logfolder)
                        return False, "user unavailable"

                    else:
                        person_new = get_username(browser, logger)
                        logger.info("User '{}' has changed username and now is called '{}' :S"
                                        .format(person, person_new))
                else:
                    logger.info("--> Couldn't unfollow '{0}'!\t~the user ID of '{0}' "
                                "doesn't exist in local records".format(person))
                    post_unfollow_cleanup("uncertain", username, person, relationship_data, logger, logfolder)
                    return False, "user inaccessible"


        if following in [True, "Requested"]:
            click_element(browser, follow_button)
            sleep(4)
            confirm_unfollow(browser)
            # double check the following state
            follow_button = browser.find_element_by_xpath(
                                "//*[contains(text(), 'Follow')]")
            # if the button still has not changed it can be a temporary block
            if follow_button.text not in ['Follow', 'Follow Back']:
                logger.warning("--> Unfollow error!\t~username '{}' might be blocked from unfollowing\n"
                                   .format(username))
                return False, "shadow ban"


        elif following == False:
            logger.info("--> Couldn't unfollow '{}'!\t~maybe unfollowed before"
                                .format(person.encode('utf-8')))
            post_unfollow_cleanup("uncertain", username, person, relationship_data, logger, logfolder)
            return False, "uncertain"


    elif track == "dialog":
        click_element(browser, button)
        sleep(4)
        confirm_unfollow(browser)


    ## general tasks after a successful unfollow

    logger.info("--> Unfollowed '{}'!".format(person))
    update_activity('unfollows')
    post_unfollow_cleanup("successful", username, person, relationship_data, logger, logfolder)

    return True, "success"



def confirm_unfollow(browser):
    """ Deal with the confirmation dialog boxes during an unfollow """
    attempt = 0

    while attempt<3:
        try:
            button_xp = "//button[text()='Unfollow']"   # "//button[contains(text(), 'Unfollow')]"
            unfollow_button = browser.find_element_by_xpath(button_xp)
            attempt += 1

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



def post_unfollow_cleanup(state, username, person, relationship_data, logger, logfolder):
    """ Casual local data cleaning after an unfollow """
    delete_line_from_file("{0}{1}_followedPool.csv"
                            .format(logfolder, username), person, logger)
    nap = 10 if state == "successful" else 3

    if state == "successful":
        if person in relationship_data[username]["all_following"]:
            relationship_data[username]["all_following"].remove(person)

    if state == "uncertain":
        # this user was found in our unfollow list but currently is not being followed
        log_uncertain_unfollowed_pool(username, person, logger, logfolder)
        # save any unfollowed person
        log_record_all_unfollowed(username, person, logger, logfolder)

    print('')
    sleep(nap)




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
    user_link = "https://www.instagram.com/{}/".format(username)

    if track == "dialog":
        # navigate to the profile page directly in a newly opened tab
        with new_tab(browser):
            web_address_navigator(browser, user_link)
            user_id = find_user_id(browser, track, username, logger)

    else:
        user_id = find_user_id(browser, track, username, logger)

    return user_id



