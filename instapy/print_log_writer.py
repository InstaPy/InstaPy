"""Module only used to log the number of followers to a file"""
from datetime import datetime


def log_follower_num(browser, username):
    """Prints and logs the current number of followers to
    a seperate file"""
    browser.get('https://www.instagram.com/' + username)

    followed_by = browser.execute_script(
        "return window._sharedData.""entry_data.ProfilePage[0]."
        "user.followed_by.count")

    with open('./logs/followerNum.txt', 'a') as numFile:
        numFile.write(
            '{:%Y-%m-%d %H:%M} {}\n'.format(datetime.now(), followed_by or 0))

    return followed_by

def log_following_num(browser, username):
    """Prints and logs the current number of followers to
    a seperate file"""
    browser.get('https://www.instagram.com/' + username)

    following_num = browser.execute_script(
        "return window._sharedData.""entry_data.ProfilePage[0]."
        "user.follows.count")

    with open('./logs/followingNum.txt', 'a') as numFile:
        numFile.write(
            '{:%Y-%m-%d %H:%M} {}\n'.format(datetime.now(), following_num or 0))

    return following_num

def log_followed_pool(login, followed, logger):
    """Prints and logs the followed to
    a seperate file"""
    try:
        with open('./logs/' + login + '_followedPool.csv', 'a+') as followPool:
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