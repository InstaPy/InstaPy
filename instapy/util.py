import csv
import json
import datetime
import os
import re
import sqlite3
import time
import signal
from contextlib import contextmanager

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

from .time_util import sleep
from .time_util import sleep_actual
from .database_engine import get_database

def is_private_profile(browser, logger, following=True, username=None):
    if username is not None:
        profile_page = 'https://www.instagram.com/{}/'.format(username)
        web_adress_navigator(browser, profile_page)
    try:
        is_private = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].graphql.user.is_private")
    except WebDriverException:   # handle the possible `entry_data` error
        try:
            browser.execute_script("location.reload()")
            is_private = browser.execute_script(
                "return window._sharedData.entry_data."
                "ProfilePage[0].graphql.user.is_private")
        except WebDriverException:
            is_private = None

    # double check with xpath that should work only when we not following a user
    if is_private is True and not following:
        try:
            logger.info("Is private account you're not following.")
            body_elem = browser.find_element_by_tag_name('body')
            is_private = body_elem.find_element_by_xpath(
                '//h2[@class="_kcrwx"]')
        except NoSuchElementException:
            logger.info("Failed to double check with xpath if is a private profile")

    return is_private


def media_count(browser, username):
    link = 'https://www.instagram.com/{}/'.format(username)
    web_adress_navigator(browser, link)
    try:
        media_c = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].graphql.user.edge_owner_to_timeline_media.count")
    except WebDriverException:   # handle the possible `entry_data` error
        try:
            browser.execute_script("location.reload()")
            media_c = browser.execute_script(
                "return window._sharedData.entry_data."
                "ProfilePage[0].graphql.user.edge_owner_to_timeline_media.count")
        except WebDriverException:
            media_c = None
    return media_c


def have_profile_pic(browser, username, logger, logging_enabled):
    link = 'https://www.instagram.com/{}/'.format(username)
    default_image = "11906329_960233084022564_1448528159_a.jpg"
    web_adress_navigator(browser, link)
    try:
        url = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].graphql.user.profile_pic_url")
    except WebDriverException:   # handle the possible `entry_data` error
        try:
            browser.execute_script("location.reload()")
            url = browser.execute_script(
                "return window._sharedData.entry_data."
                "ProfilePage[0].graphql.user.profile_pic_url")
        except WebDriverException:
            url = ""
    if logging_enabled:
        logger.info("Profile pic: {}".format(url))
    return default_image not in url
               "---> Username '{}' is yours!  ~skipping user\n".format(own_username)

    if username in ignore_users:
        return False, \
               "---> User {} is in ignore_users list  ~skipping user\n".format(username)

    if username in blacklist:
        return False, \
               "---> User {} is in blacklist  ~skipping user\n".format(username)

    is_private = is_private_profile(browser, logger, following=True, username=username)

    if skip_private:
        if is_private:
            return False, \
                   "---> User {} is private ~skipping user\n".format(username)

    media_c = media_count(browser, username)

    if media_c:
        if min_media != 0 and max_media != 0:
            if max_media == -1:
                if media_c < min_media:
                    return False, \
                           "---> User {} have {} posts, min_media is {} max_media is {} ~skipping user\n".format(
                               username,
                               media_c,
                               min_media,
                               "No limit")
            else:
                if media_c > max_media or media_c < min_media:
                    return False, \
                           "---> User {} have {} posts, min_media is {} max_media is {} ~skipping user\n".format(
                               username,
                               media_c,
                               min_media,
                               max_media)

    if skip_no_profile_pic:
        user_have_profile_pic = have_profile_pic(browser, username, logger, logging_enabled)
        if not user_have_profile_pic:
            return False, \
                   "---> User {} don't have a profile pic ~skipping user\n".format(username)

    """Checks the potential of target user by relationship status in order to delimit actions
     within the desired boundary"""
    if potency_ratio or max_relationship_ratio or delimit_by_numbers and \
            (max_followers or max_following or min_followers or min_following):
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

            if relationship_ratio > max_relationship_ratio:
                return False, \
                       "---> User {}'s relationship ratio {} exceeds maximum limit of {}  ~skipping user\n".format(
                           username, float("{0:.2f}".format(relationship_ratio)),
                           float("{0:.2f}".format(max_relationship_ratio)))

        # not sure about this. Could be also that failed to get data from profile.
        if not media_c and not followers_count and not following_count and not relationship_ratio:
            return False, \
                   "---> User {} seems not existing anymore\n".format(username)

        if followers_count or following_count:
            if potency_ratio and not delimit_by_numbers:
                if relationship_ratio and relationship_ratio < potency_ratio:
                    return False, \
                           "---> User {} is not a {} with the relationship ratio of {}  ~skipping user\n".format(
                               username, "potential user" if not reverse_relationship else "massive follower",
                               float("{0:.2f}".format(relationship_ratio)))

            elif delimit_by_numbers:
                if followers_count:
                    if max_followers:
                        if followers_count > max_followers:
                            return False, \
                                   "---> User {}'s followers count exceeds maximum limit  ~skipping user\n"\
                                   .format(username)
                    if min_followers:
                        if followers_count < min_followers:
                            return False, \
                                   "---> User {}'s followers count is less than minimum limit  ~skipping user\n"\
                                   .format(username)
                if following_count:
                    if max_following:
                        if following_count > max_following:
                            return False, \
                                   "---> User {}'s following count exceeds maximum limit  ~skipping user\n"\
                                   .format(username)
                    if min_following:
                        if following_count < min_following:
                            return False, \
                                   "---> User {}'s following count is less than minimum limit  ~skipping user\n"\
                                   .format(username)
                if potency_ratio:
                    if relationship_ratio and relationship_ratio < potency_ratio:
                        return False, \
                               "---> User {} is not a {} with the relationship ratio of {}  ~skipping user\n".format(
                                   username, "potential user" if not reverse_relationship else "massive follower",
                                   float("{0:.2f}".format(relationship_ratio)))

        logger.info('User: {} >> media: {}  |  followers: {}  |  following: {}  |  relationship ratio: {}'.format(
            username,
            media_c if media_c else 'unknown',
            followers_count if followers_count else 'unknown',
            following_count if following_count else 'unknown',
            float("{0:.2f}".format(relationship_ratio)) if relationship_ratio else 'unknown'))

    # if everything ok
    return True, "Valid user"



def update_activity(action=None):
    """ Record every Instagram server call (page load, content load, likes,
        comments, follows, unfollow). """

    # get a DB and start a connection
    db, id = get_database()
    conn = sqlite3.connect(db)

    with conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        # collect today data
        cur.execute("SELECT * FROM recordActivity WHERE profile_id=:var AND created == date('now')", {"var":id})
        data = cur.fetchone()

        if data is None:
            # create a new record for the new day
            cur.execute("INSERT INTO recordActivity VALUES "
                        "(?, 0, 0, 0, 0, 1, date('now'))", (id,))
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

            sql = ("UPDATE recordActivity set likes = ?, comments = ?, "
                   "follows = ?, unfollows = ?, server_calls = ? "
                   "WHERE profile_id=? AND created = date('now')")
            cur.execute(sql, (data['likes'], data['comments'], data['follows'],
                              data['unfollows'], data['server_calls'], id))

        # commit the latest changes
        conn.commit()

def add_user_to_blacklist(username, campaign, action, logger, logfolder):

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



def get_active_users(browser, username, posts, boundary, logger):
    """Returns a list with usernames who liked the latest n posts"""

    user_link = 'https://www.instagram.com/{}/'.format(username)

    #Check URL of the webpage, if it already is user's profile page, then do not navigate to it again
    web_adress_navigator(browser, user_link)

    try:
        total_posts = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].graphql.user.edge_owner_to_timeline_media.count")
    except WebDriverException:
        try:
            total_posts = format_number(browser.find_elements_by_xpath(
                "//span[contains(@class,'g47SY')]")[0].text)
            if total_posts: #prevent an empty string scenario
                total_posts = format_number(total_posts)
            else:
                logger.info("Failed to get posts count on your profile!  ~empty string")
                total_posts = None
        except NoSuchElementException:
            logger.info("Failed to get posts count on your profile!")
            total_posts = None

    # if posts > total user posts, assume total posts
    posts = posts if total_posts is None else total_posts if posts > total_posts else posts

    # click latest post
    browser.find_elements_by_xpath(
        "//div[contains(@class, '_9AhH0')]")[0].click()

    active_users = []
    sc_rolled = 0
    start_time = time.time()
    too_many_requests = 0  # this will help to prevent misbehaviours when you request the list of active users repeatedly within less than 10 min of breaks

    message = (("~collecting the entire usernames from posts without a boundary!\n") if boundary is None else
               (
               "~collecting only the visible usernames from posts without scrolling at the boundary of zero..\n") if boundary == 0 else
               ("~collecting the usernames from posts with the boundary of {}\n".format(boundary)))
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
                    if likers_count: ##prevent an empty string scenarios
                        likers_count = format_number(likers_count)
                    else:
                        logger.info("Failed to get likers count on your post {}  ~empty string".format(count))
                        likers_count = None
                except NoSuchElementException:
                    logger.info("Failed to get likers count on your post {}".format(count))
                    likers_count = None

            browser.find_element_by_xpath(
                "//a[contains(@class, 'zV_Nj')]").click()
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
                            logger.info(
                                "Cor! ~failed to get the desired amount of usernames, trying again!  |  post:{}  |  attempt: {}".format(
                                    posts, try_again + 1))
                            try_again += 1
                            too_many_requests += 1
                            scroll_it = True
                            nap_it = 4 if try_again == 0 else 7
                            sleep_actual(nap_it)

            tmp_list = browser.find_elements_by_xpath(
                "//a[contains(@class, 'FPmhX')]")
            logger.info("Post {}  |  Likers: found {}, catched {}".format(count, likers_count, len(tmp_list)))

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
        if count +1 != posts +1 and count != 0:
            try:
                # click next button
                browser.find_element_by_xpath(
                    "//a[contains(@class, 'HBoOv')]"
                    "[text()='Next']").click()
            except:
                logger.error('Unable to go to next profile post')

    real_time = time.time()
    diff_in_minutes = int((real_time - start_time) / 60)
    diff_in_seconds = int((real_time - start_time) % 60)
    # delete duplicated users
    active_users = list(set(active_users))
    logger.info(
        "Gathered total of {} unique active followers from the latest {} posts in {} minutes and {} seconds".format(len(active_users),
                                                                                                     posts,
                                                                                                     diff_in_minutes,
                                                                                                     diff_in_seconds))

    return active_users



def delete_line_from_file(filepath, lineToDelete, logger):
    try:
        file_path_old = filepath+".old"
        file_path_Temp = filepath+".temp"

        f = open(filepath, "r")
        lines = f.readlines()
        f.close()

        f = open(file_path_Temp, "w")
        for line in lines:
            if not line.endswith(lineToDelete):
                f.write(line)
            else:
                logger.info("\tRemoved '{}' from followedPool.csv file".format(line.split(',\n')[0]))
        f.close()

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
    a = username_url.replace ("https://www.instagram.com/","")
    username = a.split ('/')
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

    #Check URL of the webpage, if it already is user's profile page, then do not navigate to it again
    web_adress_navigator(browser, user_link)

    try:
        followers_count = format_number(browser.find_element_by_xpath("//a[contains"
                                "(@href,'followers')]/span").text)
    except NoSuchElementException:
        try:
            followers_count = browser.execute_script(
                "return window._sharedData.entry_data."
                "ProfilePage[0].graphql.user.edge_followed_by.count")
        except WebDriverException:
            try:
                browser.execute_script("location.reload()")
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
        following_count = format_number(browser.find_element_by_xpath("//a[contains"
                                "(@href,'following')]/span").text)
    except NoSuchElementException:
        try:
            following_count = browser.execute_script(
                "return window._sharedData.entry_data."
                "ProfilePage[0].graphql.user.edge_follow.count")
        except WebDriverException:
            try:
                browser.execute_script("location.reload()")
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



def web_adress_navigator(browser, link):
    """Checks and compares current URL of web page and the URL to be navigated and if it is different, it does navigate"""

    try:
        current_url = browser.current_url
    except WebDriverException:
        try:
            current_url = browser.execute_script("return window.location.href")
        except WebDriverException:
            current_url = None

    if current_url is None or current_url != link:
        browser.get(link)
        # update server calls
        update_activity()
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
    #can add other highlighters at other priorities enriching this function

    #find the number of chars needed off the length of the logger message
    output_len = 28+len(username)+3+len(message)

    if priority in ["initialization", "end"]:
        #OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
        #E.g.:          Session started!
        #oooooooooooooooooooooooooooooooooooooooooooooooo
        upper_char = "O"
        lower_char = "o"

    elif priority == "login":
        #................................................
        #E.g.:        Logged in successfully!
        #''''''''''''''''''''''''''''''''''''''''''''''''
        upper_char = "."
        lower_char = "'"

    elif priority == "feature":  #feature highlighter
        #________________________________________________
        #E.g.:    Starting to interact by users..
        #""""""""""""""""""""""""""""""""""""""""""""""""
        upper_char = "_"
        lower_char = "\""

    print("\n{}".format(upper_char*output_len))

    if level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "critical":
        logger.critical(message)

    print("{}".format(lower_char*output_len))

def remove_duplicated_from_list_keep_order(_list):
    seen = set()
    seen_add = seen.add
    return [x for x in _list if not (x in seen or seen_add(x))]

def dump_record_activity(profile_name, logger, logfolder):
    """ Dump the record activity data to a local human-readable JSON """

    try:
        # get a DB and start a connection
        db, id = get_database()
        conn = sqlite3.connect(db)

        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute("SELECT * FROM recordActivity WHERE profile_id=:var", {"var":id})
            data = cur.fetchall()

        if data:
            record_data = {}

            # get the existing data
            filename = "{}recordActivity.json".format(logfolder)
            if os.path.isfile(filename):
                with open(filename) as recordActFile:
                    current_data = json.load(recordActFile)
            else:
                current_data = {}

            # pack the new data
            for day in data:
                record_data[day[-1]] = {"likes":day[1],
                                         "comments":day[2],
                                          "follows":day[3],
                                           "unfollows":day[4],
                                            "server_calls":day[5]}
            current_data[profile_name] = record_data

            # dump the fresh record data to a local human readable JSON
            with open(filename, 'w') as recordActFile:
                json.dump(current_data, recordActFile)

    except Exception as exc:
        logger.error("Pow! Error occured while dumping record activity data to a local JSON:\n\t{}".format(str(exc).encode("utf-8")))

    finally:
        if conn:
            # close the open connection
            conn.close()



