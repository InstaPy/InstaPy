"""Module only used to log the number of followers to a file"""
from datetime import datetime

from .util import getUserData, interruption_handler, web_address_navigator


def get_log_time():
    """this method will keep same format for all recorded"""
    log_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    return log_time


def log_follower_num(browser, username, logfolder):
    """Prints and logs the current number of followers to
    a separate file"""
    user_link = f"https://www.instagram.com/{username}"
    web_address_navigator(browser, user_link)

    followed_by = getUserData("graphql.user.edge_followed_by.count", browser)

    with open(f"{logfolder}followerNum.txt", "a") as numFile:
        numFile.write(f"{datetime.now():%Y-%m-%d %H:%M} {followed_by or 0}\n")

    return followed_by


def log_following_num(browser, username, logfolder):
    """Prints and logs the current number of followers to
    a separate file"""
    user_link = f"https://www.instagram.com/{username}"
    web_address_navigator(browser, user_link)

    following_num = getUserData("graphql.user.edge_follow.count", browser)

    with open(f"{logfolder}followingNum.txt", "a") as numFile:
        numFile.write(f"{datetime.now():%Y-%m-%d %H:%M} {following_num or 0}\n")

    return following_num


def log_followed_pool(login, followed, logger, logfolder, logtime, user_id):
    """Prints and logs the followed to
    a separate file"""
    try:
        with open(f"{logfolder}{login}_followedPool.csv", "a+") as followPool:
            with interruption_handler():
                followPool.write(f"{logtime} ~ {followed} ~ {user_id},\n")

    except BaseException as e:
        logger.error(f"log_followed_pool error {str(e)}")

    # We save all followed to a pool that will never be erase
    log_record_all_followed(login, followed, logger, logfolder, logtime, user_id)


def log_uncertain_unfollowed_pool(login, person, logger, logfolder, logtime, user_id):
    """Prints and logs the uncertain unfollowed to
    a separate file"""
    try:
        with open(
            f"{logfolder}{login}_uncertain_unfollowedPool.csv", "a+"
        ) as followPool:
            with interruption_handler():
                followPool.write(f"{logtime} ~ {person} ~ {user_id},\n")
    except BaseException as e:
        logger.error(f"log_uncertain_unfollowed_pool error {str(e)}")


def log_record_all_unfollowed(login, unfollowed, logger, logfolder):
    """logs all unfollowed ever to
    a separate file"""
    try:
        with open(f"{logfolder}{login}_record_all_unfollowed.csv", "a+") as followPool:
            with interruption_handler():
                followPool.write(f"{unfollowed},\n")
    except BaseException as e:
        logger.error(f"log_record_all_unfollowed_pool error {str(e)}")


def log_record_all_followed(login, followed, logger, logfolder, logtime, user_id):
    """logs all followed ever to a pool that will never be erase"""
    try:
        with open(f"{logfolder}{login}_record_all_followed.csv", "a+") as followPool:
            with interruption_handler():
                followPool.write(f"{logtime} ~ {followed} ~ {user_id},\n")
    except BaseException as e:
        logger.error(f"log_record_all_followed_pool error {str(e)}")
