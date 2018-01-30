import csv
import os
import sys
from .time_util import sleep
from .time_util import sleep_actual
from selenium.common.exceptions import NoSuchElementException
import sqlite3
from datetime import time, timedelta, date, datetime
from time import sleep as real_sleep
import time as epoch_time
from plyer import notification
import random


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


def update_activity(action=None):
    """Record every Instagram server call (page load, content load, likes,
    comments, follows, unfollow)."""

    conn = sqlite3.connect('./db/instapy.db')
    with conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        # collect today data
        cur.execute("SELECT * FROM statistics WHERE STRFTIME('%Y-%m-%d %H', created)==STRFTIME('%Y-%m-%d %H', 'now', 'localtime')")
        data = cur.fetchone()

        if data is None:
            # create a new record for the new day
            cur.execute("INSERT INTO statistics VALUES "
                        "(0, 0, 0, 0, 1, STRFTIME('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))")
        else:
            # sqlite3.Row' object does not support item assignment -> so,
            # convert it into a new dict
            data = dict(data)
            # update
            if action != 'jumps':
                data['server_calls'] += 1
                quota_supervisor('server_calls')
            if action == 'likes':
                data['likes'] += 1
            elif action == 'comments':
                data['comments'] += 1
            elif action == 'follows':
                data['follows'] += 1
            elif action == 'unfollows':
                data['unfollows'] += 1

            sql = ("UPDATE statistics set likes = ?, comments = ?, "
                   "follows = ?, unfollows = ?, server_calls = ?, created = STRFTIME('%Y-%m-%d %H:%M:%S', 'now', 'localtime') "
                   "WHERE STRFTIME('%Y-%m-%d %H', created)==STRFTIME('%Y-%m-%d %H', 'now', 'localtime')")
            cur.execute(sql, (data['likes'], data['comments'], data['follows'],
                              data['unfollows'], data['server_calls']))
        # commit
        conn.commit()


def add_user_to_blacklist(browser, username, campaign, action, logger, logfolder):

    file_exists = os.path.isfile('{}blacklist.csv'.format(logfolder))
    fieldnames = ['date', 'username', 'campaign', 'action']
    today = date.today().strftime('%m/%d/%y')

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


def quota_supervisor(inspect):
    conn = sqlite3.connect('./db/instapy.db')   #check Quota Supervisor's state (overall execution time takes less than a second: 2 rows & 17 columns)
    with conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM QuotaPeaks WHERE recorded == (SELECT MAX(recorded) FROM QuotaPeaks)")  #selecting the latest record
        data = cur.fetchone()
        data = dict (data)

    if data['state'] == 1:  #start processing if verified
        record_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #of course, who would prefer speed of quarter of a second should disable stochastic_flow
        if data['stochastic'] == 1:
            quota_supervisor_stochastic(data, record_time)

        #inspect and act
        if inspect == 'server_calls':
            peak_server_calls_daily = data ['server_calls_d']
            peak_server_calls_hourly = data ['server_calls_h']
            if peak_server_calls_daily is not None:
                cur.execute("SELECT SUM(server_calls) FROM statistics WHERE STRFTIME('%Y-%m-%d', created)==STRFTIME('%Y-%m-%d', 'now', 'localtime')")
                fetched_data = cur.fetchone()
                if fetched_data is None:
                    update_activity('timeloop')  #this is to prevent asynchronous 'now' (23:59:59 vs 00:00:01) between update_activity and quota_supervisor realtime- very rare, but can happen
                else:
                    fetched_server_calls_daily = fetched_data[0]
                    if fetched_server_calls_daily >= peak_server_calls_daily:
                        if quota_supervisor_sleeper(protosleep=data['sleep'], interval='daily', check='server_calls') == True:
                            forward_sleep_seconds = quota_supervisor_sleeper(protosleep=data['sleep'], interval='daily')
                            print('{} - INFO - Quota Supervisor: daily server calls reached quotient.. (going to sleep {} hours long)\n~ time for IstaPy to take a big good nap :-)'.format(record_time, "%.1f" % (forward_sleep_seconds/60/60)))
                            quota_supervisor_notifier(protonotify=data['notify'], alert='sleep', job='Server calls', interval='daily')
                            real_sleep (forward_sleep_seconds)
                            quota_supervisor_notifier(protonotify=data['notify'], alert='wake up', job='Server calls', interval='daily')
                        else:
                            print('{} - INFO - QuotaSupervisor: daily server calls reached quotient.. (..exiting)\n~ for *non-stop botting add sleep_after=[\'server_calls\'] arg on the go! ;)'.format(record_time))
                            quota_supervisor_notifier(protonotify=data['notify'], alert='exit', job='Server calls', interval='daily')
                            exit()  #if peak_server_calls is fairly not None and sleep_after has no 'server_calls', Quota Supervisor will end up session.
            if peak_server_calls_hourly is not None:
                cur.execute("SELECT server_calls, created FROM statistics WHERE STRFTIME('%Y-%m-%d %H', created)==STRFTIME('%Y-%m-%d %H', 'now', 'localtime')")
                fetched_data = cur.fetchone()
                if fetched_data is None:
                    update_activity('timeloop') #this is to prevent asynchronous 'now' (59:59 vs 00:01) between update_activity and quota_supervisor realtime- rare, but can happen
                else:
                    fetched_server_calls_hourly, fetched_raw_time = fetched_data[0], fetched_data[1]
                    if fetched_server_calls_hourly >= peak_server_calls_hourly:
                        if quota_supervisor_sleeper(protosleep=data['sleep'], interval='hourly', check='server_calls') == True:
                            forward_sleep_seconds = quota_supervisor_sleeper(protosleep=data['sleep'], interval='hourly', fetched_time=fetched_raw_time)
                            print('{} - INFO - Quota Supervisor: hourly server calls reached quotient.. (going to sleep {} minutes long)\n~ take a tea break? :>'.format(record_time, "%.0f" % (forward_sleep_seconds/60)))
                            quota_supervisor_notifier(protonotify=data['notify'], alert='sleep', job='Server calls', interval='hourly')
                            real_sleep (forward_sleep_seconds)
                            quota_supervisor_notifier(protonotify=data['notify'], alert='wake up', job='Server calls', interval='hourly')
                        else:
                            print('{} - INFO - QuotaSupervisor: hourly server calls reached quotient.. (..exiting)\n~ for *non-stop botting add sleep_after=[\'server_calls\'] arg on the go! ;)'.format(record_time))
                            quota_supervisor_notifier(protonotify=data['notify'], alert='exit', job='Server calls', interval='hourly')
                            exit() #to prevent quitting after peak values reached, just enable sleep_after=['server_calls'] or just put None to server_calls's peak value(s)

        if inspect == 'likes':
            peak_likes_daily = data['likes_d']
            peak_likes_hourly = data['likes_h']
            if peak_likes_daily is not None:
                cur.execute("SELECT SUM(likes) FROM statistics WHERE STRFTIME('%Y-%m-%d', created)==STRFTIME('%Y-%m-%d', 'now', 'localtime')")
                fetched_data = cur.fetchone()
                if fetched_data is None:
                    update_activity('timeloop')
                else:
                    fetched_likes_daily = fetched_data[0]
                    if fetched_likes_daily >= peak_likes_daily:
                        if quota_supervisor_sleeper(protosleep=data['sleep'], interval='daily', check='likes') == True:
                            forward_sleep_seconds = quota_supervisor_sleeper(protosleep=data['sleep'], interval='daily')
                            print('{} - INFO - Quota Supervisor: daily likes reached quotient.. (going to sleep {} hours long)\n~ time for IstaPy to take a big good nap :-)'.format(record_time, "%.1f" % (forward_sleep_seconds/60/60)))
                            quota_supervisor_notifier(protonotify=data['notify'], alert='sleep', job='Likes', interval='daily')
                            real_sleep (forward_sleep_seconds)
                            quota_supervisor_notifier(protonotify=data['notify'], alert='wake up', job='Likes', interval='daily')
                        else:
                            print('{} - INFO - QuotaSupervisor: jumped a like out of daily quotient.. be fair with numbers, behave good! :]'.format(record_time))
                            return 'jump'
            if peak_likes_hourly is not None:
                cur.execute("SELECT likes, created FROM statistics WHERE STRFTIME('%Y-%m-%d %H', created)==STRFTIME('%Y-%m-%d %H', 'now', 'localtime')")
                fetched_data = cur.fetchone()
                if fetched_data is None:
                    update_activity('timeloop')
                else:
                    fetched_likes_hourly, fetched_raw_time = fetched_data[0], fetched_data[1]
                    if fetched_likes_hourly >= peak_likes_hourly:
                        if quota_supervisor_sleeper(protosleep=data['sleep'], interval='hourly', check='likes') == True:
                            forward_sleep_seconds = quota_supervisor_sleeper(protosleep=data['sleep'], interval='hourly', fetched_time=fetched_raw_time)
                            print('{} - INFO - Quota Supervisor: hourly likes reached quotient.. (going to sleep {} minutes long)\n~ take a tea break? :>'.format(record_time, "%.0f" % (forward_sleep_seconds/60)))
                            quota_supervisor_notifier(protonotify=data['notify'], alert='sleep', job='Likes', interval='hourly')
                            real_sleep (forward_sleep_seconds)
                            quota_supervisor_notifier(protonotify=data['notify'], alert='wake up', job='Likes', interval='hourly')
                        else:
                            print('{} - INFO - QuotaSupervisor: jumped a like out of hourly quotient.. be fair with numbers, behave good! :]'.format(record_time))
                            return 'jump'

        elif inspect == 'comments':
            peak_comments_daily = data ['comments_d']
            peak_comments_hourly = data ['comments_h']
            peak_likes_daily = data ['likes_d']
            peak_likes_hourly = data ['likes_h']
            if peak_comments_daily is not None:
                cur.execute("SELECT SUM(comments), SUM(likes) FROM statistics WHERE STRFTIME('%Y-%m-%d', created)==STRFTIME('%Y-%m-%d', 'now', 'localtime')")
                fetched_data = cur.fetchone()
                if fetched_data is None:
                    update_activity('timeloop')
                else:
                    fetched_comments_daily, fetched_likes_daily = fetched_data[0], fetched_data[1]
                    if (fetched_comments_daily >= peak_comments_daily or
                        fetched_likes_daily >= peak_likes_daily):
                        if (quota_supervisor_sleeper(protosleep=data['sleep'], interval='daily', check='comments') == True and
                             fetched_comments_daily >= peak_comments_daily):
                            forward_sleep_seconds = quota_supervisor_sleeper(protosleep=data['sleep'], interval='daily')
                            print('{} - INFO - Quota Supervisor: daily comments reached quotient.. (going to sleep {} hours long)\n~ time for IstaPy to take a big good nap :-)'.format(record_time, "%.1f" % (forward_sleep_seconds/60/60)))
                            quota_supervisor_notifier(protonotify=data['notify'], alert='sleep', job='Comments', interval='daily')
                            real_sleep (forward_sleep_seconds)
                            quota_supervisor_notifier(protonotify=data['notify'], alert='wake up', job='Comments', interval='daily')
                        else:
                            print('{} - INFO - QuotaSupervisor: jumped a comment out of daily quotient.. be fair with numbers, behave good! :]'.format(record_time))
                            return 'jump'
            if peak_comments_hourly is not None:
                cur.execute("SELECT comments, likes, created FROM statistics WHERE STRFTIME('%Y-%m-%d %H', created)==STRFTIME('%Y-%m-%d %H', 'now', 'localtime')")
                fetched_data = cur.fetchone()
                if fetched_data is None:
                    update_activity('timeloop')
                else:
                    fetched_comments_hourly, fetched_likes_hourly, fetched_raw_time = fetched_data[0], fetched_data[1], fetched_data[2]
                    if (fetched_comments_hourly >= peak_comments_hourly or
                        fetched_likes_hourly >= peak_likes_hourly):
                        if (quota_supervisor_sleeper(protosleep=data['sleep'], interval='hourly', check='comments') == True and
                             fetched_comments_hourly >= peak_comments_hourly):
                            forward_sleep_seconds = quota_supervisor_sleeper(protosleep=data['sleep'], interval='hourly', fetched_time=fetched_raw_time)
                            print('{} - INFO - Quota Supervisor: hourly comments reached quotient.. (going to sleep {} minutes long)\n~ take a tea break? :>'.format(record_time, "%.0f" % (forward_sleep_seconds/60)))
                            quota_supervisor_notifier(protonotify=data['notify'], alert='sleep', job='Comments', interval='hourly')
                            real_sleep (forward_sleep_seconds)
                            quota_supervisor_notifier(protonotify=data['notify'], alert='wake up', job='Comments', interval='hourly')
                        else:
                            print('{} - INFO - QuotaSupervisor: jumped a comment out of hourly quotient.. be fair with numbers, behave good! :]'.format(record_time))
                            return 'jump'

        elif inspect == 'follows':
            peak_follows_daily = data ['follows_d']
            peak_follows_hourly = data ['follows_h']
            if peak_follows_daily is not None:
                cur.execute("SELECT SUM(follows) FROM statistics WHERE STRFTIME('%Y-%m-%d', created)==STRFTIME('%Y-%m-%d', 'now', 'localtime')")
                fetched_data = cur.fetchone()
                if fetched_data is None:
                    update_activity('timeloop')
                else:
                    fetched_follows_daily = fetched_data[0]
                    if fetched_follows_daily >= peak_follows_daily:
                        if quota_supervisor_sleeper(protosleep=data['sleep'], interval='daily', check='follows') == True:
                            forward_sleep_seconds = quota_supervisor_sleeper(protosleep=data['sleep'], interval='daily')
                            print('{} - INFO - Quota Supervisor: daily follows reached quotient.. (going to sleep {} hours long)\n~ time for IstaPy to take a big good nap :-)'.format(record_time, "%.1f" % (forward_sleep_seconds/60/60)))
                            quota_supervisor_notifier(protonotify=data['notify'], alert='sleep', job='Follows', interval='daily')
                            real_sleep (forward_sleep_seconds)
                            quota_supervisor_notifier(protonotify=data['notify'], alert='wake up', job='Follows', interval='daily')
                        else:
                            print('{} - INFO - QuotaSupervisor: jumped a follow out of daily quotient.. be fair with numbers, behave good! :]'.format(record_time))
                            return 'jump'
            if peak_follows_hourly is not None:
                cur.execute("SELECT follows, created FROM statistics WHERE STRFTIME('%Y-%m-%d %H', created)==STRFTIME('%Y-%m-%d %H', 'now', 'localtime')")
                fetched_data = cur.fetchone()
                if fetched_data is None:
                    update_activity('timeloop')
                else:
                    fetched_follows_hourly, fetched_raw_time = fetched_data[0], fetched_data[1]
                    if fetched_follows_hourly >= peak_follows_hourly:
                        if quota_supervisor_sleeper(protosleep=data['sleep'], interval='hourly', check='follows') == True:
                            forward_sleep_seconds = quota_supervisor_sleeper(protosleep=data['sleep'], interval='hourly', fetched_time=fetched_raw_time)
                            print('{} - INFO - Quota Supervisor: hourly follows reached quotient.. (going to sleep {} minutes long)\n~ take a tea break? :>'.format(record_time, "%.0f" % (forward_sleep_seconds/60)))
                            quota_supervisor_notifier(protonotify=data['notify'], alert='sleep', job='Follows', interval='hourly')
                            real_sleep (forward_sleep_seconds)
                            quota_supervisor_notifier(protonotify=data['notify'], alert='wake up', job='Follows', interval='hourly')
                        else:
                            print('{} - INFO - QuotaSupervisor: jumped a follow out of hourly quotient.. be fair with numbers, behave good! :]'.format(record_time))
                            return 'jump'

        elif inspect == 'unfollows':
            peak_unfollows_daily = data ['unfollows_d']
            peak_unfollows_hourly = data ['unfollows_h']
            if peak_unfollows_daily is not None:
                cur.execute("SELECT SUM(unfollows) FROM statistics WHERE STRFTIME('%Y-%m-%d', created)==STRFTIME('%Y-%m-%d', 'now', 'localtime')")
                fetched_data = cur.fetchone()
                if fetched_data is None:
                    update_activity('timeloop')
                else:
                    fetched_unfollows_daily = fetched_data[0]
                    if fetched_unfollows_daily >= peak_unfollows_daily:
                        if quota_supervisor_sleeper(protosleep=data['sleep'], interval='daily', check='unfollows') == True:
                            forward_sleep_seconds = quota_supervisor_sleeper(protosleep=data['sleep'], interval='daily')
                            print('{} - INFO - Quota Supervisor: daily unfollows reached quotient.. (going to sleep {} hours long)\n~ time for IstaPy to take a big good nap :-)'.format(record_time, "%.1f" % (forward_sleep_seconds/60/60)))
                            quota_supervisor_notifier(protonotify=data['notify'], alert='sleep', job='Unfollows', interval='daily')
                            real_sleep (forward_sleep_seconds)
                            quota_supervisor_notifier(protonotify=data['notify'], alert='wake up', job='Unfollows', interval='daily')
                        else:
                            print('{} - INFO - QuotaSupervisor: jumped an unfollow out of daily quotient.. be fair with numbers, behave good! :]'.format(record_time))
                            return 'jump'
            if peak_unfollows_hourly is not None:
                cur.execute("SELECT unfollows, created FROM statistics WHERE STRFTIME('%Y-%m-%d %H', created)==STRFTIME('%Y-%m-%d %H', 'now', 'localtime')")
                fetched_data = cur.fetchone()
                if fetched_data is None:
                    update_activity('timeloop')
                else:
                    fetched_unfollows_hourly, fetched_raw_time = fetched_data[0], fetched_data[1]
                    if fetched_unfollows_hourly >= peak_unfollows_hourly:
                        if quota_supervisor_sleeper(protosleep=data['sleep'], interval='hourly', check='likes') == True:
                            forward_sleep_seconds = quota_supervisor_sleeper(protosleep=data['sleep'], interval='hourly', fetched_time=fetched_raw_time)
                            print('{} - INFO - Quota Supervisor: hourly unfollows reached quotient.. (going to sleep {} minutes long)\n~ take a tea break? :>'.format(record_time, "%.0f" % (forward_sleep_seconds/60)))
                            quota_supervisor_notifier(protonotify=data['notify'], alert='sleep', job='Unfollows', interval='hourly')
                            real_sleep (forward_sleep_seconds)
                            quota_supervisor_notifier(protonotify=data['notify'], alert='wake up', job='Unfollows', interval='hourly')
                        else:
                            print('{} - INFO - QuotaSupervisor: jumped an unfollow out of hourly quotient.. be fair with numbers, behave good! :]'.format(record_time))
                            return 'jump'


def quota_supervisor_stochastic (protostoch, record_time):
    """ Generate casually chosen arbitrary peak values based on protostoch, entered by the user """
    stochastic_realtime = epoch_time.time()
    stochastic_latesttime_h = protostoch ['stochastic_time_h']
    stochastic_latesttime_d = protostoch ['stochastic_time_d']
    #checking these guys both firsthand will reduce querying time below..
    if ((stochastic_realtime - stochastic_latesttime_h) >= 3750 or
        (stochastic_realtime - stochastic_latesttime_d) >= 27144
        ):
        conn = sqlite3.connect('./db/instapy.db')
        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM QuotaPeaks WHERE tact==1 ORDER BY recorded DESC LIMIT 1") #selecting original peaks from current session to generate stochastic peaks
            stoch_data = cur.fetchone()
        stoch_data = dict (stoch_data)
        #tact>1 is and gonna be current day's stochastical peaks' row since tact==1 is original peaks' row
        cur.execute("SELECT tact FROM QuotaPeaks WHERE STRFTIME('%Y-%m-%d', recorded) == STRFTIME('%Y-%m-%d', 'now', 'localtime') and tact>1")
        tact_data = cur.fetchone()
        tact_cycle = tact_data[0] + 1 if tact_data is not None else 2
        stoch_percent = 85  #over 70, below 85 would be good
        #renew peak values at relative range just after an hour
        if (stochastic_realtime - stochastic_latesttime_h) >= 3750:
            peak_likes_hourly = None if stoch_data['likes_h'] is None else (random.randint (int((stoch_data['likes_h']+1)*stoch_percent/100),stoch_data['likes_h']))
            peak_comments_hourly = None if stoch_data['comments_h'] is None else (random.randint (int((stoch_data['comments_h']+1)*stoch_percent/100),stoch_data['comments_h']))
            peak_follows_hourly = None if stoch_data['follows_h'] is None else (random.randint (int((stoch_data['follows_h']+1)*stoch_percent/100),stoch_data['follows_h']))
            peak_unfollows_hourly = None if stoch_data['unfollows_h'] is None else (random.randint (int((stoch_data['unfollows_h']+1)*stoch_percent/100),stoch_data['unfollows_h']))
            peak_server_calls_hourly = None if stoch_data['server_calls_h'] is None else (random.randint (int((stoch_data['server_calls_h']+1)*stoch_percent/100),stoch_data['server_calls_h']))
            stochastic_latesttime_h = epoch_time.time()
            if tact_data is None:
                cur.execute("INSERT INTO QuotaPeaks (state, sleep, stochastic, notify, likes_h, likes_d, comments_h, comments_d, follows_h, follows_d, unfollows_h, unfollows_d, server_calls_h, server_calls_d, stochastic_time_h, stochastic_time_d, tact, recorded) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                                        (protostoch['state'], protostoch['sleep'], protostoch['stochastic'], protostoch['notify'], peak_likes_hourly, protostoch['likes_d'], peak_comments_hourly, protostoch['comments_d'],
                                                        peak_follows_hourly, protostoch['follows_d'], peak_unfollows_hourly, protostoch['unfollows_d'],
                                                        peak_server_calls_hourly, protostoch['server_calls_d'], stochastic_latesttime_h, protostoch['stochastic_time_d'], tact_cycle, record_time))
            else:
                cur.execute("UPDATE QuotaPeaks set state=?, sleep=?, likes_h=?, comments_h=?, follows_h=?, unfollows_h=?, server_calls_h=?, stochastic_time_h=?, tact=?, recorded=? WHERE recorded == (SELECT MAX(recorded) FROM QuotaPeaks WHERE tact>1)",
                                                        (protostoch['state'], protostoch['sleep'], peak_likes_hourly, peak_comments_hourly, peak_follows_hourly, peak_unfollows_hourly, peak_server_calls_hourly,
                                                         stochastic_latesttime_h, tact_cycle, record_time))
            conn.commit()    # with next call, quota_supervisor will load new hourly stochastic peak values at tact>1
            print('{} - INFO - Quota Supervisor: hourly peak rates are updated in stochastic probablity'.format(record_time))
        #about ~one day (most people will not reach 86400 seconds hence errors, smaller is better)
        if (stochastic_realtime - stochastic_latesttime_d) >= 27144:
            peak_likes_daily = None if stoch_data['likes_d'] is None else (random.randint (int((stoch_data['likes_d']+1)*stoch_percent/100),stoch_data['likes_d']))
            peak_comments_daily = None if stoch_data['comments_d'] is None else (random.randint (int((stoch_data['comments_d']+1)*stoch_percent/100),stoch_data['comments_d']))
            peak_follows_daily = None if stoch_data['follows_d'] is None else (random.randint (int((stoch_data['follows_d']+1)*stoch_percent/100),stoch_data['follows_d']))
            peak_unfollows_daily = None if stoch_data['unfollows_d'] is None else (random.randint (int((stoch_data['unfollows_d']+1)*stoch_percent/100),stoch_data['unfollows_d']))
            peak_server_calls_daily = None if stoch_data['server_calls_d'] is None else (random.randint (int((stoch_data['server_calls_d']+1)*stoch_percent/100),stoch_data['server_calls_d']))
            stochastic_latesttime_d = epoch_time.time()
            if tact_data is None:
                cur.execute("INSERT INTO QuotaPeaks (state, sleep, stochastic, notify, likes_h, likes_d, comments_h, comments_d, follows_h, follows_d, unfollows_h, unfollows_d, server_calls_h, server_calls_d, stochastic_time_h, stochastic_time_d, tact, recorded) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                                        (protostoch['state'], protostoch['sleep'], protostoch['stochastic'], protostoch['notify'], protostoch['likes_h'], peak_likes_daily, protostoch['comments_h'], peak_comments_daily,
                                                        protostoch['follows_h'], peak_follows_daily, protostoch['unfollows_h'], peak_unfollows_daily,
                                                        protostoch['server_calls_h'], peak_server_calls_daily, protostoch['stochastic_time_h'], stochastic_latesttime_d, tact_cycle, record_time))
            else:
                cur.execute("UPDATE QuotaPeaks set state=?, sleep=?, likes_d=?, comments_d=?, follows_d=?, unfollows_d=?, server_calls_d=?, stochastic_time_d=?, tact=?, recorded=? WHERE recorded == (SELECT MAX(recorded) FROM QuotaPeaks WHERE tact>1)",
                                                        (protostoch['state'], protostoch['sleep'], peak_likes_daily, peak_comments_daily, peak_follows_daily, peak_unfollows_daily, peak_server_calls_daily,
                                                         stochastic_latesttime_d, tact_cycle, record_time))
            conn.commit()    # with next call, quota_supervisor will load new daily stochastic peak values at tact>1
            print('{} - INFO - Quota Supervisor: daily peak rates are updated in stochastic probablity'.format(record_time))


def quota_supervisor_sleeper (protosleep, interval, fetched_time=None, check=None):
    """ Calculate wake up time and return accurate or randomly fixed (extra bear time) sleep seconds """
    #processing time outside major Quota Supervisor definition will save up time whereas, will only be requested once the supervisor decides to sleep
    sleepzz = protosleep.split('-')
    bear_sleep = sleepzz[5]
    bear_extra_sleep_percent = 140  #actually 114 is not that bad amount
    #will be called every time after reaching quotient, speed is real issue below
    if check is not None:
        if check=='likes':
            if interval == 'hourly':
                return True if sleepzz[0].startswith('1') else False
            elif interval == 'daily':
                return True if sleepzz[0].endswith('1') else False
        elif check=='comments':
            if interval == 'hourly':
                return True if sleepzz[1].startswith('1') else False
            elif interval == 'daily':
                return True if sleepzz[1].endswith('1') else False
        elif check=='follows':
            if interval == 'hourly':
                return True if sleepzz[2].startswith('1') else False
            elif interval == 'daily':
                return True if sleepzz[2].endswith('1') else False
        elif check=='unfollows':
            if interval == 'hourly':
                return True if sleepzz[3].startswith('1') else False
            elif interval == 'daily':
                return True if sleepzz[3].endswith('1') else False
        elif check=='server_calls':
            if interval == 'hourly':
                return True if sleepzz[4].startswith('1') else False
            elif interval == 'daily':
                return True if sleepzz[4].endswith('1') else False

    #will only be asked to only once going to sleep that speed is no problem
    else:
        if interval == 'hourly':
                fetched_converted_time = datetime.strptime(fetched_time, '%Y-%m-%d %H:%M:%S')
                remaining_seconds_h = (61 - int(fetched_converted_time.strftime('%M')))*60
                return remaining_seconds_h if bear_sleep.startswith('0') else random.randint(remaining_seconds_h, int(remaining_seconds_h*bear_extra_sleep_percent/100))

        elif interval == 'daily':
                tomorrow = date.today() + timedelta(1)
                midnight = datetime.combine(tomorrow, time())
                now = datetime.now()
                remaining_seconds_d = (midnight - now).seconds
                return remaining_seconds_d if bear_sleep.startswith('0') else random.randint(remaining_seconds_d, int(remaining_seconds_d*bear_extra_sleep_percent/100))


def quota_supervisor_notifier(protonotify, alert, job, interval):
    """ Send Toast notifications about supervising states to directly the operating system with plyer modules """
    if protonotify == 1:
        if sys.platform.startswith('win32' or
                                    'linux' or
                                     'darwin'):
            sleep_icon = './icons/qs_sleep_windows.ico' if sys.platform.startswith('win32') else './icons/qs_sleep_linux.png' if sys.platform.startswith('linux') else './icons/qs_sleep_mac.icns' if sys.platform.startswith('darwin') else None
            wakeup_icon = './icons/qs_wakeup_windows.ico' if sys.platform.startswith('win32') else './icons/qs_wakeup_linux.png' if sys.platform.startswith('linux') else './icons/qs_wakeup_mac.icns' if sys.platform.startswith('darwin') else None
            exit_icon = './icons/qs_exit_windows.ico' if sys.platform.startswith('win32') else './icons/qs_exit_linux.png' if sys.platform.startswith('linux') else './icons/qs_exit_mac.icns' if sys.platform.startswith('darwin') else None

            if alert == 'sleep':
                try:
                    notification.notify(
                        title = 'Quota Supervisor',
                        message = 'Yawn! {} filled {} quotient!\n ..falling asleep a bit :>'.format(job, interval),
                        app_name ='InstaPy',
                        app_icon = sleep_icon,
                        timeout = 7,
                        ticker = 'To switch supervising methods, please review quickstart.py'
                        )
                except: #i couldn't guess exact exceptions to catch, it would be great to find it out (*errors will be related to `plyer` package's OS support, ValueError in strings and non-working customized icons error)
                    print ('{} - INFO - Quota Supervisor: toast notifications currently isn\'t supported in your platform.. :L'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), sys.exc_info()[0])
                    raise
                    pass
            elif alert == 'wake up':
                try:
                    notification.notify(
                        title = 'Quota Supervisor',
                        message = 'Yikes! {} just woke up from {} quotient bandage!\n ..let\'s chill again wakey ;)'.format(job, interval),
                        app_name = 'InstaPy',
                        app_icon = wakeup_icon,
                        timeout = 7,
                        ticker = 'To switch supervising methods, please review quickstart.py'
                        )
                except:
                    print ('{} - INFO - Quota Supervisor: toast notifications currently isn\'t supported in your platform.. :L'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), sys.exc_info()[0])
                    raise
                    pass
            elif alert == 'exit':
                try:
                    notification.notify(
                        title = 'Quota Supervisor',
                        message ='D\'oh! {} finished {} quotient!\n ..exiting ~,~'.format(job, interval),
                        app_name = 'InstaPy',
                        app_icon = exit_icon,
                        timeout = 9,
                        ticker = 'To switch supervising methods, please review quickstart.py'
                        )
                except:
                    print ('{} - INFO - Quota Supervisor: toast notifications currently isn\'t supported in your platform.. :L'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), sys.exc_info()[0])
                    raise
                    pass
