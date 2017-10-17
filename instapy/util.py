from .time_util import sleep
from selenium.common.exceptions import NoSuchElementException


def get_active_users(browser, username, posts):

    browser.get('https://www.instagram.com/' + username)
    sleep(2)
    # click latest post
    browser.find_element_by_xpath(
        '//article/div/div[1]/div[1]/div[1]/a').click()

    active_users = []

    for count in range(posts):
        try:
            sleep(1)
            tmp_list = (browser.find_element_by_class_name('_3gwk6').
                        find_elements_by_tag_name('a'))
            # need to improve it
            if len(tmp_list) == 1:
                if tmp_list[0].text[-5:] == 'likes':
                    browser.find_element_by_class_name('_nzn1h').click()

                    sleep(1)
                    tmp_list = browser.find_elements_by_class_name('_2g7d5')

        except NoSuchElementException:
            raise RuntimeWarning('There is some error finding active users')

        for user in tmp_list:
            active_users.append(user.text)

        sleep(1)
        # go to next media
        if count == 0:
            browser.find_element_by_xpath(
                '//body/div[4]/div/div/div[1]/div/div/a').click()
        else:
            browser.find_element_by_xpath(
                '//body/div[4]/div/div/div[1]/div/div/a[2]').click()
        sleep(1)

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
