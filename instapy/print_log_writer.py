"""Module only used to log the number of followers to a file"""
from datetime import datetime

from .util import interruption_handler, getUserData
from .util import web_address_navigator


def get_log_time():
    """this method will keep same format for all recorded"""
    log_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    return log_time


def log_follower_num(browser, username, logfolder):
    """Prints and logs the current number of followers to
    a separate file"""
    user_link = "https://www.instagram.com/{}".format(username)
    web_address_navigator(browser, user_link)

    followed_by = getUserData("graphql.user.edge_followed_by.count", browser)

    with open("{}followerNum.txt".format(logfolder), "a") as numFile:
        numFile.write("{:%Y-%m-%d %H:%M} {}\n".format(datetime.now(), followed_by or 0))

    return followed_by


def log_following_num(browser, username, logfolder):
    """Prints and logs the current number of followers to
    a separate file"""
    user_link = "https://www.instagram.com/{}".format(username)
    web_address_navigator(browser, user_link)

    following_num = getUserData("graphql.user.edge_follow.count", browser)

    with open("{}followingNum.txt".format(logfolder), "a") as numFile:
        numFile.write(
            "{:%Y-%m-%d %H:%M} {}\n".format(datetime.now(), following_num or 0)
        )

    return following_num


def log_followed_pool(login, followed, logger, logfolder, logtime, user_id):
    """Prints and logs the followed to
    a separate file"""
    try:
        with open(
            "{0}{1}_followedPool.csv".format(logfolder, login), "a+"
        ) as followPool:
            with interruption_handler():
                followPool.write("{} ~ {} ~ {},\n".format(logtime, followed, user_id))

    except BaseException as e:
        logger.error("log_followed_pool error {}".format(str(e)))

    # We save all followed to a pool that will never be erase
    log_record_all_followed(login, followed, logger, logfolder, logtime, user_id)


def log_uncertain_unfollowed_pool(login, person, logger, logfolder, logtime, user_id):
    """Prints and logs the uncertain unfollowed to
    a separate file"""
    try:
        with open(
            "{0}{1}_uncertain_unfollowedPool.csv".format(logfolder, login), "a+"
        ) as followPool:
            with interruption_handler():
                followPool.write("{} ~ {} ~ {},\n".format(logtime, person, user_id))
    except BaseException as e:
        logger.error("log_uncertain_unfollowed_pool error {}".format(str(e)))


def log_record_all_unfollowed(login, unfollowed, logger, logfolder):
    """logs all unfollowed ever to
    a separate file"""
    try:
        with open(
            "{0}{1}_record_all_unfollowed.csv".format(logfolder, login), "a+"
        ) as followPool:
            with interruption_handler():
                followPool.write("{},\n".format(unfollowed))
    except BaseException as e:
        logger.error("log_record_all_unfollowed_pool error {}".format(str(e)))


def log_record_all_followed(login, followed, logger, logfolder, logtime, user_id):
    """logs all followed ever to a pool that will never be erase"""
    try:
        with open(
            "{0}{1}_record_all_followed.csv".format(logfolder, login), "a+"
        ) as followPool:
            with interruption_handler():
                followPool.write("{} ~ {} ~ {},\n".format(logtime, followed, user_id))
    except BaseException as e:
        logger.error("log_record_all_followed_pool error {}".format(str(e)))
