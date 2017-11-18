import re
import csv
import datetime
import shutil
import os
from .time_util import sleep
from selenium.common.exceptions import NoSuchElementException
from tempfile import NamedTemporaryFile


def update_activity(action=None):
    """Record every Instagram server call (page load, content load, likes,
    comments, follows, unfollow)."""

    # workaround for windows users, they cant use it in this way, we need to
    if os.name == 'nt':
        return

    # file header
    fieldnames = [
        'date', 'likes', 'comments', 'follows', 'unfollows', 'server_calls']
    today = datetime.date.today().strftime('%m/%d/%y')
    tmpfile = NamedTemporaryFile(mode='w', delete=False)

    # csv update file technique, moves activity.csv content to a temporary
    # file, update needed line, then move temporary file content back to
    # activity.csv file
    try:
        with open('./logs/activity.csv', 'r') as activity, tmpfile:
            reader = csv.DictReader(activity)
            writer = csv.DictWriter(tmpfile, fieldnames=fieldnames)

            # add header to the new file (temporary file)
            writer.writeheader()

            new_day = True
            for row in reader:
                if row['date'] == today:
                    new_day = False
                    # update server call
                    row['server_calls'] = int(row['server_calls']) + 1

                    if action == 'likes':
                        row['likes'] = int(row['likes']) + 1
                    elif action == 'comments':
                        row['comments'] = int(row['comments']) + 1
                    elif action == 'follows':
                        row['follows'] = int(row['follows']) + 1
                    elif action == 'unfollows':
                        row['unfollows'] = int(row['unfollows']) + 1

                # update daily activity
                writer.writerow({
                    'date': row['date'],
                    'likes': row['likes'],
                    'comments': row['comments'],
                    'follows': row['follows'],
                    'unfollows': row['unfollows'],
                    'server_calls': row['server_calls']
                })

            # begin new statistics if it's a new day
            if new_day is True:

                likes = 0
                comments = 0
                follows = 0
                unfollows = 0

                if action == 'likes':
                    likes = 1
                elif action == 'comments':
                    comments = 1
                elif action == 'follows':
                    follows = 1
                elif action == 'unfollows':
                    unfollows = 1

                writer.writerow({
                    'date': today,
                    'likes': likes,
                    'comments': comments,
                    'follows': follows,
                    'unfollows': unfollows,
                    'server_calls': 1
                })

            # move temporary file to activity.csv (updating csv file)
            shutil.move(tmpfile.name, './logs/activity.csv')
    except IOError:
        # if file doesnt exist/first run, create activity file
        with open('./logs/activity.csv', 'w') as activity:
            writer = csv.DictWriter(activity, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                'date': today,
                'likes': 0,
                'comments': 0,
                'follows': 0,
                'unfollows': 0,
                'server_calls': 1
            })


def add_user_to_blacklist(browser, username, campaign, action):

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
        print(err)

    print('--> {} added to blacklist for {} campaign (action: {})'
          .format(username, campaign, action))


def get_active_users(browser, username, posts):
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
            raise RuntimeWarning('There is some error searching active users')

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


def delete_line_from_file(filepath, lineToDelete):
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
        print("delete_line_from_file error \n", str(e))


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
