"""
Class to define the Logger
"""

# import helpers
from ..util import interruption_handler

# import libraries
from datetime import datetime
import logging
import logging.handlers
from math import ceil

# import drivers.actions
from instapy.drivers import WebDriver


class Logger(object):
    """
    should contain all the function used throughout the code related to logging
    """

    __logger = None

    def __init__(
        self,
        username: str = "",
        logfolder: str = "",
        show_logs: bool = False,
        log_handler=None,
    ):
        self.username = username
        self.logfolder = logfolder
        self.show_logs = show_logs

        _logger = logging.getLogger(self.username)
        _logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler("{}general.log".format(self.logfolder))
        file_handler.setLevel(logging.DEBUG)
        extra = {"username": self.username}
        logger_formatter = logging.Formatter(
            "%(levelname)s [%(asctime)s] [%(username)s]  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(logger_formatter)
        _logger.addHandler(file_handler)

        # add custom user handler if given
        if log_handler:
            _logger.addHandler(log_handler)

        if self.show_logs is True:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(logger_formatter)
            _logger.addHandler(console_handler)

        self.__logger = logging.LoggerAdapter(_logger, extra)

    @property
    def logger(self):
        return self.__logger

    @classmethod
    def getLogger(cls):
        return cls.__logger

    @classmethod
    def info(cls, message: str = ""):
        cls.__logger.info(message)

    @classmethod
    def error(cls, message: str = ""):
        cls.__logger.error(message)

    @classmethod
    def warning(cls, message: str = ""):
        cls.__logger.warning(message)

    @classmethod
    def highlight_print(cls, message=None, priority=None, level=None):
        """ Print headers in a highlighted style """
        # can add other highlighters at other priorities enriching this function

        # find the number of chars needed off the length of the logger message
        output_len = (
            28 + len(cls.username) + 3 + len(message) if cls.__logger else len(message)
        )

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

        if upper_char and (cls.show_logs or priority == "workspace"):
            print("{}".format(upper_char * int(ceil(output_len / len(upper_char)))))

        if level == "info":
            if cls.logger:
                cls.logger.info(message)
            else:
                print(message)

        elif level == "warning":
            if cls.logger:
                cls.logger.warning(message)
            else:
                print(message)

        elif level == "critical":
            if cls.logger:
                cls.logger.critical(message)
            else:
                print(message)

        if lower_char and (cls.show_logs or priority == "workspace"):
            print("{}".format(lower_char * int(ceil(output_len / len(lower_char)))))

    @staticmethod
    def get_log_time():
        """ this method will keep same format for all recored"""
        log_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        return log_time

    @classmethod
    def log_follower_num(cls):
        """Prints and logs the current number of followers to
        a seperate file"""

        try:
            user = WebDriver.go_user(cls.username)
            followed_by = user.get_follower_count()

        except:  # handle the possible `entry_data` error
            followed_by = None

        with open("{}followerNum.txt".format(cls.logfolder), "a") as numFile:
            numFile.write(
                "{:%Y-%m-%d %H:%M} {}\n".format(datetime.now(), followed_by or 0)
            )

        return followed_by

    @classmethod
    def log_following_num(cls):
        """Prints and logs the current number of followers to
        a seperate file"""

        try:
            user = WebDriver.go_user(cls.username)
            following_num = user.get_following_count()

        except:
            following_num = None

        with open("{}followingNum.txt".format(cls.logfolder), "a") as numFile:
            numFile.write(
                "{:%Y-%m-%d %H:%M} {}\n".format(datetime.now(), following_num or 0)
            )

        return following_num

    @classmethod
    def log_followed_pool(cls, followed, logtime, user_id):
        """Prints and logs the followed to
        a separate file"""
        try:
            with open(
                "{0}{1}_followedPool.csv".format(cls.logfolder, cls.username), "a+"
            ) as followPool:
                with interruption_handler():
                    followPool.write(
                        "{} ~ {} ~ {},\n".format(logtime, followed, user_id)
                    )

        except BaseException as e:
            cls.logger.error("log_followed_pool error {}".format(str(e)))

        # We save all followed to a pool that will never be erase
        cls.log_record_all_followed(followed, logtime, user_id)

    @classmethod
    def log_uncertain_unfollowed_pool(cls, person, logtime, user_id):
        """Prints and logs the uncertain unfollowed to
        a seperate file"""
        try:
            with open(
                "{0}{1}_uncertain_unfollowedPool.csv".format(
                    cls.logfolder, cls.username
                ),
                "a+",
            ) as followPool:
                with interruption_handler():
                    followPool.write("{} ~ {} ~ {},\n".format(logtime, person, user_id))
        except BaseException as e:
            cls.logger.error("log_uncertain_unfollowed_pool error {}".format(str(e)))

    @classmethod
    def log_record_all_unfollowed(cls, unfollowed):
        """logs all unfollowed ever to
        a seperate file"""
        try:
            with open(
                "{0}{1}_record_all_unfollowed.csv".format(cls.logfolder, cls.username),
                "a+",
            ) as followPool:
                with interruption_handler():
                    followPool.write("{},\n".format(unfollowed))
        except BaseException as e:
            cls.logger.error("log_record_all_unfollowed_pool error {}".format(str(e)))

    @classmethod
    def log_record_all_followed(cls, followed, logtime, user_id):
        """logs all followed ever to a pool that will never be erase"""
        try:
            with open(
                "{0}{1}_record_all_followed.csv".format(cls.logfolder, cls.username),
                "a+",
            ) as followPool:
                with interruption_handler():
                    followPool.write(
                        "{} ~ {} ~ {},\n".format(logtime, followed, user_id)
                    )
        except BaseException as e:
            cls.logger.error("log_record_all_followed_pool error {}".format(str(e)))
