"""
Class to define the Logger
"""

from datetime import datetime

from .time_util import sleep
from .util import interruption_handler
from .util import web_address_navigator
from .util import update_activity

import logging
import logging.handlers

import drivers.actions

class Logger(object):
    """
    should contain all the function used throughout the code related to logging
    """

    def __init__(self, username: str='', logfolder: str='', show_logs: bool=False, log_handler=None):
        self.username = username
        self.logfolder = logfolder
        self.show_logs = show_logs

        self.__logger = logging.getLogger(self.username)
        self.__logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler("{}general.log".format(self.logfolder))
        file_handler.setLevel(logging.DEBUG)
        extra = {"username": self.username}
        logger_formatter = logging.Formatter(
            "%(levelname)s [%(asctime)s] [%(username)s]  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(logger_formatter)
        self.__logger.addHandler(file_handler)

        # add custom user handler if given
        if log_handler:
            self.__logger.addHandler(log_handler)

        if self.show_logs is True:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(logger_formatter)
            self.__logger.addHandler(console_handler)

        self.__logger = logging.LoggerAdapter(self.__logger, extra)


    def highlight_print(self,
             message=None, priority=None, level=None
    ):
        """ Print headers in a highlighted style """
        # can add other highlighters at other priorities enriching this function

        # find the number of chars needed off the length of the logger message
        output_len = 28 + len(self.username) + 3 + len(message) if self.__logger else len(message)

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
            lower_char = '"'

        elif priority == "user iteration":
            # ::::::::::::::::::::::::::::::::::::::::::::::::
            # E.g.:            User: [1/4]
            upper_char = ":"
            lower_char = None

        elif priority == "post iteration":
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # E.g.:            Post: [2/10]
            upper_char = "~"
            lower_char = None

        elif priority == "workspace":
            # ._. ._. ._. ._. ._. ._. ._. ._. ._. ._. ._. ._.
            # E.g.: |> Workspace in use: "C:/Users/El/InstaPy"
            upper_char = " ._. "
            lower_char = None

        if upper_char and (self.show_logs or priority == "workspace"):
            print("{}".format(upper_char * int(ceil(output_len / len(upper_char)))))

        if level == "info":
            if self.__logger:
                self.__logger.info(message)
            else:
                print(message)

        elif level == "warning":
            if self.__logger:
                self.__logger.warning(message)
            else:
                print(message)

        elif level == "critical":
            if self.__logger:
                self.__logger.critical(message)
            else:
                print(message)

        if lower_char and (self.show_logs or priority == "workspace"):
            print("{}".format(lower_char * int(ceil(output_len / len(lower_char)))))


    @staticmethod
    def get_log_time():
        """ this method will keep same format for all recored"""
        log_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        return log_time


    def log_follower_num(self, driver):
        """Prints and logs the current number of followers to
        a seperate file"""



        try:
            user = driver.go_user(self.username)
            user.populate()
            followed_by = user.get_follower_count()

        except WebDriverException:  # handle the possible `entry_data` error
            followed_by = None

        with open("{}followerNum.txt".format(logfolder), "a") as numFile:
            numFile.write("{:%Y-%m-%d %H:%M} {}\n".format(datetime.now(), followed_by or 0))

        return followed_by

    @staticmethod
    def log_following_num(browser, username, logfolder):
        """Prints and logs the current number of followers to
        a seperate file"""
        user_link = "https://www.instagram.com/{}".format(username)
        web_address_navigator(browser, user_link)

        try:
            following_num = browser.execute_script(
                "return window._sharedData."
                "entry_data.ProfilePage[0]."
                "graphql.user.edge_follow.count"
            )

        except WebDriverException:
            try:
                browser.execute_script("location.reload()")
                update_activity(browser, state=None)

                sleep(10)
                following_num = browser.execute_script(
                    "return window._sharedData."
                    "entry_data.ProfilePage[0]."
                    "graphql.user.edge_follow.count"
                )

            except WebDriverException:
                following_num = None

        with open("{}followingNum.txt".format(logfolder), "a") as numFile:
            numFile.write(
                "{:%Y-%m-%d %H:%M} {}\n".format(datetime.now(), following_num or 0)
            )

        return following_num

    @staticmethod
    def log_followed_pool(login, followed, logger, logfolder, logtime, user_id):
        """Prints and logs the followed to
        a seperate file"""
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

    @staticmethod
    def log_uncertain_unfollowed_pool(login, person, logger, logfolder, logtime, user_id):
        """Prints and logs the uncertain unfollowed to
        a seperate file"""
        try:
            with open(
                    "{0}{1}_uncertain_unfollowedPool.csv".format(logfolder, login), "a+"
            ) as followPool:
                with interruption_handler():
                    followPool.write("{} ~ {} ~ {},\n".format(logtime, person, user_id))
        except BaseException as e:
            logger.error("log_uncertain_unfollowed_pool error {}".format(str(e)))

    @staticmethod
    def log_record_all_unfollowed(login, unfollowed, logger, logfolder):
        """logs all unfollowed ever to
        a seperate file"""
        try:
            with open(
                    "{0}{1}_record_all_unfollowed.csv".format(logfolder, login), "a+"
            ) as followPool:
                with interruption_handler():
                    followPool.write("{},\n".format(unfollowed))
        except BaseException as e:
            logger.error("log_record_all_unfollowed_pool error {}".format(str(e)))

    @staticmethod
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
