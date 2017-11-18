import re
import csv
import os
from .time_util import sleep
from selenium.common.exceptions import NoSuchElementException
import sqlite3


def update_activity(action=None):
    """Record every Instagram server call (page load, content load, likes,
    comments, follows, unfollow)."""

    conn = sqlite3.connect('./db/instapy.db')
    with conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        # collect today data
        cur.execute("SELECT * FROM statistics WHERE created == date('now')")
        data = cur.fetchone()

        if data is None:
            # create a new record for the new day
            cur.execute("INSERT INTO statistics VALUES "
                        "(0, 0, 0, 0, 1, date('now'))")
        else:
            # sqlite3.Row' object does not support item assignment -> so,
            # convert it into a new dict
            data = dict(data)
            # update
            data['server_calls'] += 1

            if action == 'likes':
                data['likes'] += 1
            elif action == 'comments':
                data['comments'] += 1
            elif action == 'follows':
                data['follows'] += 1
            elif action == 'unfollows':
                data['unfollows'] += 1

            sql = ("UPDATE statistics set likes = ?, comments = ?, "
                   "follows = ?, unfollows = ?, server_calls = ? "
                   "WHERE created = date('now')")
            cur.execute(sql, (data['likes'], data['comments'], data['follows'],
                              data['unfollows'], data['server_calls']))
        # commit
        conn.commit()


def add_user_to_blacklist(browser, username, campaign, action, logger):

    file_exists = os.path.isfile('./logs/blacklist.csv')
    fieldnames = ['username', 'campaign', 'action']

    try:

        with open('./logs/blacklist.csv', 'a+') as blacklist:
            writer = csv.DictWriter(blacklist, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                    'username': username,
                    'campaign': campaign,
                    'action': action
            })
    except Exception as err:
        logger.error(err)

    logger.info('--> {} added to blacklist for {} campaign (action: {})'
                .format(username, campaign, action))


def get_active_users(browser, username, posts, logger):
    """Returns a list with users who liked the latest posts"""

    browser.get('https://www.instagram.com/' + username)
    sleep(2)

    total_posts = formatNumber(browser.find_element_by_xpath(
        '//header/div[2]/ul/li[1]/span/span').text)

    if posts > total_posts:
        # reaches all user posts
        posts = total_posts

    # click latest post
    browser.find_element_by_xpath(
        '//article/div/div[1]/div[1]/div[1]/a').click()

    active_users = []

    # posts argument is the number of posts to collect usernames
    for count in range(posts):
        try:
            sleep(2)
            tmp_list = (browser.find_element_by_class_name('_3gwk6').
                        find_elements_by_tag_name('a'))
            # if post has no liked
            if tmp_list[0].text == 'like this':
                tmp_list = []
            else:
                # if there is a button to show more likes
                more_likes = (
                    re.search(r'\b\d+ likes?\b', tmp_list[0].text, re.I)
                )
                if more_likes is not None:
                    browser.find_element_by_class_name('_nzn1h').click()
                    sleep(1)
                    tmp_list = browser.find_elements_by_class_name('_2g7d5')

        except NoSuchElementException:
            logger.error('There is some error searching active users')

        if len(tmp_list) is not 0:
            for user in tmp_list:
                active_users.append(user.text)

        sleep(2)
        # trick to find the right button after 1st posts
        if count == 0:
            browser.find_element_by_xpath(
                '//body/div[4]/div/div/div[1]/div/div/a').click()
        elif count is not (total_posts-1):
            # don't click next posts on last post
            browser.find_element_by_xpath(
                '//body/div[4]/div/div/div[1]/div/div/a[2]').click()

    # delete duplicated users
    active_users = list(set(active_users))

    return active_users


def delete_line_from_file(filepath, lineToDelete, logger):
    try:
        f = open(filepath, "r")
        lines = f.readlines()
        f.close()
        f = open(filepath, "w")

        for line in lines:

            if line != lineToDelete:
                f.write(line)
        f.close()
    except BaseException as e:
        logger.error("delete_line_from_file error {}".format(str(e)))


def scroll_bottom(browser, element, range_int):
    # put a limit to the scrolling
    if range_int > 50:
        range_int = 50

    for i in range(int(range_int / 2)):
        browser.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", element)
        # update server calls
        update_activity()
        sleep(1)

    return


def formatNumber(number):
    formattedNum = number.replace(',', '').replace('.', '')
    formattedNum = int(formattedNum.replace('k', '00').replace('m', '00000'))
    return formattedNum
