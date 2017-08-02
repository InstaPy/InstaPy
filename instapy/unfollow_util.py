"""Module which handles the follow features like unfollowing and following"""
import json
import csv
from .time_util import sleep
from random import randint
from .util import delete_line_from_file
from .util import scroll_bottom
from .print_log_writer import log_followed_pool


def set_automated_followed_pool(username):
    automatedFollowedPool = []
    try:
        with open('./logs/' + username + '_followedPool.csv') as followedPoolFile:
            reader = csv.reader(followedPoolFile)
            automatedFollowedPool = [row[0] for row in reader]

        print("Number of people followed automatically remaining: {}".format(len(automatedFollowedPool)))
        followedPoolFile.close()

    except BaseException as e:
        print("set_automated_followed_pool error \n", str(e))

    return automatedFollowedPool


def unfollow(browser, username, amount, dont_include, onlyInstapyFollowed, automatedFollowedPool):
    """unfollows the given amount of users"""
    unfollowNum = 0

    browser.get('https://www.instagram.com/' + username)

    #  check how many poeple we are following
    allfollowing = browser.find_element_by_xpath("//li[3]/a/span").text
    allfollowing = allfollowing.replace(',', '').replace('.', '')
    allfollowing = int(allfollowing.replace('k', '00').replace('m', '00000'))

    #  throw RuntimeWarning if we are 0 people following
    if (allfollowing == 0):
        raise RuntimeWarning('There are 0 people to unfollow')

    try:
        following_link = browser.find_elements_by_xpath('//header/div[2]//li[3]')
        following_link[0].click()
    except BaseException as e:
        print("following_link error \n", str(e))

    sleep(2)

    # find dialog box

    dialog = browser.find_element_by_xpath('/html/body/div[4]/div/div[2]/div/div[2]/div/div[2]')

    # scroll down the page
    scroll_bottom(browser, dialog, allfollowing)

    # get persons, unfollow buttons, and length of followed pool
    person_list_a = dialog.find_elements_by_tag_name("a")
    person_list = []

    for person in person_list_a:

        if person and hasattr(person, 'text') and person.text:
            person_list.append(person.text)

    follow_buttons = dialog.find_elements_by_tag_name('button')
    automatedFollowedPoolLength = len(automatedFollowedPool)

    # unfollow loop
    try:
        hasSlept = False

        for button, person in zip(follow_buttons, person_list):
            if unfollowNum >= amount:
                print("--> Total unfollowNum reached it's amount given ", unfollowNum)
                break

            if onlyInstapyFollowed == True and unfollowNum >= automatedFollowedPoolLength:
                print("--> Total unfollowNum exeeded the pool of automated followed ", unfollowNum)
                break

            if unfollowNum != 0 and hasSlept == False and unfollowNum % 10 == 0:
                print('sleeping for about 10min')
                sleep(600)
                hasSlept = True
                continue

            if person not in dont_include:
                if onlyInstapyFollowed == True and person in automatedFollowedPool:
                    unfollowNum += 1
                    button.click()
                    delete_line_from_file('./logs/' + username + '_followedPool.csv', person + ",\n")

                    print('--> Ongoing Unfollow From InstaPy ' + str(unfollowNum) + ', now unfollowing: {}'.format(
                        person.encode('utf-8')))
                    sleep(15)
                    # To only sleep once until there is the next unfollow
                    if hasSlept: hasSlept = False

                    continue

                elif onlyInstapyFollowed != True:
                    unfollowNum += 1
                    button.click()

                    print('--> Ongoing Unfollow ' + str(unfollowNum) + ', now unfollowing: {}'.format(
                        person.encode('utf-8')))
                    sleep(15)
                    # To only sleep once until there is the next unfollow
                    if hasSlept: hasSlept = False

                    continue

            else:
                continue

    except BaseException as e:
        print("unfollow loop error \n", str(e))

    return unfollowNum


def follow_user(browser, follow_restrict, login, user_name):
    """Follows the user of the currently opened image"""

    follow_button = browser.find_element_by_xpath("//article/header/span/button")
    sleep(2)

    if follow_button.text == 'Follow':
        follow_button.click()
        print('--> Now following')
        log_followed_pool(login, user_name)
        follow_restrict[user_name] = follow_restrict.get(user_name, 0) + 1
        sleep(3)
        return 1

    else:
        print('--> Already following')
        sleep(1)
        return 0


def follow_given_user(browser, acc_to_follow, follow_restrict):
    """Follows a given user."""
    browser.get('https://www.instagram.com/' + acc_to_follow)
    print('--> {} instagram account is opened...'.format(acc_to_follow))
    follow_button = browser.find_element_by_xpath("//*[contains(text(), 'Follow')]")
    sleep(10)
    if follow_button.text == 'Follow':
        follow_button.click()
        print('---> Now following: {}'.format(acc_to_follow))
        print('*' * 20)
        follow_restrict[acc_to_follow] = follow_restrict.get(acc_to_follow, 0) + 1
        sleep(3)
        return 1
    else:
        print('---> {} is already followed'.format(acc_to_follow))
        print('*' * 20)
        sleep(3)
        return 0


def dump_follow_restriction(followRes):
    """Dumps the given dictionary to a file using the json format"""
    with open('./logs/followRestriction.json', 'w') as followResFile:
        json.dump(followRes, followResFile)


def load_follow_restriction():
    """Loads the saved """
    with open('./logs/followRestriction.json') as followResFile:
        return json.load(followResFile)
