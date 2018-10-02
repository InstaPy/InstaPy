""" Common utilities """
import random
import time
import datetime
import re
import signal
import os
from sys import exit as clean_exit
from platform import system
from subprocess import call
import csv
import sqlite3
import json
from contextlib import contextmanager
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from tempfile import gettempdir

from .time_util import sleep
from .time_util import sleep_actual
from .database_engine import get_database
from .quota_supervisor import quota_supervisor
from .settings import Settings

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException

default_profile_pic_instagram = ["https://instagram.flas1-2.fna.fbcdn.net/vp/a8539c22ed9fec8e1c43b538b1ebfd1d/5C5A1A7A/t51.2885-19/11906329_960233084022564_1448528159_a.jpg",
                                 "https://scontent-yyz1-1.cdninstagram.com/vp/a8539c22ed9fec8e1c43b538b1ebfd1d/5C5A1A7A/t51.2885-19/11906329_960233084022564_1448528159_a.jpg",
                                 "https://instagram.faep12-1.fna.fbcdn.net/vp/a8539c22ed9fec8e1c43b538b1ebfd1d/5C5A1A7A/t51.2885-19/11906329_960233084022564_1448528159_a.jpg",
                                 "https://instagram.fbts2-1.fna.fbcdn.net/vp/a8539c22ed9fec8e1c43b538b1ebfd1d/5C5A1A7A/t51.2885-19/11906329_960233084022564_1448528159_a.jpg",
                                 "https://scontent-mia3-1.cdninstagram.com/vp/a8539c22ed9fec8e1c43b538b1ebfd1d/5C5A1A7A/t51.2885-19/11906329_960233084022564_1448528159_a.jpg"]


def is_private_profile(browser, logger, following=True):
    is_private = None
    try:
        is_private = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].graphql.user.is_private")

    except WebDriverException:
        try:
            browser.execute_script("location.reload()")
            update_activity()

            is_private = browser.execute_script(
                "return window._sharedData.entry_data."
                "ProfilePage[0].graphql.user.is_private")

        except WebDriverException:
            return None

    # double check with xpath that should work only when we not follwoing a user
    if is_private is True and not following:
        logger.info("Is private account you're not following.")
        body_elem = browser.find_element_by_tag_name('body')
        is_private = body_elem.find_element_by_xpath(
            '//h2[@class="_kcrwx"]')

    return is_private


def validate_username(browser,
                      username_or_link,
                      own_username,
                      ignore_users,
                      blacklist,
                      potency_ratio,
                      delimit_by_numbers,
                      max_followers,
                      max_following,
                      min_followers,
                      min_following,
                      min_posts,
                      max_posts,
                      skip_private,
                      skip_private_percentage,
                      skip_no_profile_pic,
                      skip_no_profile_pic_percentage,
                      skip_business,
                      skip_business_percentage,
                      skip_business_categories,
                      dont_skip_business_categories,
                      logger):
    """Check if we can interact with the user"""

    # Some features may not povide `username` and in those cases we will get it from post's page.
    if '/' in username_or_link:
        link = username_or_link  # if there is a `/` in `username_or_link`, then it is a `link`

        # check URL of the webpage, if it already is user's profile page, then do not navigate to it again
        web_address_navigator(browser, link)

        try:
            username = browser.execute_script(
                "return window._sharedData.entry_data."
                "PostPage[0].graphql.shortcode_media.owner.username")

        except WebDriverException:
            try:
                browser.execute_script("location.reload()")
                update_activity()

                username = browser.execute_script(
                    "return window._sharedData.entry_data."
                    "PostPage[0].graphql.shortcode_media.owner.username")

            except WebDriverException:
                logger.error("Username validation failed! ~cannot get the post owner's username")
                return False, \
                       "---> Sorry, this page isn't available! ~link is broken, or page is removed\n"
    else:
        username = username_or_link  # if there is no `/` in `username_or_link`, then it is a `username`

    if username == own_username:
        return False, \
               "---> Username '{}' is yours!  ~skipping user\n".format(own_username)

    if username in ignore_users:
        return False, \
               "---> {} is in ignore_users list  ~skipping user\n".format(username)

    if username in blacklist:
        return False, \
               "---> {} is in blacklist  ~skipping user\n".format(username)

    """Checks the potential of target user by relationship status in order to delimit actions within the desired boundary"""
    if potency_ratio or delimit_by_numbers and (max_followers or max_following or min_followers or min_following):

        relationship_ratio = None
        reverse_relationship = False

        # Get followers & following counts
        followers_count, following_count = get_relationship_counts(browser, username, logger)

        if potency_ratio and potency_ratio < 0:
            potency_ratio *= -1
            reverse_relationship = True

        if followers_count and following_count:
            relationship_ratio = (float(followers_count) / float(following_count)
                                  if not reverse_relationship
                                  else float(following_count) / float(followers_count))

        logger.info('User: {} >> followers: {}  |  following: {}  |  relationship ratio: {}'.format(username,
                                                                                                    followers_count if followers_count else 'unknown',
                                                                                                    following_count if following_count else 'unknown',
                                                                                                    float(
                                                                                                        "{0:.2f}".format(
                                                                                                            relationship_ratio)) if relationship_ratio else 'unknown'))

        if followers_count or following_count:
            if potency_ratio and not delimit_by_numbers:
                if relationship_ratio and relationship_ratio < potency_ratio:
                    return False, \
                           "{} is not a {} with the relationship ratio of {}  ~skipping user\n".format(
                               username, "potential user" if not reverse_relationship else "massive follower",
                               float("{0:.2f}".format(relationship_ratio)))

            elif delimit_by_numbers:
                if followers_count:
                    if max_followers:
                        if followers_count > max_followers:
                            return False, \
                                   "User {}'s followers count exceeds maximum limit  ~skipping user\n".format(username)
                    if min_followers:
                        if followers_count < min_followers:
                            return False, \
                                   "User {}'s followers count is less than minimum limit  ~skipping user\n".format(
                                       username)
                if following_count:
                    if max_following:
                        if following_count > max_following:
                            return False, \
                                   "User {}'s following count exceeds maximum limit  ~skipping user\n".format(username)
                    if min_following:
                        if following_count < min_following:
                            return False, \
                                   "User {}'s following count is less than minimum limit  ~skipping user\n".format(
                                       username)
                if potency_ratio:
                    if relationship_ratio and relationship_ratio < potency_ratio:
                        return False, \
                               "{} is not a {} with the relationship ratio of {}  ~skipping user\n".format(
                                   username, "potential user" if not reverse_relationship else "massive follower",
                                   float("{0:.2f}".format(relationship_ratio)))

    web_address_navigator(browser, "https://www.instagram.com/" + username + "/")
    if min_posts or max_posts:
        # If you are interested in relationship number of posts boundaries
        try:
            number_of_posts = getUserData("graphql.user.edge_owner_to_timeline_media.count", browser)
        except WebDriverException:
            logger.error("~cannot get number of posts for username")
            return False, "---> Sorry, couldn't check for number of posts of username\n"
        if max_posts:
            if number_of_posts > max_posts:
                return False, "Number of posts ({}) of {} exceeds the max limit given {}\n".format(number_of_posts,
                                                                                                   username, max_posts)
        if min_posts:
            if number_of_posts < min_posts:
                return False, "Number of posts ({}) of {} is not enough for the minimum limit given {}\n".format(
                    number_of_posts, username, min_posts)
    """Skip users"""
    # Skip private

    if skip_private:
        try:
            is_private = getUserData("graphql.user.is_private", browser)
        except WebDriverException:
            logger.error("~cannot get if user is private")
            return False, "---> Sorry, couldn't get if user is private\n"
        if is_private and (random.randint(0, 100) <= skip_private_percentage):
            return False, "{} is private account, by default skip\n".format(username)

    # Skip no profile pic
    if skip_no_profile_pic:
        try:
            profile_pic = getUserData("graphql.user.profile_pic_url", browser)
        except WebDriverException:
            logger.error("~cannot get the post profile pic url")
            return False, "---> Sorry, couldn't get if user profile pic url\n"
        if (profile_pic in default_profile_pic_instagram or str(profile_pic).find("11906329_960233084022564_1448528159_a.jpg") > 0) and (random.randint(0, 100) <= skip_no_profile_pic_percentage):
            return False, "{} has default instagram profile picture\n".format(username)

    # Skip business
    if skip_business:
        # If is business account skip under conditions
        try:
            is_business_account = getUserData("graphql.user.is_business_account", browser)
        except WebDriverException:
            logger.error("~cannot get if user has business account active")
            return False, "---> Sorry, couldn't get if user has business account active\n"
        if is_business_account:
            try:
                category = getUserData("graphql.user.business_category_name", browser)
            except WebDriverException:
                logger.error("~cannot get category name for user")
                return False, "---> Sorry, couldn't get category name for user\n"
            if len(skip_business_categories) == 0:
                # skip if not in dont_include
                if category not in dont_skip_business_categories:
                    if len(dont_skip_business_categories) == 0 and (random.randint(0, 100) <= skip_business_percentage):
                        return False, "{} has business account\n".format(username)
                    else:
                        return False, "{} has business account as a {} which is in the skip_business_categories list given\n".format(
                            username, category)
            else:
                if category in skip_business_categories:
                    return False, "{} has business account as a {} which is in the skip_business_categories list given\n".format(
                        username, category)

    # if everything ok
    return True, "Valid user"


def getUserData(query, browser, basequery="return window._sharedData.entry_data.ProfilePage[0]."):
    try:
        data = browser.execute_script(
            basequery + query)
        return data
    except WebDriverException:
        browser.execute_script("location.reload()")
        update_activity()

        data = browser.execute_script(
            basequery + query)
        return data


def update_activity(action="server_calls"):
    """ Record every Instagram server call (page load, content load, likes,
        comments, follows, unfollow). """
    # check action availability
    quota_supervisor("server_calls")

    # get a DB and start a connection
    db, id = get_database()
    conn = sqlite3.connect(db)

    with conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        # collect today data
        cur.execute("SELECT * FROM recordActivity WHERE profile_id=:var AND "
                    "STRFTIME('%Y-%m-%d %H', created) == STRFTIME('%Y-%m-%d %H', 'now', 'localtime')",
                    {"var": id})
        data = cur.fetchone()

        if data is None:
            # create a new record for the new day
            cur.execute("INSERT INTO recordActivity VALUES "
                        "(?, 0, 0, 0, 0, 1, STRFTIME('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))", (id,))

        else:
            # sqlite3.Row' object does not support item assignment -> so,
            # convert it into a new dict
            data = dict(data)

            # update
            data[action] += 1
            quota_supervisor(action, update=True)

            if action != "server_calls":
                # always update server calls
                data["server_calls"] += 1
                quota_supervisor("server_calls", update=True)

            sql = ("UPDATE recordActivity set likes = ?, comments = ?, "
                   "follows = ?, unfollows = ?, server_calls = ?, "
                   "created = STRFTIME('%Y-%m-%d %H:%M:%S', 'now', 'localtime') "
                   "WHERE  profile_id=? AND STRFTIME('%Y-%m-%d %H', created) == "
                   "STRFTIME('%Y-%m-%d %H', 'now', 'localtime')")

            cur.execute(sql, (data['likes'], data['comments'], data['follows'],
                              data['unfollows'], data['server_calls'], id))

        # commit the latest changes
        conn.commit()


def add_user_to_blacklist(username, campaign, action, logger, logfolder):
    file_exists = os.path.isfile('{}blacklist.csv'.format(logfolder))
    fieldnames = ['date', 'username', 'campaign', 'action']
    today = datetime.date.today().strftime('%m/%d/%y')

    try:
        with open('{}blacklist.csv'.format(logfolder), 'a+', encoding="utf-8") as blacklist:
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
        logger.error('blacklist dictWrite error {}'.format(err))

    logger.info('--> {} added to blacklist for {} campaign (action: {})'
                .format(username, campaign, action))


def get_active_users(browser, username, posts, boundary, logger):
    """Returns a list with usernames who liked the latest n posts"""

    user_link = 'https://www.instagram.com/{}/'.format(username)

    # check URL of the webpage, if it already is user's profile page, then do not navigate to it again
    web_address_navigator(browser, user_link)

    try:
        total_posts = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].graphql.user.edge_owner_to_timeline_media.count")

    except WebDriverException:
        try:
            topCount_elements = browser.find_elements_by_xpath(
                "//span[contains(@class,'g47SY')]")

            if topCount_elements:  # prevent an empty string scenario
                total_posts = format_number(topCount_elements[0].text)

            else:
                logger.info("Failed to get posts count on your profile!  ~empty string")
                total_posts = None

        except NoSuchElementException:
            logger.info("Failed to get posts count on your profile!")
            total_posts = None

    # if posts > total user posts, assume total posts
    posts = posts if total_posts is None else total_posts if posts > total_posts else posts

    # click latest post
    try:
        latest_post = browser.find_elements_by_xpath(
            "//div[contains(@class, '_9AhH0')]")[0]
        click_element(browser, latest_post)

    except (NoSuchElementException, WebDriverException):
        logger.warning("Failed to click on the latest post to grab active likers!\n")
        return []

    active_users = []
    sc_rolled = 0
    start_time = time.time()
    too_many_requests = 0  # this will help to prevent misbehaviours when you request the list of active users repeatedly within less than 10 min of breaks

    message = ("~collecting the entire usernames from posts without a boundary!\n" if boundary is None else
               "~collecting only the visible usernames from posts without scrolling at the boundary of zero..\n" if boundary == 0 else
               "~collecting the usernames from posts with the boundary of {}\n".format(boundary))
    # posts argument is the number of posts to collect usernames
    logger.info("Getting active users who liked the latest {} posts:\n  {}".format(posts, message))

    for count in range(1, posts + 1):
        try:
            sleep_actual(2)
            try:
                likers_count = browser.execute_script(
                    "return window._sharedData.entry_data."
                    "PostPage[0].graphql.shortcode_media.edge_media_preview_like.count")
            except WebDriverException:
                try:
                    likers_count = (browser.find_element_by_xpath(
                        "//a[contains(@class, 'zV_Nj')]/span").text)
                    if likers_count:  ##prevent an empty string scenarios
                        likers_count = format_number(likers_count)
                    else:
                        logger.info("Failed to get likers count on your post {}  ~empty string".format(count))
                        likers_count = None
                except NoSuchElementException:
                    logger.info("Failed to get likers count on your post {}".format(count))
                    likers_count = None

            likes_button = browser.find_element_by_xpath(
                "//a[contains(@class, 'zV_Nj')]")
            click_element(browser, likes_button)
            sleep_actual(5)

            dialog = browser.find_element_by_xpath(
                "//div[text()='Likes']/following-sibling::div")

            scroll_it = True
            try_again = 0

            while scroll_it != False and boundary != 0:
                scroll_it = browser.execute_script('''
                    var div = arguments[0];
                    if (div.offsetHeight + div.scrollTop < div.scrollHeight) {
                        div.scrollTop = div.scrollHeight;
                        return true;}
                    else {
                        return false;}
                    ''', dialog)

                if scroll_it == True:
                    update_activity()

                if sc_rolled > 91 or too_many_requests > 1:  # old value 100
                    logger.info("Too Many Requests sent! ~will sleep some :>")
                    sleep_actual(600)
                    sc_rolled = 0
                    too_many_requests = 0 if too_many_requests >= 1 else too_many_requests

                else:
                    sleep_actual(1.2)  # old value 5.6
                    sc_rolled += 1

                tmp_list = browser.find_elements_by_xpath(
                    "//a[contains(@class, 'FPmhX')]")

                if boundary is not None:
                    if len(tmp_list) >= boundary:
                        break

                if (scroll_it == False and
                        likers_count and
                        likers_count - 1 > len(tmp_list)):

                    if ((boundary is not None and likers_count - 1 > boundary) or
                            boundary is None):

                        if try_again <= 1:  # you can increase the amount of tries here
                            logger.info("Cor! ~failed to get the desired amount of usernames, "
                                        "trying again!  |  post:{}  |  attempt: {}".format(
                                posts, try_again + 1))
                            try_again += 1
                            too_many_requests += 1
                            scroll_it = True
                            nap_it = 4 if try_again == 0 else 7
                            sleep_actual(nap_it)

            tmp_list = browser.find_elements_by_xpath(
                "//a[contains(@class, 'FPmhX')]")

            logger.info("Post {}  |  Likers: found {}, catched {}".format(
                count, likers_count, len(tmp_list)))

        except NoSuchElementException:
            try:
                tmp_list = browser.find_elements_by_xpath(
                    "//div[contains(@class, '_1xe_U')]/a")

                if len(tmp_list) > 0:
                    logger.info("Post {}  |  Likers: found {}, catched {}".format(count, len(tmp_list), len(tmp_list)))

            except NoSuchElementException:
                logger.error('There is some error searching active users')

        if len(tmp_list) is not 0:
            for user in tmp_list:
                active_users.append(user.text)

        sleep_actual(1)

        # if not reached posts(parameter) value, continue
        if count + 1 != posts + 1 and count != 0:
            try:
                # click next button
                next_button = browser.find_element_by_xpath(
                    "//a[contains(@class, 'HBoOv')]"
                    "[text()='Next']")
                click_element(browser, next_button)

            except:
                logger.error('Unable to go to next profile post')

    real_time = time.time()
    diff_in_minutes = int((real_time - start_time) / 60)
    diff_in_seconds = int((real_time - start_time) % 60)

    # delete duplicated users
    active_users = list(set(active_users))

    logger.info("Gathered total of {} unique active followers from the latest {}"
                "posts in {} minutes and {} seconds".format(len(active_users),
                                                            posts,
                                                            diff_in_minutes,
                                                            diff_in_seconds))

    return active_users


def delete_line_from_file(filepath, userToDelete, logger):
    """ Remove user's record from the followed pool file after unfollowing """
    if not os.path.isfile(filepath):
        # in case of there is no any followed pool file yet
        return 0

    try:
        file_path_old = filepath + ".old"
        file_path_Temp = filepath + ".temp"

        with open(filepath, "r") as f:
            lines = f.readlines()

        with open(file_path_Temp, "w") as f:
            for line in lines:
                entries = line.split(" ~ ")
                sz = len(entries)
                if sz == 1:
                    user = entries[0][:-2]
                elif sz == 2:
                    user = entries[1][:-2]
                else:
                    user = entries[1]

                if user == userToDelete:
                    logger.info("\tRemoved '{}' from {} file".format(line.split(',\n')[0], filepath))
                else:
                    f.write(line)

        # File leftovers that should not exist, but if so remove it
        while os.path.isfile(file_path_old):
            try:
                os.remove(file_path_old)
            except OSError as e:
                logger.error("Can't remove file_path_old {}".format(str(e)))
                sleep(5)

        # rename original file to _old
        os.rename(filepath, file_path_old)
        # rename new temp file to filepath
        while os.path.isfile(file_path_Temp):
            try:
                os.rename(file_path_Temp, filepath)
            except OSError as e:
                logger.error("Can't rename file_path_Temp to filepath {}".format(str(e)))
                sleep(5)

        # remove old and temp file
        os.remove(file_path_old)

    except BaseException as e:
        logger.error("delete_line_from_file error {}\n{}".format(str(e).encode("utf-8")))


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


def click_element(browser, element, tryNum=0):
    # There are three (maybe more) different ways to "click" an element/button.
    # 1. element.click()
    # 2. element.send_keys("\n")
    # 3. browser.execute_script("document.getElementsByClassName('" + element.get_attribute("class") + "')[0].click()")

    # I'm guessing all three have their advantages/disadvantages
    # Before committing over this code, you MUST justify your change
    # and potentially adding an 'if' statement that applies to your
    # specific case. See the following issue for more details
    # https://github.com/timgrossmann/InstaPy/issues/1232

    # explaination of the following recursive function:
    #   we will attempt to click the element given, if an error is thrown
    #   we know something is wrong (element not in view, element doesn't
    #   exist, ...). on each attempt try and move the screen around in
    #   various ways. if all else fails, programmically click the button
    #   using `execute_script` in the browser.

    try:
        # use Selenium's built in click function
        element.click()

        # update server calls after a successful click by selenium
        update_activity()

    except:
        # click attempt failed
        # try something funky and try again

        if tryNum == 0:
            # try scrolling the element into view
            browser.execute_script("document.getElementsByClassName('" + element.get_attribute(
                "class") + "')[0].scrollIntoView({ inline: 'center' });")

        elif tryNum == 1:
            # well, that didn't work, try scrolling to the top and then clicking again
            browser.execute_script("window.scrollTo(0,0);")

        elif tryNum == 2:
            # that didn't work either, try scrolling to the bottom and then clicking again
            browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")

        else:
            # try `execute_script` as a last resort
            # print("attempting last ditch effort for click, `execute_script`")
            browser.execute_script(
                "document.getElementsByClassName('" + element.get_attribute("class") + "')[0].click()")
            # update server calls after last click attempt by JS
            update_activity()
            # end condition for the recursive function
            return

        # update server calls after the scroll(s) in 0, 1 and 2 attempts
        update_activity()

        # sleep for 1 second to allow window to adjust (may or may not be needed)
        sleep_actual(1)

        tryNum += 1

        # try again!
        click_element(browser, element, tryNum)


def format_number(number):
    """
    Format number. Remove the unused comma. Replace the concatenation with relevant zeros. Remove the dot.

    :param number: str

    :return: int
    """
    formatted_num = number.replace(',', '')
    formatted_num = re.sub(r'(k)$', '00' if '.' in formatted_num else '000', formatted_num)
    formatted_num = re.sub(r'(m)$', '00000' if '.' in formatted_num else '000000', formatted_num)
    formatted_num = formatted_num.replace('.', '')
    return int(formatted_num)


def username_url_to_username(username_url):
    a = username_url.replace("https://www.instagram.com/", "")
    username = a.split('/')
    return username[0]


def get_number_of_posts(browser):
    """Get the number of posts from the profile screen"""
    num_of_posts_txt = browser.find_element_by_xpath("//section/main/div/header/section/ul/li[1]/span/span").text
    num_of_posts_txt = num_of_posts_txt.replace(" ", "")
    num_of_posts_txt = num_of_posts_txt.replace(",", "")
    num_of_posts = int(num_of_posts_txt)
    return num_of_posts


def get_relationship_counts(browser, username, logger):
    """ Gets the followers & following counts of a given user """

    user_link = "https://www.instagram.com/{}/".format(username)

    # check URL of the webpage, if it already is user's profile page, then do not navigate to it again
    web_address_navigator(browser, user_link)

    try:
        followers_count = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].graphql.user.edge_followed_by.count")

    except WebDriverException:
        try:
            followers_count = format_number(browser.find_element_by_xpath("//a[contains"
                                                                          "(@href,'followers')]/span").text)
        except NoSuchElementException:
            try:
                browser.execute_script("location.reload()")
                update_activity()

                followers_count = browser.execute_script(
                    "return window._sharedData.entry_data."
                    "ProfilePage[0].graphql.user.edge_followed_by.count")

            except WebDriverException:
                try:
                    topCount_elements = browser.find_elements_by_xpath(
                        "//span[contains(@class,'g47SY')]")

                    if topCount_elements:
                        followers_count = format_number(topCount_elements[1].text)

                    else:
                        logger.info("Failed to get followers count of '{}'  ~empty list".format(username))
                        followers_count = None

                except NoSuchElementException:
                    logger.error("Error occured during getting the followers count of '{}'\n".format(username))
                    followers_count = None

    try:
        following_count = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].graphql.user.edge_follow.count")

    except WebDriverException:
        try:
            following_count = format_number(browser.find_element_by_xpath("//a[contains"
                                                                          "(@href,'following')]/span").text)

        except NoSuchElementException:
            try:
                browser.execute_script("location.reload()")
                update_activity()

                following_count = browser.execute_script(
                    "return window._sharedData.entry_data."
                    "ProfilePage[0].graphql.user.edge_follow.count")

            except WebDriverException:
                try:
                    topCount_elements = browser.find_elements_by_xpath(
                        "//span[contains(@class,'g47SY')]")

                    if topCount_elements:
                        following_count = format_number(topCount_elements[2].text)

                    else:
                        logger.info("Failed to get following count of '{}'  ~empty list".format(username))
                        following_count = None

                except NoSuchElementException:
                    logger.error("\nError occured during getting the following count of '{}'\n".format(username))
                    following_count = None

    return followers_count, following_count


def web_address_navigator(browser, link):
    """Checks and compares current URL of web page and the URL to be navigated and if it is different, it does navigate"""
    current_url = get_current_url(browser)
    total_timeouts = 0
    page_type = None  # file or directory

    # remove slashes at the end to compare efficiently
    if current_url is not None and current_url.endswith('/'):
        current_url = current_url[:-1]

    if link.endswith('/'):
        link = link[:-1]
        page_type = "dir"  # slash at the end is a directory

    new_navigation = (current_url != link)

    if current_url is None or new_navigation:
        link = link + '/' if page_type == "dir" else link  # directory links navigate faster

        while True:
            try:
                browser.get(link)
                # update server calls
                update_activity()
                sleep(2)
                break

            except TimeoutException as exc:
                if total_timeouts >= 7:
                    raise TimeoutException("Retried {} times to GET '{}' webpage "
                                           "but failed out of a timeout!\n\t{}".format(total_timeouts,
                                                                                       str(link).encode("utf-8"),
                                                                                       str(exc).encode("utf-8")))
                total_timeouts += 1
                sleep(2)


@contextmanager
def interruption_handler(SIG_type=signal.SIGINT, handler=signal.SIG_IGN, notify=None, logger=None):
    """ Handles external interrupt, usually initiated by the user like KeyboardInterrupt with CTRL+C """
    if notify is not None and logger is not None:
        logger.warning(notify)

    original_handler = signal.signal(SIG_type, handler)

    try:
        yield

    finally:
        signal.signal(SIG_type, original_handler)


def highlight_print(username=None, message=None, priority=None, level=None, logger=None):
    """ Print headers in a highlighted style """
    # can add other highlighters at other priorities enriching this function

    # find the number of chars needed off the length of the logger message
    output_len = 28 + len(username) + 3 + len(message)

    if priority in ["initialization", "end"]:
        # OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
        # E.g.:          Session started!
        # oooooooooooooooooooooooooooooooooooooooooooooooo
        upper_char = "O"
        lower_char = "o"

    elif priority == "login":
        # ................................................
        # E.g.:        Logged in successfully!
        # ''''''''''''''''''''''''''''''''''''''''''''''''
        upper_char = "."
        lower_char = "'"

    elif priority == "feature":  # feature highlighter
        # ________________________________________________
        # E.g.:    Starting to interact by users..
        # """"""""""""""""""""""""""""""""""""""""""""""""
        upper_char = "_"
        lower_char = "\""

    print("\n{}".format(upper_char * output_len))

    if level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "critical":
        logger.critical(message)

    print("{}".format(lower_char * output_len))


def remove_duplicates(container, keep_order, logger):
    """ Remove duplicates from all kinds of data types easily """
    # add support for data types as needed in future
    # currently only 'list' data type is supported
    if type(container) == list:
        if keep_order == True:
            result = sorted(set(container), key=container.index)

        else:
            result = set(container)

    else:
        logger.warning("The given data type- '{}' is not supported "
                       "in `remove_duplicates` function, yet!"
                       .format(type(container)))
        result = container

    return result


def dump_record_activity(profile_name, logger, logfolder):
    """ Dump the record activity data to a local human-readable JSON """

    try:
        # get a DB and start a connection
        db, id = get_database()
        conn = sqlite3.connect(db)

        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute("SELECT * FROM recordActivity WHERE profile_id=:var", {"var": id})
            user_data = cur.fetchall()

        if user_data:
            ordered_user_data = {}
            current_data = {}

            # get the existing data
            filename = "{}recordActivity.json".format(logfolder)
            if os.path.isfile(filename):
                with open(filename) as recordActFile:
                    current_data = json.load(recordActFile)

            # re-order live user data in the required structure
            for hourly_data in user_data:
                hourly_data = tuple(hourly_data)
                day = hourly_data[-1][:10]
                hour = hourly_data[-1][-8:-6]

                if day not in ordered_user_data.keys():
                    ordered_user_data.update({day: {}})

                ordered_user_data[day].update({hour: {"likes": hourly_data[1],
                                                      "comments": hourly_data[2],
                                                      "follows": hourly_data[3],
                                                      "unfollows": hourly_data[4],
                                                      "server_calls": hourly_data[5]}})

            # update user data with live data whilst preserving all other data (keys)
            current_data.update({profile_name: ordered_user_data})

            # dump the fresh record data to a local human readable JSON
            with open(filename, 'w') as recordActFile:
                json.dump(current_data, recordActFile)

    except Exception as exc:
        logger.error("Pow! Error occured while dumping record activity data to a local JSON:\n\t{}".format(
            str(exc).encode("utf-8")))

    finally:
        if conn:
            # close the open connection
            conn.close()


def ping_server(host, logger):
    """
    Return True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    logger.info("Pinging '{}' to check the connectivity...".format(str(host)))

    # ping command count option as function of OS
    param = "-n" if system().lower() == "windows" else "-c"
    # building the command. Ex: "ping -c 1 google.com"
    command = ' '.join(["ping", param, '1', str(host)])
    need_sh = False if system().lower() == "windows" else True

    # pinging
    ping_attempts = 2
    connectivity = None

    while connectivity != True and ping_attempts > 0:
        connectivity = call(command, shell=need_sh) == 0

        if connectivity == False:
            logger.warning("Pinging the server again!\t~total attempts left: {}"
                           .format(ping_attempts))
            ping_attempts -= 1
            sleep(5)

    if connectivity == False:
        logger.critical("There is no connection to the '{}' server!".format(host))
        return False

    return True


def emergency_exit(browser, username, logger):
    """ Raise emergency if the is no connection to server OR if user is not logged in """
    using_proxy = True if Settings.connection_type == "proxy" else False
    # ping the server only if connected directly rather than through a proxy
    if not using_proxy:
        server_address = "instagram.com"
        connection_state = ping_server(server_address, logger)
        if connection_state == False:
            return True, "not connected"

    # check if the user is logged in
    auth_method = "activity counts"
    login_state = check_authorization(browser, username, auth_method, logger)
    if login_state == False:
        return True, "not logged in"

    return False, "no emergency"


def load_user_id(username, person, logger, logfolder):
    """ Load the user ID at reqeust from local records """
    pool_name = "{0}{1}_followedPool.csv".format(logfolder, username)
    user_id = "undefined"

    try:
        with open(pool_name, 'r+') as followedPoolFile:
            reader = csv.reader(followedPoolFile)

            for row in reader:
                entries = row[0].split(' ~ ')
                if len(entries) < 3:
                    # old entry which does not contain an ID
                    pass

                user_name = entries[1]
                if user_name == person:
                    user_id = entries[2]
                    break

        followedPoolFile.close()

    except BaseException as exc:
        logger.exception("Failed to load the user ID of '{}'!\n{}".format(person, str(exc).encode("utf-8")))

    return user_id


def check_authorization(browser, username, method, logger):
    """ Check if user is NOW logged in """
    logger.info("Checking if '{}' is logged in...".format(username))

    # different methods can be added in future
    if method == "activity counts":

        profile_link = 'https://www.instagram.com/{}/'.format(username)
        web_address_navigator(browser, profile_link)

        # if user is not logged in, `activity_counts` will be `None`- JS `null`
        try:
            activity_counts = browser.execute_script(
                "return window._sharedData.activity_counts")

        except WebDriverException:
            try:
                browser.execute_script("location.reload()")
                update_activity()

                activity_counts = browser.execute_script(
                    "return window._sharedData.activity_counts")

            except WebDriverException:
                activity_counts = None

        # if user is not logged in, `activity_counts_new` will be `None`- JS `null`
        try:
            activity_counts_new = browser.execute_script(
                "return window._sharedData.config.viewer")

        except WebDriverException:
            try:
                browser.execute_script("location.reload()")
                activity_counts_new = browser.execute_script(
                    "return window._sharedData.config.viewer")

            except WebDriverException:
                activity_counts_new = None

        if activity_counts is None and activity_counts_new is None:
            logger.critical("--> '{}' is not logged in!\n".format(username))
            return False

    return True


def get_username(browser, track, logger):
    """ Get the username of a user from the loaded profile page """
    if track == "profile":
        query = "return window._sharedData.entry_data. \
                    ProfilePage[0].graphql.user.username"

    elif track == "post":
        query = "return window._sharedData.entry_data. \
                    PostPage[0].graphql.shortcode_media.owner.username"

    try:
        username = browser.execute_script(query)

    except WebDriverException:
        try:
            browser.execute_script("location.reload()")
            update_activity()

            username = browser.execute_script(query)

        except WebDriverException:
            current_url = get_current_url(browser)
            logger.info("Failed to get the username from '{}' page".format(current_url or
                                                                           "user" if track == "profile" else "post"))
            username = None

    # in future add XPATH ways of getting username

    return username


def find_user_id(browser, track, username, logger):
    """  Find the user ID from the loaded page """
    if track in ["dialog", "profile"]:
        query = "return window._sharedData.entry_data.ProfilePage[0].graphql.user.id"

    elif track == "post":
        query = "return window._sharedData.entry_data.PostPage[0].graphql.shortcode_media.owner.id"
        meta_XP = "//meta[@property='instapp:owner_user_id']"

    failure_message = "Failed to get the user ID of '{}' from {} page!".format(username, track)

    try:
        user_id = browser.execute_script(query)

    except WebDriverException:
        try:
            browser.execute_script("location.reload()")
            update_activity()

            user_id = browser.execute_script(query)

        except WebDriverException:
            if track == "post":
                try:
                    user_id = browser.find_element_by_xpath(meta_XP).get_attribute("content")
                    if user_id:
                        user_id = format_number(user_id)

                    else:
                        logger.error("{}\t~empty string".format(failure_message))
                        user_id = None

                except NoSuchElementException:
                    logger.error(failure_message)
                    user_id = None

            else:
                logger.error(failure_message)
                user_id = None

    return user_id


@contextmanager
def new_tab(browser):
    """ USE once a host tab must remain untouched and yet needs extra data- get from guest tab """
    try:
        # add a guest tab
        browser.execute_script("window.open()")
        sleep(1)
        # switch to the guest tab
        browser.switch_to.window(browser.window_handles[1])
        sleep(2)
        yield

    finally:
        # close the guest tab
        browser.execute_script("window.close()")
        sleep(1)
        # return to the host tab
        browser.switch_to.window(browser.window_handles[0])
        sleep(2)


def explicit_wait(browser, track, ec_params, logger, timeout=35, notify=True):
    """
    Explicitly wait until expected condition validates

    :param browser: webdriver instance
    :param track: short name of the expected condition
    :param ec_params: expected condition specific parameters - [param1, param2]
    :param logger: the logger instance
    """
    # list of available tracks:
    # <https://seleniumhq.github.io/selenium/docs/api/py/webdriver_support/
    # selenium.webdriver.support.expected_conditions.html>

    if not isinstance(ec_params, list):
        ec_params = [ec_params]

    # find condition according to the tracks
    if track == "VOEL":
        elem_address, find_method = ec_params
        ec_name = "visibility of element located"

        find_by = (By.XPATH if find_method == "XPath" else
                   By.CSS_SELECTOR if find_method == "CSS" else
                   By.CLASS_NAME)
        locator = (find_by, elem_address)
        condition = ec.visibility_of_element_located(locator)

    elif track == "TC":
        expect_in_title = ec_params[0]
        ec_name = "title contains '{}' string".format(expect_in_title)

        condition = ec.title_contains(expect_in_title)

    elif track == "PFL":
        ec_name = "page fully loaded"
        condition = (lambda browser: browser.execute_script("return document.readyState")
                                     in ["complete" or "loaded"])

    # generic wait block
    try:
        wait = WebDriverWait(browser, timeout)
        result = wait.until(condition)

    except TimeoutException:
        if notify == True:
            logger.info("Timed out with failure while explicitly waiting until {}!\n"
                        .format(ec_name))
        return False

    return result


def get_current_url(browser):
    """ Get URL of the loaded webpage """
    try:
        current_url = browser.execute_script("return window.location.href")

    except WebDriverException:
        try:
            current_url = browser.current_url

        except WebDriverException:
            current_url = None

    return current_url


def get_username_from_id(browser, user_id, logger):
    """ Convert user ID to username """
    # method using graphql 'Account media' endpoint
    logger.info("Trying to find the username from the given user ID by loading a post")

    query_hash = "42323d64886122307be10013ad2dcc44"  # earlier- "472f257a40c653c64c666ce877d59d2b"
    graphql_query_URL = "https://www.instagram.com/graphql/query/?query_hash={}".format(query_hash)
    variables = {"id": str(user_id), "first": 1}
    post_url = u"{}&variables={}".format(graphql_query_URL, str(json.dumps(variables)))

    web_address_navigator(browser, post_url)
    pre = browser.find_element_by_tag_name("pre").text
    user_data = json.loads(pre)["data"]["user"]

    if user_data:
        user_data = user_data["edge_owner_to_timeline_media"]

        if user_data["edges"]:
            post_code = user_data["edges"][0]["node"]["shortcode"]
            post_page = "https://www.instagram.com/p/{}".format(post_code)

            web_address_navigator(browser, post_page)
            username = get_username(browser, "post", logger)
            if username:
                return username

        else:
            if user_data["count"] == 0:
                logger.info("Profile with ID {}: no pics found".format(user_id))

            else:
                logger.info("Can't load pics of a private profile to find username (ID: {})".format(user_id))

    else:
        logger.info("No profile found, the user may have blocked you (ID: {})".format(user_id))
        return None

    # method using private API
    logger.info("Trying to find the username from the given user ID by a quick API call")

    req = requests.get(u"https://i.instagram.com/api/v1/users/{}/info/"
                       .format(user_id))
    if req:
        data = json.loads(req.text)
        if data["user"]:
            username = data["user"]["username"]
            return username

    # method using graphql 'Follow' endpoint
    logger.info("Trying to find the username from the given user ID "
                "by using the GraphQL Follow endpoint")

    user_link_by_id = ("https://www.instagram.com/web/friendships/{}/follow/"
                       .format(user_id))

    web_address_navigator(browser, user_link_by_id)
    username = get_username(browser, "profile", logger)

    return username


def is_page_available(browser, logger):
    """ Check if the page is available and valid """
    # wait for the current page fully load
    explicit_wait(browser, "PFL", [], logger, 10)

    try:
        page_title = browser.title

    except WebDriverException:
        try:
            page_title = browser.execute_script("return document.title")

        except WebDriverException:
            try:
                page_title = browser.execute_script(
                    "return document.getElementsByTagName('title')[0].text")

            except WebDriverException:
                logger.info("Unable to find the title of the page :(")
                return True

    expected_keywords = ["Page Not Found", "Content Unavailable"]
    if any(keyword in page_title for keyword in expected_keywords):
        if "Page Not Found" in page_title:
            logger.warning("The page isn't available!\t~the link may be broken, or the page may have been removed...")

        elif "Content Unavailable" in page_title:
            logger.warning("The page isn't available!\t~the user may have blocked you...")

        return False

    return True


@contextmanager
def smart_run(session):
    try:
        session.login()
        yield

    except (Exception, KeyboardInterrupt) as exc:
        if isinstance(exc, NoSuchElementException):
            # the problem is with a change in IG page layout
            log_file = "{}.html".format(time.strftime("%Y%m%d-%H%M%S"))
            file_path = os.path.join(gettempdir(), log_file)
            with open(file_path, "wb") as fp:
                fp.write(session.browser.page_source.encode("utf-8"))
            print("{0}\nIf raising an issue, "
                  "please also upload the file located at:\n{1}\n{0}"
                  .format('*' * 70, file_path))

        # provide full stacktrace (else than external interrupt)
        if isinstance(exc, KeyboardInterrupt):
            clean_exit("You have exited successfully.")

        else:
            raise

    finally:
        session.end()
