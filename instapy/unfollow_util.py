"""Module which handles the follow features like unfollowing and following"""
import random
import os
import json
import csv
import time
from datetime import datetime, timedelta
from math import ceil

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from .time_util import sleep
from .util import delete_line_from_file
from .util import scroll_bottom
from .util import format_number
from .util import update_activity
from .util import add_user_to_blacklist
from .util import click_element
from .util import web_adress_navigator
from .util import interruption_handler
from .util import get_relationship_counts
from .print_log_writer import log_followed_pool
from .print_log_writer import log_uncertain_unfollowed_pool
from .print_log_writer import log_record_all_unfollowed
from .relationship_tools import get_followers
from .relationship_tools import get_following
from .relationship_tools import get_nonfollowers



def set_automated_followed_pool(username, unfollow_after, logger, logfolder, pool='followedPool'):
    automatedFollowedPool = {"all":[], "eligible":[]}
    try:
        with open('{0}{1}_{2}.csv'.format(logfolder, username, pool), 'r+') as followedPoolFile:
            reader = csv.reader(followedPoolFile)
            for row in reader:
                if unfollow_after is not None:
                    try:
                        ftime = datetime.strptime(row[0].split(' ~ ')[0], '%Y-%m-%d %H:%M')
                        ftimestamp = (ftime - datetime(1970, 1, 1)).total_seconds()
                        realtimestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
                        fword = row[0].split(' ~ ')[1]
                        if realtimestamp - ftimestamp > unfollow_after:
                            automatedFollowedPool["eligible"].append(fword)
                        automatedFollowedPool["all"].append(fword)
                    except ValueError:
                        fword = row[0]
                        automatedFollowedPool["all"].append(fword)
                        automatedFollowedPool["eligible"].append(fword)
                else:
                    try:
                        fword = row[0].split(' ~ ')[1]
                    except IndexError:
                        fword = row[0]
                    automatedFollowedPool["all"].append(fword)
                    automatedFollowedPool["eligible"].append(fword)

        followedPoolFile.close()

    except BaseException as e:
        logger.error("set_automated_followed_pool error {}".format(str(e)))

    return automatedFollowedPool


def get_following_status(browser, person, logger):

    following = False
    follow_button = None
    try:
        follow_button = browser.find_element_by_xpath(
            "//*[contains(text(), 'Follow')]")
        if follow_button.text == 'Following':
            following = "Following"
        else:
            if follow_button.text in ['Follow', 'Follow Back']:
                following = False
            else:
                follow_button = browser.find_element_by_xpath(
                    "//*[contains(text(), 'Requested')]")
                if follow_button.text == "Requested":
                    following = "Requested"
    except:
        logger.error(
            '--> Unfollow error with {},'
            ' maybe no longer exists...'
                .format(person.encode('utf-8')))

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

    user_link ='https://www.instagram.com/{}/'.format(username)

    #Check URL of the webpage, if it already is the one to be navigated, then do not navigate to it again
    web_adress_navigator(browser, user_link)

    #check how many poeple we are following
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
            unfollow_list = automatedFollowedPool["eligible"]

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

        #pick only the users in the right track- ["all" or "nonfollowers"] for `customList` and `InstapyFollowed` technics
        if customList == True or InstapyFollowed == True:
            if unfollow_track == "nonfollowers":
                all_followers = get_followers(browser, username, "full", relationship_data, False, True, logger, logfolder)
                loyal_users = [user for user in unfollow_list if user in all_followers]
                logger.info("Found {} loyal followers!  ~will not unfollow them".format(len(loyal_users)))
                unfollow_list = [user for user in unfollow_list if user not in loyal_users]

            elif unfollow_track != "all":
                logger.info("Unfollow track is not specified! ~choose \"all\" or \"nonfollowers\"")
                return 0

        #re-generate unfollow list according to the `unfollow_after` parameter for `customList` and `nonFollowers` technics
        if customList == True or nonFollowers == True:
            not_found = []
            non_eligible = []
            for person in unfollow_list:
                if person not in automatedFollowedPool["all"]:
                    not_found.append(person)
                elif (person in automatedFollowedPool["all"] and
                        person not in automatedFollowedPool["eligible"]):
                    non_eligible.append(person)

            unfollow_list = [user for user in unfollow_list if user not in non_eligible]
            logger.info("Total {} users available to unfollow"
                            "  ~not found in 'followedPool.csv': {}  |  didn't pass `unfollow_after`: {}\n".format(
                                len(unfollow_list), len(not_found), len(non_eligible)))

        elif InstapyFollowed == True:
            non_eligible = [user for user in automatedFollowedPool["all"] if user not in automatedFollowedPool["eligible"]]
            logger.info("Total {} users available to unfollow  ~didn't pass `unfollow_after`: {}\n".format(len(unfollow_list), len(non_eligible)))

        if len(unfollow_list) < 1:
            logger.info("There are no any users available to unfollow")
            return 0

        #choose the desired order of the elements
        if style == "LIFO":
            unfollow_list = list(reversed(unfollow_list))
        elif style == "RANDOM":
            random.shuffle(unfollow_list)

        if amount > len(unfollow_list):
            logger.info("You have requested more amount: {} than {} of users available to unfollow  ~using available amount".format(
                                amount, len(unfollow_list)))
            amount = len(unfollow_list)

        # unfollow loop
        try:
            sleep_counter = 0
            sleep_after = random.randint(8, 12)

            for person in unfollow_list:
                if unfollowNum >= amount:
                    logger.warning(
                        "--> Total unfollows reached it's amount given {}\n"
                        .format(unfollowNum))
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
                    browser.get('https://www.instagram.com/' + person)
                    sleep(2)

                    try:
                        following, follow_button = get_following_status(browser, person, logger)
                    except:
                        logger.error(
                            '--> Unfollow error with {},'
                            ' maybe no longer exists...'
                                .format(person.encode('utf-8')))
                        delete_line_from_file('{0}{1}_followedPool.csv'.format(logfolder, username), person + ",\n", logger)

                        continue

                    if following:
                        # click the button
                        click_element(browser, follow_button) # follow_button.click()
                        sleep(4)

                        try:
                            browser.find_element_by_xpath("//button[contains(text(), 'Unfollow')]").click()
                            sleep(4)
                        except Exception:
                            pass

                        # double check not following
                        follow_button = browser.find_element_by_xpath(
                            "//*[contains(text(), 'Follow')]")

                        if follow_button.text in ['Follow','Follow Back']:

                            unfollowNum += 1
                            sleep_counter += 1

                            update_activity('unfollows')

                            if person in relationship_data[username]["all_following"]:
                                relationship_data[username]["all_following"].remove(person)

                            logger.info(
                                '--> Ongoing Unfollow From InstaPy {}/{},'
                                ' now unfollowing: {}'
                                .format(str(unfollowNum), amount, person.encode('utf-8')))

                            delete_line_from_file('{0}{1}_followedPool.csv'.format(logfolder, username), person +
                                              ",\n", logger)

                            print('')
                            sleep(15)

                        else:
                            logger.error("Unfollow error!  ~username {} might be blocked\n".format(username))
                            # stop the loop
                            break
                    else:
                        # this user found in our list of unfollow but is not followed
                        if follow_button is None or follow_button.text not in ['Follow', 'Follow Back']:
                            log_uncertain_unfollowed_pool(username, person, logger, logfolder)
                        # check we are now logged in
                        valid_connection = browser.execute_script(
                            "return window._sharedData.""activity_counts")
                        if not valid_connection:
                            # if no valid connection
                            msg = '--> user:{} have no valid_connection wait 3600'.format(person)
                            logger.warning(msg)
                            break


                        # save any unfollowed person
                        log_record_all_unfollowed(username, person, logger, logfolder)

                        logger.warning(
                            "--> Cannot Unfollow From InstaPy {}"
                            ", maybe {} was unfollowed before..."
                            .format(str(unfollowNum), person.encode('utf-8')))

                        delete_line_from_file('{0}{1}_followedPool.csv'.format(logfolder, username),
                                              person + ",\n", logger)

                        print('')
                        sleep(2)
                else:
                    # if the user in dont include (should not be) we shall remove him from the follow list
                    # if he is a white list user (set at init and not during run time)
                    if person in white_list:
                        delete_line_from_file('{0}{1}_followedPool.csv'.format(logfolder, username),
                                              person + ",\n", logger)
                        list_type = 'whitelist'
                    else:
                        list_type = 'dont_include'
                    logger.info("Not unfollowing '{}'!  ~user is in the list {}\n".format(person, list_type))
                    continue

        except BaseException as e:
            logger.error("Unfollow loop error:  {}\n".format(str(e)))

    elif allFollowing == True:
        logger.info("Unfollowing the users you are following")
        # unfollow from profile
        try:
            following_link = browser.find_elements_by_xpath(
                '//section//ul//li[3]')

            click_element(browser, following_link[0]) # following_link[0].click()
            # update server calls
            update_activity()
        except BaseException as e:
            logger.error("following_link error {}".format(str(e)))
            return 0

        #scroll down the page to get sufficient amount of usernames
        get_users_through_dialog(browser, None, username, amount,
                                     allfollowing, False, None,
                                      None, None, None,
                                       False, "Unfollow", logger, logfolder)

        # find dialog box
        dialog = browser.find_element_by_xpath(
            "//div[text()='Following']/following-sibling::div")
        sleep(3)

        # get persons, unfollow buttons, and length of followed pool
        person_list_a = dialog.find_elements_by_tag_name("a")
        person_list = []

        for person in person_list_a:

            if person and hasattr(person, 'text') and person.text:
                person_list.append(person.text)

        follow_buttons = dialog.find_elements_by_tag_name('button')

        #re-generate person list to unfollow according to the `unfollow_after` parameter
        user_info = list(zip(follow_buttons, person_list))
        non_eligible = []
        not_found = []

        for button, person in user_info:
            if person not in automatedFollowedPool["all"]:
                not_found.append(person)
            elif (person in automatedFollowedPool["all"] and
                    person not in automatedFollowedPool["eligible"]):
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

                if (unfollowNum != 0 and
                        hasSlept is False and
                            unfollowNum % 10 == 0):
                    logger.info('sleeping for about {}min'
                                .format(int(sleep_delay/60)))
                    sleep(sleep_delay)
                    hasSlept = True
                    pass

                if person not in dont_include:
                    unfollowNum += 1
                    click_element(browser, button) # button.click()
                    sleep(4)

                    try:
                        browser.find_element_by_xpath("//button[contains(text(), 'Unfollow')]").click()
                        sleep(4)
                    except Exception:
                        pass

                    update_activity('unfollows')

                    if person in relationship_data[username]["all_following"]:
                        relationship_data[username]["all_following"].remove(person)

                    logger.info(
                        '--> Ongoing Unfollow {}/{}, now unfollowing: {}'
                        .format(str(unfollowNum), amount, person.encode('utf-8')))

                    delete_line_from_file('{0}{1}_followedPool.csv'.format(logfolder, username), person +
                                      ",\n", logger)

                    print('')
                    sleep(15)
                    # To only sleep once until there is the next unfollow
                    if hasSlept:
                        hasSlept = False

                    continue

                else:
                    logger.info("Not unfollowing '{}'!  ~user is in the whitelist\n".format(person))
                    continue

        except Exception as exc:
            logger.error("Unfollow loop error:\n\n{}\n\n".format(exc.encode('utf-8')))

    else:
        logger.info("Please select a proper unfollow method!  ~leaving unfollow activity\n")

    return unfollowNum


def follow_user(browser, follow_restrict, login, user_name, blacklist, logger, logfolder):
    """Follows the user of the currently opened image"""
    follow_xpath =  "//button[text()='Follow']"
    try:
        sleep(2)
        follow_button = browser.find_element_by_xpath(follow_xpath)

        if follow_button.is_displayed():
            click_element(browser, follow_button) # follow_button.click()
        else:
            browser.execute_script(
                "arguments[0].style.visibility = 'visible'; "
                "arguments[0].style.height = '10px'; "
                "arguments[0].style.width = '10px'; "
                "arguments[0].style.opacity = 1", follow_button)
            click_element(browser, follow_button) # follow_button.click()
        update_activity('follows')

        logger.info('--> Now following')
        logtime = datetime.now().strftime('%Y-%m-%d %H:%M')
        log_followed_pool(login, user_name, logger, logfolder, logtime)
        follow_restrict[user_name] = follow_restrict.get(user_name, 0) + 1
        if blacklist['enabled'] is True:
            action = 'followed'
            add_user_to_blacklist(
                user_name, blacklist['campaign'], action, logger, logfolder
            )
        sleep(3)
        return 1
    except NoSuchElementException:
        logger.info('--> Already following')
        sleep(1)
        return 0
    except StaleElementReferenceException:
        # https://stackoverflow.com/questions/16166261/selenium-webdriver-how-to-resolve-stale-element-reference-exception
        # 1. An element that is found on a web page referenced as a WebElement in WebDriver then the DOM changes
        # (probably due to JavaScript functions) that WebElement goes stale.
        # 2. The element has been deleted entirely.
        logger.error('--> element that is found on a web page referenced  while the DOM changes')
        sleep(1)
        return 0


def unfollow_user(browser, username, person, relationship_data, logger, logfolder):
    """Unfollows the user of the currently opened image"""

    try:
        unfollow_button = browser.find_element_by_xpath(
            "//*[text()='Following' or text()='Requested']")
            #"//*[contains(text(), 'Following')]")  # or Requested
    except NoSuchElementException:
        logger.error("Could not locate \"Following\" or \"Requested\" button in order to unfollow '{}'!".format(person))
        return 0

    if unfollow_button.text in ['Following', 'Requested']:
        click_element(browser, unfollow_button) # unfollow_button.send_keys("\n")
        logger.warning("--> Unfollowed '{}' due to Inappropriate Content".format(person))

        delete_line_from_file('{0}{1}_followedPool.csv'.format(logfolder, username), person +
                          ",\n", logger)

        if person in relationship_data[username]["all_following"]:
            relationship_data[username]["all_following"].remove(person)

        update_activity('unfollows')
        sleep(3)

        return 1


def follow_given_user(browser,
                      login,
                      acc_to_follow,
                      follow_restrict,
                      blacklist,
                      logger,
                      logfolder):
    """Follows a given user"""
    user_link = "https://www.instagram.com/{}/".format(acc_to_follow)

    #Check URL of the webpage, if it already is user's profile page, then do not navigate to it again
    web_adress_navigator(browser, user_link)

    logger.info('--> {} instagram account is opened...'.format(acc_to_follow))

    try:
        sleep(10)
        follow_button = browser.find_element_by_xpath("//*[text()='Follow']")
        click_element(browser, follow_button) # unfollow_button.send_keys("\n")
        update_activity('follows')
        logger.info('---> Now following: {}'.format(acc_to_follow))
        logtime = datetime.now().strftime('%Y-%m-%d %H:%M')
        log_followed_pool(login, acc_to_follow, logger, logfolder, logtime)
        follow_restrict[acc_to_follow] = follow_restrict.get(
            acc_to_follow, 0) + 1

        if blacklist['enabled'] is True:
            action = 'followed'
            add_user_to_blacklist(
                acc_to_follow, blacklist['campaign'], action, logger, logfolder
            )

        sleep(3)
        return 1
    except NoSuchElementException:
        logger.warning('---> {} is already followed'.format(acc_to_follow))
        sleep(3)
        return 0


def get_users_through_dialog(browser,
                          login,
                          user_name,
                          amount,
                          users_count,
                          randomize,
                          dont_include,
                          follow_restrict,
                          blacklist,
                          follow_times,
                          simulation,
                          channel,
                          logger,
                          logfolder):
    sleep(2)
    person_followed = []
    real_amount = amount
    if randomize and amount >= 3:
        # expanding the popultaion for better sampling distribution
        amount = amount * 3

    if amount > int(users_count*0.85):   #taking 85 percent of possible amounts is a safe study
        amount = int(users_count*0.85)
    try_again = 0
    sc_rolled = 0

    # find dialog box
    dialog = browser.find_element_by_xpath(
      "//div[text()='Followers' or text()='Following']/following-sibling::div")

    if channel == "Follow":
        # get follow buttons. This approach will find the follow buttons and
        # ignore the Unfollow/Requested buttons.
        buttons = dialog.find_elements_by_xpath(
            "//div/div/span/button[text()='Follow']")

    elif channel == "Unfollow":
        buttons = dialog.find_elements_by_xpath(
            "//div/div/span/button[text()='Following']")

    abort = False
    person_list = []
    total_list = len(buttons)
    simulated_list = []
    simulator_counter = 0

    # scroll down if the generated list of user to follow is not enough to
    # follow amount set
    while (total_list < amount) and not abort:
        before_scroll = total_list
        for i in range(3):
            scroll_bottom(browser, dialog, 2)
            sc_rolled += 1
            simulator_counter += 1

        if channel == "Follow":
            buttons = dialog.find_elements_by_xpath(
                "//div/div/span/button[text()='Follow']")

        elif channel == "Unfollow":
            buttons = dialog.find_elements_by_xpath(
                "//div/div/span/button[text()='Following']")

        total_list = len(buttons)
        abort = (before_scroll == total_list)
        if abort:
            if total_list < real_amount:
                logger.info("Failed to load desired amount of users")

        if sc_rolled > 85:   #you may want to use up to 100
            if total_list < amount:
                logger.info("Too many requests sent!  attempt: {}  |  gathered links: {}   ~sleeping a bit  ".format(try_again+1, total_list))
                sleep(random.randint(600, 655))
                try_again += 1
                sc_rolled = 0

        # Will follow a little bit of users in order to simulate real interaction
        if (simulation == True and
               (simulator_counter > random.randint(5, 17) or
                    abort == True or
                        total_list >= amount or
                            sc_rolled == random.randint(3, 5)) and
                                len(buttons) > 0):

            quick_amount = 1 if not total_list >= amount else random.randint(1, 4)

            for i in range(0, quick_amount):
                logger.info("Simulated follow : {}".format(len(simulated_list)+1))

                quick_index = random.randint(0, len(buttons)-1)
                quick_button = buttons[quick_index]
                quick_username = dialog_username_extractor(quick_button)
                if quick_username[0] not in simulated_list:
                    quick_follow = follow_through_dialog(browser,
                                                         login,
                                                         quick_username,
                                                         quick_button,
                                                         quick_amount,
                                                         dont_include,
                                                         follow_restrict,
                                                         blacklist,
                                                         follow_times,
                                                         logger,
                                                         logfolder)
                    simulated_list.extend(quick_follow)

            simulator_counter = 0

    person_list = dialog_username_extractor(buttons)
    if randomize:
        random.shuffle(person_list)

    person_list = person_list[:(real_amount-len(simulated_list))]

    for user in simulated_list:   #add simulated users to the `person_list` in random index
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
                          follow_restrict,
                          blacklist,
                          follow_times,
                          logger,
                          logfolder):
    """ Will follow username directly inside a dialog box """
    if not isinstance(person_list, list):
        person_list = [person_list]

    if not isinstance(buttons, list):
        buttons = [buttons]

    person_followed = []
    try:
        for person, button in zip(person_list, buttons):

            if (person not in dont_include and
                follow_restrict.get(person, 0) < follow_times):

                # Register this session's followed user for further interaction
                person_followed.append(person)

                click_element(browser, button)
                sleep(1)
                logtime = datetime.now().strftime('%Y-%m-%d %H:%M')
                log_followed_pool(login, person, logger, logfolder, logtime)

                update_activity('follows')

                follow_restrict[person] = follow_restrict.get(person, 0) + 1

                logger.info('--> Followed {}'.format(person.encode('utf-8')))

                if blacklist['enabled'] is True:
                    action = 'followed'
                    add_user_to_blacklist(
                        person, blacklist['campaign'], action, logger, logfolder
                    )

                sleep(3)

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
                                follow_restrict,
                                blacklist,
                                follow_times,
                                simulation,
                                logger,
                                logfolder):
    """
    For the given username, follow their followers.

    :param browser: webdriver instance
    :param login:
    :param user_name: given username of account to follow
    :param amount: the number of followers to follow
    :param dont_include: ignore these usernames
    :param follow_restrict:
    :param random: randomly select from users' followers
    :param blacklist:
    :param follow_times:
    :param logger: the logger instance
    :param logfolder: the logger folder
    :return: list of user's followers also followed
    """
    user_name = user_name.strip()

    browser.get('https://www.instagram.com/{}/'.format(user_name))
    update_activity()

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
                    allfollowers = format_number(browser.find_elements_by_xpath(
                        "//span[contains(@class,'g47SY')]")[1].text)
                except NoSuchElementException:
                    logger.error("Error occured during getting the followers count of '{}'\n".format(user_name))
                    return [], []

    # skip early for no followers
    if not allfollowers:
        logger.info('{} has no followers'.format(user_name))
        return [], []

    elif allfollowers < amount:
        logger.warning('{} has less followers than given amount of {}'.format(
            allfollowers, amount))

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
                                                  follow_restrict, blacklist, follow_times,
                                                   simulation, channel, logger, logfolder)

    return person_list, simulated_list


def get_given_user_following(browser,
                                login,
                                user_name,
                                amount,
                                dont_include,
                                randomize,
                                follow_restrict,
                                blacklist,
                                follow_times,
                                simulation,
                                logger,
                                logfolder):
    user_name = user_name.strip()

    browser.get('https://www.instagram.com/{}/'.format(user_name))
    # update server calls
    update_activity()

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
                    allfollowing = format_number(browser.find_elements_by_xpath(
                        "//span[contains(@class,'g47SY')]")[2].text)
                except NoSuchElementException:
                    logger.error("\nError occured during getting the following count of '{}'\n".format(user_name))
                    return [], []

    # skip early for no followers
    if not allfollowing:
        logger.info('{} has no any following'.format(user_name))
        return [], []

    elif allfollowing < amount:
        logger.warning('{} has less following than given amount of {}'.format(
            allfollowing, amount))

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
                                                  follow_restrict, blacklist, follow_times,
                                                   simulation, channel, logger, logfolder)

    return person_list, simulated_list


def dump_follow_restriction(followRes, logfolder):
    """Dumps the given dictionary to a file using the json format"""
    filename = '{}followRestriction.json'.format(logfolder)

    with open(filename, 'w') as followResFile:
        json.dump(followRes, followResFile)


def load_follow_restriction(logfolder):
    """Loads the saved """
    filename = '{}followRestriction.json'.format(logfolder)

    if not os.path.isfile(filename):
        data = {}
        with open(filename,'w+') as followResFile:
            json.dump(data, followResFile)
            followResFile.close()

    with open(filename) as followResFile:
        return json.load(followResFile)
