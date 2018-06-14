"""Module which handles the follow features like unfollowing and following"""
import json
import csv
from datetime import datetime, timedelta
from .time_util import sleep
from .util import delete_line_from_file
from .util import scroll_bottom
from .util import format_number
from .util import update_activity
from .util import add_user_to_blacklist
from .util import click_element
from .util import web_adress_navigator
from .print_log_writer import log_followed_pool
from .print_log_writer import log_uncertain_unfollowed_pool
from .print_log_writer import log_record_all_unfollowed
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
import random
import os
from selenium.common.exceptions import StaleElementReferenceException
from random import randint

def set_automated_followed_pool(username, logger, logfolder, unfollow_after):
    automatedFollowedPool = []
    try:
        with open('{0}{1}_followedPool.csv'.format(logfolder, username), 'r+') as followedPoolFile:
            reader = csv.reader(followedPoolFile)
            for row in reader:
                if unfollow_after is not None:
                    try:
                        ftime = datetime.strptime(row[0].split(' ~ ')[0], '%Y-%m-%d %H:%M')
                        ftimestamp = (ftime - datetime(1970, 1, 1)).total_seconds()
                        realtimestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
                        if realtimestamp - ftimestamp > unfollow_after:
                            fword = row[0].split(' ~ ')[1]
                            automatedFollowedPool.append(fword)
                    except ValueError:
                        fword = row[0]
                        automatedFollowedPool.append(fword)
                else:
                    try:
                        fword = row[0].split(' ~ ')[1]
                    except IndexError:
                        fword = row[0]
                    automatedFollowedPool.append(fword)

        logger.info("Number of users available to unfollow: {}"
                    .format(len(automatedFollowedPool)))

        followedPoolFile.close()

    except BaseException as e:
        logger.error("set_automated_followed_pool error {}".format(str(e)))

    return automatedFollowedPool


def unfollow(browser,
             username,
             amount,
             dont_include,
             onlyInstapyFollowed,
             onlyInstapyMethod,
             automatedFollowedPool,
             sleep_delay,
             onlyNotFollowMe,
             logger,
             logfolder):

    """unfollows the given amount of users"""
    unfollowNum = 0

    user_link ='https://www.instagram.com/{}/'.format(username)

    #Check URL of the webpage, if it already is the one to be navigated, then do not navigate to it again
    web_adress_navigator(browser, user_link)

    #  check how many poeple we are following
    #  throw RuntimeWarning if we are 0 people following
    try:
        allfollowing = format_number(
            browser.find_element_by_xpath('//li[3]/a/span').text)
    except NoSuchElementException:
        logger.warning('There are 0 people to unfollow')

    automatedFollowedPoolLength = len(automatedFollowedPool)

    if onlyInstapyFollowed is True:
        # Unfollow only instapy followed
        if onlyInstapyMethod == 'LIFO':
            automatedFollowedPool = list(reversed(automatedFollowedPool))

        # unfollow loop
        try:
            hasSlept = False
            for person in automatedFollowedPool:
                if unfollowNum >= amount:
                    logger.warning(
                        "--> Total unfollowNum reached it's amount given {}"
                        .format(unfollowNum))
                    break

                if unfollowNum >= automatedFollowedPoolLength:
                    logger.warning(
                        "--> Total unfollowNum exeeded the pool of automated"
                        "followed {}".format(unfollowNum))
                    break

                if unfollowNum != 0 and \
                   hasSlept is False and \
                   unfollowNum % 10 == 0:
                        logger.warning('sleeping for about {}min'
                                       .format(int(sleep_delay/60)))
                        sleep(sleep_delay)
                        hasSlept = True
                        pass

                if person not in dont_include:
                    browser.get('https://www.instagram.com/' + person)
                    sleep(2)

                    following = False
                    try:
                        try:
                            follow_button = browser.find_element_by_xpath(
                                "//*[contains(text(), 'Follow')]")
                        except NoSuchElementException:
                            follow_button = browser.find_element_by_xpath(
                                '''//*[@id="react-root"]/section/main/article/header/section/div[1]/span/span[1]/button''')
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

                    if following:
                        # click the button
                        click_element(browser, follow_button) # follow_button.click()
                        sleep(4)

                        # double check not following
                        follow_button = browser.find_element_by_xpath(
                            "//*[contains(text(), 'Follow')]")

                        if follow_button.text in ['Follow','Follow Back']:

                            unfollowNum += 1
                            update_activity('unfollows')

                            delete_line_from_file('{0}{1}_followedPool.csv'.format(logfolder, username), person +
                                              ",\n", logger)

                            logger.info(
                                '--> Ongoing Unfollow From InstaPy {},'
                                ' now unfollowing: {}'
                                .format(str(unfollowNum), person.encode('utf-8')))

                            sleep(15)

                            if hasSlept:
                                hasSlept = False
                            continue
                        else:
                            logger.error("unfollow error username {} might be blocked ".format(username))
                            # stop the loop
                            break
                    else:
						# this user found in our list of unfollow but is not followed
                        if follow_button.text != 'Follow':
                            log_uncertain_unfollowed_pool(username, person, logger, logfolder)
                        # check we are now logged in
                        valid_connection = browser.execute_script(
                            "return window._sharedData.""activity_counts")
                        if not valid_connection:
                            # if no valid connection
                            msg = '--> user:{} have no valid_connection wait 3600'.format(person)
                            logger.warning(msg)
                            break

                        delete_line_from_file('{0}{1}_followedPool.csv'.format(logfolder, username),
                                              person + ",\n", logger)
                        # save any unfollowed person
                        log_record_all_unfollowed(username, person, logger, logfolder)

                        logger.warning(
                            '--> Cannot Unfollow From InstaPy {}'
                            ', now unfollowing: {}'
                            .format(str(unfollowNum), person.encode('utf-8')))
                        sleep(2)
                else:
                    # if the user in dont include (should not be) we shall remove him from the follow list
                    delete_line_from_file('{0}{1}_followedPool.csv'.format(logfolder, username),
                                          person + ",\n", logger)
                    logger.warning('This person in dont include but better not be')

        except BaseException as e:
            logger.error("unfollow loop error {}".format(str(e)))

    elif onlyInstapyFollowed is False and onlyNotFollowMe is True:
        # unfollow only not follow me
        user_data = {}

        graphql_endpoint = 'https://www.instagram.com/graphql/query/'
        graphql_followers = (
                graphql_endpoint + '?query_hash=37479f2b8209594dde7facb0d904896a')
        graphql_following = (
                graphql_endpoint + '?query_hash=58712303d941c6855d4e888c5f0cd22f')

        all_followers = []
        all_following = []

        variables = {}
        user_data['id'] = browser.execute_script(
            "return window._sharedData.entry_data.ProfilePage[0]."
            "graphql.user.id")
        variables['id'] = user_data['id']
        variables['first'] = 50

        # get follower and following user loop
        try:
            for i in range(0, 2):
                has_next_data = True

                url = (
                    '{}&variables={}'
                    .format(graphql_followers, str(json.dumps(variables)))
                )
                if i != 0:
                    if 'after' in variables:
                        del variables['after']
                    url = (
                        '{}&variables={}'
                        .format(graphql_following, str(json.dumps(variables)))
                    )
                sleep(2)
                browser.get(url)

                # fetch all user while still has data
                while has_next_data:
                    pre = browser.find_element_by_tag_name("pre").text
                    data = json.loads(pre)['data']

                    if i == 0:
                        # get followers
                        page_info = (
                            data['user']['edge_followed_by']['page_info'])
                        edges = data['user']['edge_followed_by']['edges']
                        for user in edges:
                            all_followers.append(user['node']['username'])
                    elif i == 1:
                        # get following
                        page_info = (
                            data['user']['edge_follow']['page_info'])
                        edges = data['user']['edge_follow']['edges']
                        for user in edges:
                            all_following.append(user['node']['username'])

                    has_next_data = page_info['has_next_page']
                    if has_next_data:
                        variables['after'] = page_info['end_cursor']

                        url = (
                            '{}&variables={}'
                            .format(
                                graphql_followers, str(json.dumps(variables)))
                        )
                        if i != 0:
                            url = (
                                '{}&variables={}'
                                .format(
                                    graphql_following,
                                    str(json.dumps(variables))
                                )
                            )
                        sleep(2)
                        browser.get(url)
        except BaseException as e:
            logger.error(
                "unable to get followers and following information \n", str(e))

        # make sure to unfollow users who don't follow back and don't
        # unfollow whitelisted users
        unfollow_list = (
            set(all_following) - set(all_followers) - set(dont_include))

        # unfollow loop
        try:
            hasSlept = False
            for person in unfollow_list:
                if unfollowNum >= amount:
                    logger.info("--> Total unfollowNum reached it's amount "
                          "given {}".format(unfollowNum))
                    break

                if (unfollowNum != 0 and
                   hasSlept is False and
                   unfollowNum % 10 == 0):

                        logger.info('sleeping for about {}min'
                              .format(int(sleep_delay/60)))
                        sleep(sleep_delay)
                        hasSlept = True

                browser.get('https://www.instagram.com/{}'.format(person))
                sleep(2)
                follow_button = browser.find_element_by_xpath(
                    "//*[contains(text(), 'Follow')]")

                if follow_button.text == 'Following':
                    unfollowNum += 1
                    click_element(browser, follow_button) # follow_button.click()
                    logger.info('--> Ongoing Unfollow ' + str(unfollowNum) +
                          ', now unfollowing: {}'
                          .format(person.encode('utf-8')))
                    sleep(15)
                    if hasSlept:
                        hasSlept = False

        except BaseException as e:
            logger.error("unfollow loop error \n", str(e))

    elif onlyNotFollowMe is not True:
        # unfollow from profile
        try:
            following_link = browser.find_elements_by_xpath(
                '//section//ul//li[3]')

            click_element(browser, following_link[0]) # following_link[0].click()
            # update server calls
            update_activity()
        except BaseException as e:
            logger.error("following_link error {}".format(str(e)))

        sleep(2)

        # find dialog box
        dialog = browser.find_element_by_xpath(
            "//div[text()='Following']/following-sibling::div")

        # scroll down the page
        scroll_bottom(browser, dialog, allfollowing)

        # get persons, unfollow buttons, and length of followed pool
        person_list_a = dialog.find_elements_by_tag_name("a")
        person_list = []

        for person in person_list_a:

            if person and hasattr(person, 'text') and person.text:
                person_list.append(person.text)

        follow_buttons = dialog.find_elements_by_tag_name('button')

        # unfollow loop
        try:
            hasSlept = False

            for button, person in zip(follow_buttons, person_list):
                if unfollowNum >= amount:
                    logger.info(
                        "--> Total unfollowNum reached it's amount given: {}"
                        .format(unfollowNum))
                    break

                if unfollowNum != 0 and \
                   hasSlept is False and \
                   unfollowNum % 10 == 0:
                        logger.info('sleeping for about {}min'
                                    .format(int(sleep_delay/60)))
                        sleep(sleep_delay)
                        hasSlept = True
                        pass

                if person not in dont_include:
                    unfollowNum += 1
                    click_element(browser, button) # button.click()
                    update_activity('unfollows')

                    logger.info(
                        '--> Ongoing Unfollow {}, now unfollowing: {}'
                        .format(str(unfollowNum), person.encode('utf-8')))
                    sleep(15)
                    # To only sleep once until there is the next unfollow
                    if hasSlept:
                        hasSlept = False

                    continue
                else:
                    continue

        except BaseException as e:
            logger.error("unfollow loop error {}".format(str(e)))

    return unfollowNum


def follow_user(browser, follow_restrict, login, user_name, blacklist, logger, logfolder):

    sleepSeconds = randint(30, 60)
    logger.info("follow_user: Going to sleep for %s seconds before following", sleepSeconds)
    sleep(sleepSeconds)

    """Follows the user of the currently opened image"""
    follow_xpath =  "//button[text()='Follow']"
    try:
        sleep(2)
        follow_button = browser.find_element_by_xpath(follow_xpath)

        if follow_button.is_displayed():
            click_element(browser, follow_button) # follow_button.click()
            update_activity('follows')
        else:
            browser.execute_script(
                "arguments[0].style.visibility = 'visible'; "
                "arguments[0].style.height = '10px'; "
                "arguments[0].style.width = '10px'; "
                "arguments[0].style.opacity = 1", follow_button)
            click_element(browser, follow_button) # follow_button.click()
            update_activity('follows')


        logtime = datetime.now().strftime('%Y-%m-%d %H:%M')
        log_followed_pool(login, user_name, logger, logfolder, logtime)
        follow_restrict[user_name] = follow_restrict.get(user_name, 0) + 1
        if blacklist['enabled'] is True:
            action = 'followed'
            add_user_to_blacklist(
                browser, user_name, blacklist['campaign'], action, logger, logfolder
            )
        sleep(3)
        logger.info('follow_user: Followed user %s', user_name)
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


def unfollow_user(browser, username, person, logger, logfolder):
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
                browser, acc_to_follow, blacklist['campaign'], action, logger, logfolder
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

    # get follow buttons. This approch will find the follow buttons and
    # ignore the Unfollow/Requested buttons.
    follow_buttons = dialog.find_elements_by_xpath(
        "//div/div/span/button[text()='Follow']")

    abort = False
    person_list = []
    total_list = len(follow_buttons)
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
            sleep(random.randint(1, 2))

        follow_buttons = dialog.find_elements_by_xpath(
            "//div/div/span/button[text()='Follow']")
        total_list = len(follow_buttons)

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
        if (simulator_counter > random.randint(5, 17) or
                abort==True or
                    total_list >= amount or
                        sc_rolled==random.randint(3, 5)):

            quick_amount = 1 if not total_list >= amount else random.randint(1, 4)

            for i in range(0, quick_amount):
                logger.info("Simulated follow : {}".format(len(simulated_list)+1))

                quick_index = random.randint(0, len(follow_buttons)-1)
                quick_button = follow_buttons[quick_index]
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

    person_list = dialog_username_extractor(follow_buttons)
    if randomize:
        random.shuffle(person_list)

    person_list = person_list[:(real_amount-len(simulated_list))]
    for user in simulated_list:   #add simulated users to the `person_list` in random index
        if user not in person_list:
            person_list.insert(random.randint(0, len(person_list)-1), user)

    return person_list, simulated_list


def dialog_username_extractor(follow_buttons):
    """ Extract username of a follow button from a dialog box """
    
    if not isinstance(follow_buttons, list):
        follow_buttons = [follow_buttons]
    
    person_list = []
    for person in follow_buttons:

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
                        browser, person, blacklist['campaign'], action, logger, logfolder
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
        allfollowers = format_number(browser.find_element_by_xpath(
            '//li[2]/a/span').text)

    except NoSuchElementException:
        # todo check if private account?
        logger.error('Could not determine if {} has followers'.format(user_name))
        return []

    # skip early for no followers
    if not allfollowers:
        logger.info('{} has no followers'.format(user_name))
        return []

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
        return []

    except BaseException as e:
        logger.error("`followers_link` error {}".format(str(e)))
        return []

    person_list, simulated_list = get_users_through_dialog(browser, login, user_name, amount,
                                                 allfollowers, randomize, dont_include,
                                                  follow_restrict, blacklist, follow_times,
                                                   logger, logfolder)

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
                                logger,
                                logfolder):
    user_name = user_name.strip()

    browser.get('https://www.instagram.com/{}/'.format(user_name))
    # update server calls
    update_activity()

    #  check how many poeple are following this user.
    #  throw RuntimeWarning if we are 0 people following this user
    try:
        allfollowing = format_number(
            browser.find_element_by_xpath("//li[3]/a/span").text)

    except NoSuchElementException:
        logger.error('Could not determine if {} has any following'.format(user_name))
        return []

    # skip early for no followers
    if not allfollowing:
        logger.info('{} has no any following'.format(user_name))
        return []

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
        return []

    except BaseException as e:
        logger.error("`following_link` error {}".format(str(e)))
        return []

    person_list, simulated_list = get_users_through_dialog(browser, login, user_name, amount,
                                                 allfollowing, randomize, dont_include,
                                                  follow_restrict, blacklist, follow_times,
                                                   logger, logfolder)

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

