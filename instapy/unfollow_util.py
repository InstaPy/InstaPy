"""Module which handles the follow features like unfollowing and following"""
import json
import csv
from .time_util import sleep
from .util import delete_line_from_file
from .util import scroll_bottom
from .util import formatNumber
from .util import update_activity
from .util import add_user_to_blacklist
from .print_log_writer import log_followed_pool
from selenium.common.exceptions import NoSuchElementException
import random


def set_automated_followed_pool(username, logger):
    automatedFollowedPool = []
    try:
        with open('./logs/' + username + '_followedPool.csv') as \
                followedPoolFile:
            reader = csv.reader(followedPoolFile)
            automatedFollowedPool = [row[0] for row in reader]

        logger.info("Number of people followed automatically remaining: {}"
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
             logger):

    """unfollows the given amount of users"""
    unfollowNum = 0

    browser.get('https://www.instagram.com/' + username)
    # update server calls
    update_activity()

    #  check how many poeple we are following
    #  throw RuntimeWarning if we are 0 people following
    try:
        allfollowing = formatNumber(
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
                        continue

                if person not in dont_include:
                    browser.get('https://www.instagram.com/' + person)
                    sleep(2)
                    follow_button = browser.find_element_by_xpath(
                        "//*[contains(text(), 'Follow')]")

                    if follow_button.text == 'Following':
                        unfollowNum += 1
                        follow_button.click()
                        update_activity('unfollows')

                        delete_line_from_file('./logs/' + username +
                                              '_followedPool.csv', person +
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
                        delete_line_from_file('./logs/' + username +
                                              '_followedPool.csv',
                                              person + ",\n", logger)

                        logger.warning(
                            '--> Cannot Unfollow From InstaPy {}'
                            ', now unfollowing: {}'
                            .format(str(unfollowNum), person.encode('utf-8')))
                        sleep(2)

        except BaseException as e:
            logger.error("unfollow loop error {}".format(str(e)))

    elif onlyInstapyFollowed is False and onlyNotFollowMe is True:
        # unfollow only not follow me
        try:
            browser.get(
                'https://www.instagram.com/' + username + '/?__a=1')
            pre = browser.find_element_by_tag_name("pre").text
            user_data = json.loads(pre)['user']
        except BaseException as e:
            print("unable to get user information\n", str(e))

        graphql_endpoint = 'https://www.instagram.com/graphql/query/'
        graphql_followers = (
            graphql_endpoint + '?query_id=17851374694183129')
        graphql_following = (
            graphql_endpoint + '?query_id=17874545323001329')

        all_followers = []
        all_following = []

        variables = {}
        variables['id'] = user_data['id']
        variables['first'] = 100

        # get follower and following user loop
        try:
            for i in range(0, 2):
                has_next_data = True

                url = (
                    '{}&variables={}'
                    .format(graphql_followers, str(json.dumps(variables)))
                )
                if i != 0:
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
            print(
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
                    print("--> Total unfollowNum reached it's amount "
                          "given {}".format(unfollowNum))
                    break

                if (unfollowNum != 0 and
                   hasSlept is False and
                   unfollowNum % 10 == 0):

                        print('sleeping for about {}min'
                              .format(int(sleep_delay/60)))
                        sleep(sleep_delay)
                        hasSlept = True

                browser.get('https://www.instagram.com/{}'.format(person))
                sleep(2)
                follow_button = browser.find_element_by_xpath(
                    "//*[contains(text(), 'Follow')]")

                if follow_button.text == 'Following':
                    unfollowNum += 1
                    follow_button.click()
                    print('--> Ongoing Unfollow ' + str(unfollowNum) +
                          ', now unfollowing: {}'
                          .format(person.encode('utf-8')))
                    sleep(15)
                    if hasSlept:
                        hasSlept = False

        except BaseException as e:
            print("unfollow loop error \n", str(e))

    elif onlyNotFollowMe is not True:
        # unfollow from profile
        try:
            following_link = browser.find_elements_by_xpath(
                '//article//ul//li[3]')
            following_link[0].click()
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
                        continue

                if person not in dont_include:
                    unfollowNum += 1
                    button.click()
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


def follow_user(browser, follow_restrict, login, user_name, blacklist, logger):
    """Follows the user of the currently opened image"""

    try:
        follow_button = browser.find_element_by_xpath(
                "//button[text()='Follow']")

        # Do we still need this sleep?
        sleep(2)

        if follow_button.is_displayed():
            follow_button.click()
            update_activity('follows')
        else:
            browser.execute_script(
                "arguments[0].style.visibility = 'visible'; "
                "arguments[0].style.height = '10px'; "
                "arguments[0].style.width = '10px'; "
                "arguments[0].style.opacity = 1", follow_button)
            follow_button.click()
            update_activity('follows')

        logger.info('--> Now following')
        log_followed_pool(login, user_name, logger)
        follow_restrict[user_name] = follow_restrict.get(user_name, 0) + 1
        if blacklist['enabled'] is True:
            action = 'followed'
            add_user_to_blacklist(
                browser, user_name, blacklist['campaign'], action, logger
            )
        sleep(3)
        return 1
    except NoSuchElementException:
        logger.info('--> Already following')
        sleep(1)
        return 0


def unfollow_user(browser, logger):
    """Unfollows the user of the currently opened image"""

    unfollow_button = browser.find_element_by_xpath(
        "//*[contains(text(), 'Following')]")

    if unfollow_button.text == 'Following':
        unfollow_button.send_keys("\n")
        update_activity('unfollows')
        logger.warning('--> User unfollowed due to Inappropriate Content')
        sleep(3)
        return 1


def follow_given_user(browser,
                      acc_to_follow,
                      follow_restrict,
                      blacklist,
                      logger):
    """Follows a given user."""
    browser.get('https://www.instagram.com/' + acc_to_follow)
    # update server calls
    update_activity()
    logger.info('--> {} instagram account is opened...'.format(acc_to_follow))

    try:
        sleep(10)
        follow_button = browser.find_element_by_xpath("//*[text()='Follow']")
        follow_button.send_keys("\n")
        update_activity('follows')
        logger.info('---> Now following: {}'.format(acc_to_follow))
        follow_restrict[acc_to_follow] = follow_restrict.get(
            acc_to_follow, 0) + 1

        if blacklist['enabled'] is True:
            action = 'followed'
            add_user_to_blacklist(
                browser, acc_to_follow, blacklist['campaign'], action, logger
            )

        sleep(3)
        return 1
    except NoSuchElementException:
        logger.warning('---> {} is already followed'.format(acc_to_follow))
        sleep(3)
        return 0


def follow_through_dialog(browser,
                          user_name,
                          amount,
                          dont_include,
                          login,
                          follow_restrict,
                          allfollowing,
                          randomize,
                          delay,
                          blacklist,
                          logger,
                          follow_times,
                          callbacks=[]):
    sleep(2)
    person_followed = []
    real_amount = amount
    if randomize and amount >= 3:
        # expanding the popultaion for better sampling distribution
        amount = amount * 3

    # find dialog box
    dialog = browser.find_element_by_xpath(
      "//div[text()='Followers' or text()='Following']/following-sibling::div")

    # scroll down the page
    scroll_bottom(browser, dialog, allfollowing)

    # get follow buttons. This approch will find the follow buttons and
    # ignore the Unfollow/Requested buttons.
    follow_buttons = dialog.find_elements_by_xpath(
        "//div/div/span/button[text()='Follow']")

    person_list = []
    abort = False
    total_list = len(follow_buttons)

    # scroll down if the generated list of user to follow is not enough to
    # follow amount set
    while (total_list < amount) and not abort:
        amount_left = amount - total_list
        before_scroll = total_list
        scroll_bottom(browser, dialog, amount_left)
        sleep(1)
        follow_buttons = dialog.find_elements_by_xpath(
            "//div/div/span/button[text()='Follow']")
        total_list = len(follow_buttons)
        abort = (before_scroll == total_list)

    for person in follow_buttons:

        if person and hasattr(person, 'text') and person.text:
            try:
                person_list.append(person.find_element_by_xpath("../../../*")
                                   .find_elements_by_tag_name("a")[1].text)
            except IndexError:
                pass  # Element list is too short to have a [1] element

    if amount >= total_list:
        amount = total_list
        logger.warning("{} -> Less users to follow than requested."
                       .format(user_name))

    # follow loop
    try:
        hasSlept = False
        btnPerson = list(zip(follow_buttons, person_list))
        if randomize:
            sample = random.sample(range(0, len(follow_buttons)), real_amount)
            finalBtnPerson = []
            for num in sample:
                finalBtnPerson.append(btnPerson[num])
        else:
            finalBtnPerson = btnPerson

        followNum = 0

        for button, person in finalBtnPerson:
            if followNum >= real_amount:
                logger.info("--> Total followNum reached: {}"
                            .format(followNum))
                break

            if followNum != 0 and hasSlept is False and followNum % 10 == 0:
                if delay < 60:
                    logger.info('sleeping for about {} seconds'.format(delay))
                else:
                    logger.info(
                        'sleeping for about {} minutes'.format(delay/60))
                sleep(delay)
                hasSlept = True
                continue

            if (person not in dont_include and
                follow_restrict.get(person, 0) < follow_times):

                followNum += 1
                # Register this session's followed user for further interaction
                person_followed.append(person)

                button.send_keys("\n")
                log_followed_pool(login, person, logger)
                update_activity('follows')

                follow_restrict[person] = follow_restrict.get(person, 0) + 1

                logger.info('--> Ongoing follow {}, now following: {}'
                            .format(str(followNum), person.encode('utf-8')))

                if blacklist['enabled'] is True:
                    action = 'followed'
                    add_user_to_blacklist(
                        browser, person, blacklist['campaign'], action, logger
                    )

                for callback in callbacks:
                    callback(person.encode('utf-8'))
                sleep(15)

                # To only sleep once until there is the next follow
                if hasSlept:
                    hasSlept = False

                continue

            else:
                if randomize:
                    repickedNum = -1
                    while repickedNum not in sample and repickedNum != -1:
                        repickedNum = random.randint(0, len(btnPerson))
                    sample.append(repickedNum)
                    finalBtnPerson.append(btnPerson[repickedNum])
                continue

    except BaseException as e:
        logger.error("follow loop error {}".format(str(e)))

    return person_followed


def get_given_user_followers(browser,
                             user_name,
                             amount,
                             dont_include,
                             login,
                             randomize,
                             logger):

    browser.get('https://www.instagram.com/' + user_name)
    # update server calls
    update_activity()

    # check how many poeple are following this user.
    # throw RuntimeWarning if we are 0 people following this user or
    # if its a private account
    try:
        allfollowing = formatNumber(
            browser.find_element_by_xpath("//li[2]/a/span").text)
    except NoSuchElementException:
        logger.warning('Can\'t interact with private account')
        return

    following_link = browser.find_elements_by_xpath(
        '//a[@href="/' + user_name + '/followers/"]')
    following_link[0].send_keys("\n")
    # update server calls
    update_activity()

    sleep(2)

    # find dialog box
    dialog = browser.find_element_by_xpath(
        "//div[text()='Followers']/following-sibling::div")

    # scroll down the page
    scroll_bottom(browser, dialog, allfollowing)

    # get follow buttons. This approch will find the follow buttons and
    # ignore the Unfollow/Requested buttons.
    follow_buttons = dialog.find_elements_by_xpath(
        "//div/div/span/button[text()='Follow']")
    person_list = []

    if amount >= len(follow_buttons):
        amount = len(follow_buttons)
        logger.warning("{} -> Less users to follow than requested."
                       .format(user_name))

    finalBtnPerson = []
    if randomize:
        sample = random.sample(range(0, len(follow_buttons)), amount)

        for num in sample:
            finalBtnPerson.append(follow_buttons[num])
    else:
        finalBtnPerson = follow_buttons[0:amount]
    for person in finalBtnPerson:

        if person and hasattr(person, 'text') and person.text:
            person_list.append(person.find_element_by_xpath(
                "../../../*").find_elements_by_tag_name("a")[1].text)

    return person_list


def get_given_user_following(browser,
                             user_name,
                             amount,
                             dont_include,
                             login,
                             randomize,
                             logger):

    browser.get('https://www.instagram.com/' + user_name)
    # update server calls
    update_activity()

    #  check how many poeple are following this user.
    #  throw RuntimeWarning if we are 0 people following this user
    try:
        allfollowing = formatNumber(
            browser.find_element_by_xpath("//li[3]/a/span").text)
    except NoSuchElementException:
        logger.warning('There are 0 people to follow')

    try:
        following_link = browser.find_elements_by_xpath(
            '//a[@href="/' + user_name + '/following/"]')
        following_link[0].send_keys("\n")
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

    # get follow buttons. This approch will find the follow buttons and
    # ignore the Unfollow/Requested buttons.
    follow_buttons = dialog.find_elements_by_xpath(
        "//div/div/span/button[text()='Follow']")
    person_list = []

    if amount >= len(follow_buttons):
        amount = len(follow_buttons)
        logger.warning("{} -> Less users to follow than requested."
                       .format(user_name))

    finalBtnPerson = []
    if randomize:
        sample = random.sample(range(0, len(follow_buttons)), amount)

        for num in sample:
            finalBtnPerson.append(follow_buttons[num])
    else:
        finalBtnPerson = follow_buttons[0:amount]
    for person in finalBtnPerson:

        if person and hasattr(person, 'text') and person.text:
            person_list.append(person.find_element_by_xpath(
                "../../../*").find_elements_by_tag_name("a")[1].text)

    return person_list


def follow_given_user_followers(browser,
                                user_name,
                                amount,
                                dont_include,
                                login,
                                follow_restrict,
                                random,
                                delay,
                                blacklist,
                                logger,
                                follow_times):

    browser.get('https://www.instagram.com/' + user_name)
    # update server calls
    update_activity()

    #  check how many poeple are following this user.
    #  throw RuntimeWarning if we are 0 people following this user
    try:
        allfollowing = formatNumber(
            browser.find_element_by_xpath("//li[2]/a/span").text)
    except NoSuchElementException:
        logger.warning('There are 0 people to follow')

    try:
        following_link = browser.find_elements_by_xpath(
            '//a[@href="/' + user_name + '/followers/"]')
        following_link[0].send_keys("\n")
        # update server calls
        update_activity()
    except BaseException as e:
        logger.error("following_link error {}".format(str(e)))

    personFollowed = follow_through_dialog(browser,
                                           user_name,
                                           amount,
                                           dont_include,
                                           login,
                                           follow_restrict,
                                           allfollowing,
                                           random,
                                           delay,
                                           blacklist,
                                           logger,
                                           follow_times,
                                           callbacks=[])

    return personFollowed


def follow_given_user_following(browser,
                                user_name,
                                amount,
                                dont_include,
                                login,
                                follow_restrict,
                                random,
                                delay,
                                blacklist,
                                logger,
                                follow_times):

    browser.get('https://www.instagram.com/' + user_name)
    # update server calls
    update_activity()

    #  check how many poeple are following this user.
    #  throw RuntimeWarning if we are 0 people following this user
    try:
        allfollowing = formatNumber(
            browser.find_element_by_xpath("//li[3]/a/span").text)
    except NoSuchElementException:
        logger.warning('There are 0 people to follow')

    try:
        following_link = browser.find_elements_by_xpath(
            '//a[@href="/' + user_name + '/following/"]')
        following_link[0].send_keys("\n")
        # update server calls
        update_activity()
    except BaseException as e:
        logger.error("following_link error {}".format(str(e)))

    personFollowed = follow_through_dialog(browser,
                                           user_name,
                                           amount,
                                           dont_include,
                                           login,
                                           follow_restrict,
                                           allfollowing,
                                           random,
                                           delay,
                                           blacklist,
                                           logger,
                                           follow_times)

    return personFollowed


def dump_follow_restriction(followRes):
    """Dumps the given dictionary to a file using the json format"""
    with open('./logs/followRestriction.json', 'w') as followResFile:
        json.dump(followRes, followResFile)


def load_follow_restriction():
    """Loads the saved """
    with open('./logs/followRestriction.json') as followResFile:
        return json.load(followResFile)
