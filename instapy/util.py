import re
from .time_util import sleep
from selenium.common.exceptions import NoSuchElementException


def add_user_to_blacklist(browser):

    # image like dialog
    try:
        user_name = browser.find_element_by_xpath(
            '//article/header/div[2]/div[1]/div[1]/a')

        with open('./logs/blacklist.txt', 'a+') as blacklist:
            blacklist.write(user_name.text + "\n")
    except:
        try:
            user_name = browser.find_element_by_xpath(
                '//article/header/div[2]/div[1]/h1')

            with open('./logs/blacklist.txt', 'a+') as blacklist:
                blacklist.write(user_name.text + "\n")
        except Exception as err:
            print(err)


def get_active_users(browser, username, posts):
    """Returns a list with users who liked the latest posts"""

    browser.get('https://www.instagram.com/' + username)
    sleep(2)
    # click latest post
    browser.find_element_by_xpath(
        '//article/div/div[1]/div[1]/div[1]/a').click()

    active_users = []

    # posts argument is the number of posts to collect usernames
    for count in range(posts):
        try:
            sleep(2)
            # if there is no show more likes button
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
            raise RuntimeWarning('There is some error finding active users')

        if len(tmp_list) is not 0:
            for user in tmp_list:
                active_users.append(user.text)

        sleep(2)
        # go to next media
        if count == 0:
            browser.find_element_by_xpath(
                '//body/div[4]/div/div/div[1]/div/div/a').click()
        else:
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
        sleep(1)

    return


def formatNumber(number):
    formattedNum = number.replace(',', '').replace('.', '')
    formattedNum = int(formattedNum.replace('k', '00').replace('m', '00000'))
    return formattedNum
