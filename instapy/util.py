import csv
import os
from .time_util import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import sqlite3
import json
import pickle
import datetime
from langdetect import detect_langs


def validate_username(browser,
                      username,
                      ignore_users,
                      blacklist,
                      dont_include_language,
                      like_by_followers_upper_limit,
                      like_by_followers_lower_limit,
                      following_to_followers_ratio,
                      logger):
    """Check if we can interact with the user"""

    if username in ignore_users:
        return ('---> {} is in ignore_users list, skipping '
                'user...'.format(username))
    if username in blacklist:
        return '---> {} is in blacklist, skipping user...'

    #browser.find_element_by_xpath(
    #"// *[ @ id = \"react-root\"] / section / main / div / div / article / header / div[2] / div[1] / div[1] / a").click()
    #chrome_options = Options()
    #chrome_options.add_argument("--Referer={}".format(browser.current_url))
    browser.get('https://www.instagram.com/{}'.format(username))

    sleep(2)

    try:
        is_private = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].user.is_private")
        #is_private = body_elem.find_element_by_xpath(
        #    '//h2[@class="_kcrwx"]')
    except:
        logger.info('Interaction begin...')
    else:
        if is_private:
            logger.warning('This user is private...')
            return False

    if "Page Not Found" in browser.title or "Content Unavailable" in browser.title:
        logger.warning('Intagram error: The link you followed may be broken, or the page may have been removed...')
        return False

    try:
        followers = browser.execute_script(
            "return window._sharedData.entry_data.ProfilePage[0].user.followed_by.count")
        following = browser.execute_script(
            "return window._sharedData.entry_data.ProfilePage[0].user.follows.count")
    except NoSuchElementException:
        return '---> {} account is private, skipping user...'.format(username)
    except:
        logger.error('Intagram error: can not fetch followers/following number, The link you followed may be broken, or the page may have been removed...')
        return False

    if followers > like_by_followers_upper_limit:
        return '---> User {} exceeds followers limit'.format(username)
    elif followers < like_by_followers_lower_limit:
        return ('---> {}, number of followers does not reach '
                'minimum'.format(username))

    if (followers != 0) and ((following/followers) > following_to_followers_ratio):
        return ('---> {}, following/followers ratio is '
                'too high {}'.format(username, following_to_followers_ratio))

    """validate profile description language is supported"""
    if dont_include_language:
        profile_description = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].user.biography")
        profile_full_name = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].user.full_name")

        try:
            # detect language by profile description, if the description is empty detect by name
            profile_detect = ''
            if isinstance(profile_description, str):
                profile_detect = profile_description
            #elif isinstance(profile_full_name, str):
            #   profile_detect += profile_full_name

            update_activity()
            sleep(1)
            #logger.info('profile description {}'.format(profile_detect))
            languages = detect_langs(profile_detect)
            lan_list = [languages[i].lang for i in range(0, len(languages)) if languages[i].prob > 0.1]

            if set(lan_list) & set(dont_include_language):
                return 'detected unwanted language: {}'.format(languages)
            else:
                logger.info('detected wanted language: {}'.format(languages))
        except UnicodeEncodeError:
            logger.error('profile description and full_name of: {} have UnicodeEncodeError'.format(username))
        except TypeError:
            logger.info('profile description and full_name of: {} is empty'.format(username))
        except:
            logger.warning('profile description and full_name of: {} Could not detect language'.format(username))
    # if everything ok
    return True

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
        file_path_old = filepath+".old"
        file_path_Temp = filepath+".temp"

        f = open(filepath, "r")
        lines = f.readlines()
        f.close()

        f = open(file_path_Temp, "w")
        for line in lines:
            if line != lineToDelete:
                f.write(line)
            else:
                logger.info("{} removed from csv".format(line))
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


def formatNumber(number):
    formattedNum = number.replace(',', '').replace('.', '')
    formattedNum = int(formattedNum.replace('k', '00').replace('m', '00000'))
    return formattedNum

def get_follow_list(browser,
                    username,
                    logger,
                    maxAmount,
                    following,
                    followers):

    browser.get('https://www.instagram.com/' + username)

    if True:
        try:
            browser.get(
                'https://www.instagram.com/' + username + '/?__a=1')
            pre = browser.find_element_by_tag_name("pre").text
            user_data = json.loads(pre)['user']
        except BaseException as e:
            logger.warning("unable to get user information\n", str(e))

        graphql_endpoint = 'https://www.instagram.com/graphql/query/'
        graphql_followers = (
            graphql_endpoint + '?query_id=17851374694183129')
        graphql_following = (
            graphql_endpoint + '?query_id=17874545323001329')

        all_followers = []
        all_following = []
        unfollow_list = []

        variables = {}
        variables['id'] = user_data['id']
        variables['first'] = 100

        # get follower and following user loop
        try:
            if following is True:
                i = 1
                logger.info("Capturing following of user {}".format(username))
            elif followers is True:
                i = 0
                logger.info("Capturing followers of user {}".format(username))
            else:
                return 0
            has_next_data = True
            url = (
                '{}&variables={}'
                .format(graphql_followers, str(json.dumps(variables)))
            )
            if i != 0:

                url = (
                    '{}&variables={}'
                    .format(graphql_following, str(json.dumps(variables)))
                )
            sleep(2)
            browser.get(url)

            # fetch all user while still has data
            while has_next_data and len(all_followers) < maxAmount and len(all_following) < maxAmount:
                sleep(10)
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
            logger.warning(
                "unable to get followers and following information \n", str(e))

        if following is True:
            logger.info("following length captured is {}".format(str(len(all_following))))
            with open('./logs/following/' + username, 'wb') as output:
                pickle.dump(all_following, output, pickle.HIGHEST_PROTOCOL)
                return len(all_following)
        elif followers is True:
            logger.info("followers length captured is {}".format(str(len(all_followers))) )
            with open('./logs/followers/' + username, 'wb') as output:
                pickle.dump(all_followers, output, pickle.HIGHEST_PROTOCOL)
                return (len(all_followers))
