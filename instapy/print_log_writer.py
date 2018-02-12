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


def log_followed_pool(login, followed, logger, logfolder):
    """Prints and logs the followed to
    a seperate file"""
    try:
        with open('{0}{1}_followedPool.csv'.format(logfolder, login), 'a+') as followPool:
            followPool.write(followed + ",\n")
    except BaseException as e:
        logger.error("log_followed_pool error {}".format(str(e)))

    # We save all followed to a pool that will never be erase
    log_record_all_followed(login, followed, logger, logfolder)


def log_uncertain_unfollowed_pool(login, unfollowed, logger, logfolder):
    """Prints and logs the uncertain unfollowed to
    a seperate file"""
    try:
        with open('{0}{1}_uncertain_unfollowedPool.csv'.format(logfolder, login), 'a+') as followPool:
            followPool.write(unfollowed + ",\n")
    except BaseException as e:
        logger.error("log_uncertain_unfollowed_pool error {}".format(str(e)))


def log_record_all_unfollowed(login, unfollowed, logger, logfolder):
    """logs all unfollowed ever to
    a seperate file"""
    try:
        with open('{0}{1}_record_all_unfollowed.csv'.format(logfolder, login), 'a+') as followPool:
            followPool.write(unfollowed + ",\n")
    except BaseException as e:
        logger.error("log_record_all_unfollowed_pool error {}".format(str(e)))


def log_record_all_followed(login, followed, logger, logfolder):
    """logs all followed ever to a pool that will never be erase"""
    try:
        with open('{0}{1}_record_all_followed.csv'.format(logfolder, login), 'a+') as followPool:
            followPool.write(followed + ",\n")
    except BaseException as e:
        logger.error("log__record_all_followed_pool error {}".format(str(e)))