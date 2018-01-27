"""Module only used to log the number of followers to a file"""
from datetime import datetime


def log_follower_num(browser, username, logfolder):
    """Prints and logs the current number of followers to
    a seperate file"""
    browser.get('https://www.instagram.com/' + username)

    followed_by = browser.execute_script(
        "return window._sharedData.""entry_data.ProfilePage[0]."
        "user.followed_by.count")

    with open('{}followerNum.txt'.format(logfolder), 'a') as numFile:
        numFile.write(
            '{:%Y-%m-%d %H:%M} {}\n'.format(datetime.now(), followed_by or 0))

    return followed_by

def log_following_num(browser, username, logfolder):
    """Prints and logs the current number of followers to
    a seperate file"""
    browser.get('https://www.instagram.com/' + username)

    following_num = browser.execute_script(
        "return window._sharedData.""entry_data.ProfilePage[0]."
        "user.follows.count")

    with open('{}followingNum.txt'.format(logfolder), 'a') as numFile:
        numFile.write(
            '{:%Y-%m-%d %H:%M} {}\n'.format(datetime.now(), following_num or 0))

    return following_num

def log_followed_pool(login, followed, logger, logfolder):
    """Prints and logs the followed to
    a seperate file"""
    try:
        with open('{0}{1}_followedPool.csv'.format(logfolder, login), 'a+') as followPool:
            followPool.write(followed + ",\n")
    except BaseException as e:
        logger.error("log_followed_pool error {}".format(str(e)))

def log_uncertain_unfollowed_pool(login, unfollowed, logger):
    """Prints and logs the uncertain unfollowed to
    a seperate file"""
    try:
        with open('./logs/' + login + '_uncertain_unfollowedPool.csv', 'a+') as followPool:
            followPool.write(unfollowed + ",\n")
    except BaseException as e:
        logger.error("log_followed_pool error {}".format(str(e)))