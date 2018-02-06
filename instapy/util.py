import csv
import os
from .time_util import sleep
from .time_util import sleep_actual
from selenium.common.exceptions import NoSuchElementException
import sqlite3
import datetime


def validate_username(browser,
                      username,
                      ignore_users,
                      blacklist,
                      like_by_followers_upper_limit,
                      like_by_followers_lower_limit):
    """Check if we can interact with the user"""

    if username in ignore_users:
        return ('---> {} is in ignore_users list, skipping '
                'user...'.format(username))
    if username in blacklist:
        return '---> {} is in blacklist, skipping user...'

    browser.get('https://www.instagram.com/{}'.format(username))
    sleep(1)
    try:
        followers = (formatNumber(browser.find_element_by_xpath("//a[contains"
                     "(@href,'followers')]/span").text))
    except NoSuchElementException:
        return '---> {} account is private, skipping user...'.format(username)

    if followers > like_by_followers_upper_limit:
        return '---> User {} exceeds followers limit'.format(username)
    elif followers < like_by_followers_lower_limit:
        return ('---> {}, number of followers does not reach '
                'minimum'.format(username))

    # if everything ok
    return True


def update_activity(action=None, username):
    """Record every Instagram server call (page load, content load, likes,
    comments, follows, unfollow)."""

    conn = sqlite3.connect('./db/instapy.db')
    with conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Upgrade schema
        try:
            cur.execute('ALTER TABLE statistics ADD COLUMN username;')
        except:
            # Column already exists
            pass

        # collect today data
        cur.execute("SELECT * FROM statistics WHERE created == date('now') AND username == %s", (username))
        data = cur.fetchone()

        if data is None:
            # create a new record for the new day
            cur.execute("INSERT INTO statistics VALUES "
                        "(0, 0, 0, 0, 1, date('now'), %s)", (username))
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
                   "WHERE created == date('now') AND username == %s", (username))
            cur.execute(sql, (data['likes'], data['comments'], data['follows'],
                              data['unfollows'], data['server_calls']))
        # commit
        conn.commit()


def add_user_to_blacklist(browser, username, campaign, action, logger, logfolder):

    file_exists = os.path.isfile('{}blacklist.csv'.format(logfolder))
    fieldnames = ['date', 'username', 'campaign', 'action']
    today = datetime.date.today().strftime('%m/%d/%y')

    try:
        with open('{}blacklist.csv'.format(logfolder), 'a+') as blacklist:
            writer = csv.DictWriter(blacklist, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                    'date': today,
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
        "//span[contains(@class,'_t98z6')]//span").text)

    # if posts > total user posts, assume total posts
    if posts >= total_posts:
        # reaches all user posts
        posts = total_posts

    # click latest post
    browser.find_element_by_xpath(
        "(//div[contains(@class, '_si7dy')])[1]").click()

    active_users = []

    # posts argument is the number of posts to collect usernames
    for count in range(1, posts):
        try:
            browser.find_element_by_xpath(
                "//a[contains(@class, '_nzn1h')]").click()
            sleep(1)
            tmp_list = browser.find_elements_by_xpath(
                "//a[contains(@class, '_2g7d5')]")
        except NoSuchElementException:
            try:
                tmp_list = browser.find_elements_by_xpath(
                    "//div[contains(@class, '_3gwk6')]/a")
            except NoSuchElementException:
                logger.error('There is some error searching active users')

        if len(tmp_list) is not 0:
            for user in tmp_list:
                active_users.append(user.text)

        sleep(1)
        # if not reached posts(parameter) value, continue
        if count+1 != posts:
            try:
                # click next button
                browser.find_element_by_xpath(
                    "//a[@class='_3a693 coreSpriteRightPaginationArrow']"
                    "[text()='Next']").click()
            except:
                logger.error('Unable to go to next profile post')

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


def scroll_bottom(browser, element, range_int, username):
    # put a limit to the scrolling
    if range_int > 50:
        range_int = 50

    for i in range(int(range_int / 2)):
        browser.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", element)
        # update server calls
        update_activity(username=username)
        sleep(1)

    return

# There are three (maybe more) different ways to "click" an element/button.
# 1. element.click()
# 2. element.send_keys("\n")
# 3. browser.execute_script("document.getElementsByClassName('" + element.get_attribute("class") + "')[0].click()")

# I'm guessing all three have their advantages/disadvantages
# Before committing over this code, you MUST justify your change
# and potentially adding an 'if' statement that applies to your 
# specific case. See the following issue for more details
# https://github.com/timgrossmann/InstaPy/issues/1232
def click_element(browser, element, tryNum=0):
    # explaination of the following recursive function:
    #   we will attempt to click the element given, if an error is thrown
    #   we know something is wrong (element not in view, element doesn't 
    #   exist, ...). on each attempt try and move the screen around in 
    #   various ways. if all else fails, programmically click the button
    #   using `execute_script` in the browser.
    
    try:
        # use Selenium's built in click function
        element.click()
    except:
        # click attempt failed
        # try something funky and try again

        if tryNum == 0:
            # try scrolling the element into view
            browser.execute_script("document.getElementsByClassName('" +  element.get_attribute("class") + "')[0].scrollIntoView({ inline: 'center' });")
        elif tryNum == 1:
            # well, that didn't work, try scrolling to the top and then clicking again
            browser.execute_script("window.scrollTo(0,0);")
        elif tryNum == 2:
            # that didn't work either, try scrolling to the bottom and then clicking again
            browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        else:
            # try `execute_script` as a last resort
            # print("attempting last ditch effort for click, `execute_script`")
            browser.execute_script("document.getElementsByClassName('" +  element.get_attribute("class") + "')[0].click()")
            return # end condition for the recursive function
            

        # sleep for 1 second to allow window to adjust (may or may not be needed)
        sleep_actual(1)

        tryNum += 1

        # try again!
        click_element(browser, element, tryNum)
    

def formatNumber(number):
    formattedNum = number.replace(',', '').replace('.', '')
    formattedNum = int(formattedNum.replace('k', '00').replace('m', '00000'))
    return formattedNum
