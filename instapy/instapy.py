"""OS Modules environ method to get the setup vars from the Environment"""
# import built-in & third-party modules
import time
from datetime import datetime, timedelta
from math import ceil
import random
from sys import platform
from platform import python_version
import os
import csv
import json
import requests
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
import logging
import logging.handlers
from contextlib import contextmanager
from copy import deepcopy
import unicodedata

try:
    from pyvirtualdisplay import Display
except ModuleNotFoundError:
    pass

# import InstaPy modules
from . import __version__
from .clarifai_util import check_image
from .comment_util import comment_image
from .comment_util import verify_commenting
from .comment_util import get_comments_on_post
from .like_util import check_link
from .like_util import verify_liking
from .like_util import get_links_for_tag
from .like_util import get_links_from_feed
from .like_util import get_tags
from .like_util import get_links_for_location
from .like_util import like_image
from .like_util import get_links_for_username
from .like_util import like_comment
from .story_util import watch_story
from .login_util import login_user
from .settings import Settings
from .settings import localize_path
from .print_log_writer import log_follower_num
from .print_log_writer import log_following_num

from .time_util import sleep
from .time_util import set_sleep_percentage
from .util import get_active_users
from .util import validate_username
from .util import web_address_navigator
from .util import interruption_handler
from .util import highlight_print
from .util import dump_record_activity
from .util import truncate_float
from .util import save_account_progress
from .util import parse_cli_args
from .util import get_cord_location
from .util import get_bounding_box
from .unfollow_util import get_given_user_followers
from .unfollow_util import get_given_user_following
from .unfollow_util import unfollow
from .unfollow_util import unfollow_user
from .unfollow_util import follow_user
from .unfollow_util import follow_restriction
from .unfollow_util import dump_follow_restriction
from .unfollow_util import set_automated_followed_pool
from .unfollow_util import get_follow_requests
from .commenters_util import extract_information
from .commenters_util import users_liked
from .commenters_util import get_photo_urls_from_profile
from .relationship_tools import get_following
from .relationship_tools import get_followers
from .relationship_tools import get_unfollowers
from .relationship_tools import get_nonfollowers
from .relationship_tools import get_fans
from .relationship_tools import get_mutual_following
from .database_engine import get_database
from .text_analytics import text_analysis
from .text_analytics import yandex_supported_languages
from .browser import set_selenium_local_session
from .browser import close_browser
from .file_manager import get_workspace
from .file_manager import get_logfolder

from .pods_util import group_posts
from .pods_util import get_recent_posts_from_pods
from .pods_util import share_my_post_with_pods
from .pods_util import share_with_pods_restriction
from .pods_util import comment_restriction

from .xpath import read_xpath

# import exceptions
from selenium.common.exceptions import NoSuchElementException
from .exceptions import InstaPyError


class InstaPy:
    """Class to be instantiated to use the script"""

    def __init__(
        self,
        username: str = None,
        password: str = None,
        nogui: bool = False,
        selenium_local_session: bool = True,
        browser_profile_path: str = None,
        page_delay: int = 25,
        show_logs: bool = True,
        headless_browser: bool = False,
        proxy_username: str = None,
        proxy_password: str = None,
        proxy_address: str = None,
        proxy_port: str = None,
        disable_image_load: bool = False,
        multi_logs: bool = True,
        log_handler=None,  # TODO function type ?
        geckodriver_path: str = None,
        split_db: bool = False,
        bypass_security_challenge_using: str = "email",
    ):
        print("InstaPy Version: {}".format(__version__))
        cli_args = parse_cli_args()
        username = cli_args.username or username
        password = cli_args.password or password
        page_delay = cli_args.page_delay or page_delay
        headless_browser = cli_args.headless_browser or headless_browser
        proxy_address = cli_args.proxy_address or proxy_address
        proxy_port = cli_args.proxy_port or proxy_port
        disable_image_load = cli_args.disable_image_load or disable_image_load
        split_db = cli_args.split_db or split_db

        Settings.InstaPy_is_running = True
        # workspace must be ready before anything
        if not get_workspace():
            raise InstaPyError("Oh no! I don't have a workspace to work at :'(")

        # virtual display to hide browser (not supported on Windows)
        self.nogui = nogui
        if self.nogui:
            if not platform.startswith("win32"):
                self.display = Display(visible=0, size=(800, 600))
                self.display.start()
            else:
                raise InstaPyError("The 'nogui' parameter isn't supported on Windows.")

        self.browser = None
        self.page_delay = page_delay
        self.disable_image_load = disable_image_load
        self.bypass_security_challenge_using = bypass_security_challenge_using

        # choose environment over static typed credentials
        self.username = os.environ.get("INSTA_USER") or username
        self.password = os.environ.get("INSTA_PW") or password

        Settings.profile["name"] = self.username

        self.split_db = split_db
        if self.split_db:
            Settings.database_location = localize_path(
                "db", "instapy_{}.db".format(self.username)
            )

        self.do_comment = False
        self.comment_percentage = 0
        self.comments = ["Cool!", "Nice!", "Looks good!"]
        self.photo_comments = []
        self.video_comments = []

        self.do_reply_to_comments = False
        self.reply_to_comments_percent = 0
        self.comment_replies = []
        self.photo_comment_replies = []
        self.video_comment_replies = []

        self.liked_img = 0
        self.already_liked = 0
        self.liked_comments = 0
        self.commented = 0
        self.replied_to_comments = 0
        self.followed = 0
        self.already_followed = 0
        self.unfollowed = 0
        self.followed_by = 0
        self.following_num = 0
        self.inap_img = 0
        self.not_valid_users = 0
        self.video_played = 0
        self.already_Visited = 0
        self.stories_watched = 0
        self.reels_watched = 0

        self.follow_times = 1
        self.share_times = 1
        self.comment_times = 1
        self.do_follow = False
        self.follow_percentage = 0
        self.dont_include = set()
        self.white_list = set()
        self.blacklist = {"enabled": "True", "campaign": ""}
        self.automatedFollowedPool = {"all": [], "eligible": []}
        self.do_like = False
        self.like_percentage = 0
        self.do_story = False
        self.story_percentage = 0
        self.story_simulate = False
        self.smart_hashtags = []
        self.smart_location_hashtags = []

        self.dont_like = ["sex", "nsfw"]
        self.mandatory_words = []
        self.ignore_if_contains = []
        self.ignore_users = []

        self.user_interact_amount = 0
        self.user_interact_media = None
        self.user_interact_percentage = 0
        self.user_interact_random = False
        self.dont_follow_inap_post = True

        self.use_clarifai = False
        self.clarifai_api_key = None
        self.clarifai_models = []
        self.clarifai_workflow = []
        self.clarifai_probability = 0.50
        self.clarifai_img_tags = []
        self.clarifai_img_tags_skip = []
        self.clarifai_full_match = False
        self.clarifai_check_video = False
        self.clarifai_proxy = None

        self.potency_ratio = None  # 1.3466
        self.delimit_by_numbers = None

        self.max_followers = None  # 90000
        self.max_following = None  # 66834
        self.min_followers = None  # 35
        self.min_following = None  # 27

        self.delimit_liking = False
        self.liking_approved = True
        self.max_likes = 1000
        self.min_likes = 0

        self.delimit_commenting = False
        self.commenting_approved = True
        self.max_comments = 35
        self.min_comments = 0
        self.comments_mandatory_words = []
        self.max_posts = None
        self.min_posts = None
        self.skip_business_categories = []
        self.skip_bio_keyword = []
        self.dont_skip_business_categories = []
        self.skip_business = False
        self.skip_non_business = False
        self.skip_no_profile_pic = False
        self.skip_private = True
        self.skip_business_percentage = 100
        self.skip_no_profile_pic_percentage = 100
        self.skip_private_percentage = 100
        self.relationship_data = {username: {"all_following": [], "all_followers": []}}

        self.simulation = {"enabled": True, "percentage": 100}

        self.mandatory_language = False
        self.mandatory_character = []
        self.check_letters = {}

        # use this variable to terminate the nested loops after quotient
        # reaches
        self.quotient_breach = False
        # hold the consecutive jumps and set max of it used with QS to break
        # loops
        self.jumps = {
            "consequent": {"likes": 0, "comments": 0, "follows": 0, "unfollows": 0},
            "limit": {"likes": 7, "comments": 3, "follows": 5, "unfollows": 4},
        }

        self.allowed_pod_topics = [
            "general",
            "fashion",
            "food",
            "travel",
            "sports",
            "entertainment",
        ]
        self.allowed_pod_engagement_modes = ["no_comments", "light", "normal", "heavy"]

        # stores the features' name which are being used by other features
        self.internal_usage = {}

        self.aborting = False
        self.start_time = time.time()

        # proxy address
        self.proxy_address = proxy_address

        # assign logger
        self.show_logs = show_logs
        Settings.show_logs = show_logs or None
        self.multi_logs = multi_logs
        self.logfolder = get_logfolder(self.username, self.multi_logs)
        self.logger = self.get_instapy_logger(self.show_logs, log_handler)

        get_database(make=True)  # IMPORTANT: think twice before relocating

        if selenium_local_session:
            self.browser, err_msg = set_selenium_local_session(
                proxy_address,
                proxy_port,
                proxy_username,
                proxy_password,
                headless_browser,
                browser_profile_path,
                disable_image_load,
                page_delay,
                geckodriver_path,
                self.logger,
            )
            if len(err_msg) > 0:
                raise InstaPyError(err_msg)

    def get_instapy_logger(self, show_logs: bool, log_handler=None):
        """
        Handles the creation and retrieval of loggers to avoid
        re-instantiation.
        """

        existing_logger = Settings.loggers.get(self.username)
        if existing_logger is not None:
            return existing_logger
        else:
            # initialize and setup logging system for the InstaPy object
            logger = logging.getLogger(self.username)
            logger.setLevel(logging.DEBUG)
            file_handler = logging.FileHandler("{}general.log".format(self.logfolder))
            file_handler.setLevel(logging.DEBUG)
            extra = {"username": self.username}
            logger_formatter = logging.Formatter(
                "%(levelname)s [%(asctime)s] [%(username)s]  %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(logger_formatter)
            logger.addHandler(file_handler)

            # add custom user handler if given
            if log_handler:
                logger.addHandler(log_handler)

            if show_logs is True:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                console_handler.setFormatter(logger_formatter)
                logger.addHandler(console_handler)

            logger = logging.LoggerAdapter(logger, extra)

            Settings.loggers[self.username] = logger
            Settings.logger = logger
            return logger

    def set_selenium_remote_session(
        self, logger, selenium_url: str = "", selenium_driver=None
    ):
        """
        Starts remote session for a selenium server.
        Creates a new selenium driver instance for remote session or uses provided
        one. Useful for docker setup.

        :param selenium_url: string
        :param selenium_driver: selenium WebDriver
        :return: self
        """
        if self.aborting:
            return self

        if selenium_driver:
            self.browser = selenium_driver
        else:
            self.browser = webdriver.Remote(
                command_executor=selenium_url,
                desired_capabilities=DesiredCapabilities.FIREFOX,
            )

        # convert_selenium_browser(selenium_driver)
        message = "Session started!"
        highlight_print("browser", message, "initialization", "info", logger)

        return self

    def login(self):
        """Used to login the user either with the username and password"""
        # InstaPy uses page_delay speed to implicit wait for elements,
        # here we're decreasing it to 5 seconds instead of the default 25 seconds
        # to speed up the login process.
        #
        # In short: default page_delay speed took 25 seconds trying to locate every
        # element, now it's taking 5 seconds.
        temporary_page_delay = 5
        self.browser.implicitly_wait(temporary_page_delay)

        if not login_user(
            self.browser,
            self.username,
            self.password,
            self.logger,
            self.logfolder,
            self.proxy_address,
            self.bypass_security_challenge_using,
        ):
            message = (
                "Unable to login to Instagram! "
                "You will find more information in the logs above."
            )
            highlight_print(self.username, message, "login", "critical", self.logger)

            self.aborting = True
            return self

        # back the page_delay to default, or the value set by the user
        self.browser.implicitly_wait(self.page_delay)
        message = "Logged in successfully!"
        highlight_print(self.username, message, "login", "info", self.logger)
        # try to save account progress
        try:
            save_account_progress(self.browser, self.username, self.logger)
        except Exception as e:
            self.logger.warning(
                "Unable to save account progress, skipping data update " + str(e)
            )

        # logs only followers/following numbers when able to login,
        # to speed up the login process and avoid loading profile
        # page (meaning less server calls)
        self.followed_by = log_follower_num(self.browser, self.username, self.logfolder)
        self.following_num = log_following_num(
            self.browser, self.username, self.logfolder
        )

        return self

    def set_sleep_reduce(self, percentage: int):
        set_sleep_percentage(percentage)
        return self

    def set_action_delays(
        self,
        enabled: bool = False,
        like: int = None,
        comment: int = None,
        follow: int = None,
        unfollow: int = None,
        story: int = None,
        randomize: bool = False,
        random_range_from: int = None,
        random_range_to: int = None,
        safety_match: bool = True,
    ):
        """ Set custom sleep delay after actions """
        Settings.action_delays.update(
            {
                "enabled": enabled,
                "like": like,
                "comment": comment,
                "follow": follow,
                "unfollow": unfollow,
                "story": story,
                "randomize": randomize,
                "random_range": (random_range_from, random_range_to),
                "safety_match": safety_match,
            }
        )

    def set_do_comment(self, enabled: bool = False, percentage: int = 0):
        """
        Defines if images should be commented or not.
        E.g. percentage=25 means every ~4th picture will be commented.
        """

        if self.aborting:
            return self

        self.do_comment = enabled
        self.comment_percentage = percentage

        return self

    def set_comments(self, comments: list = [], media: str = None):
        """
        Sets the possible posted comments.
        'What an amazing shot :heart_eyes: !' is an example for using emojis.
        """
        if self.aborting:
            return self

        if media not in [None, "Photo", "Video"]:
            self.logger.warning('Unkown media type! Treating as "any".')
            media = None

        self.comments = comments

        if media is None:
            self.comments = comments
        else:
            attr = "{}_comments".format(media.lower())
            setattr(self, attr, comments)

        return self

    def set_do_follow(self, enabled: bool = False, percentage: int = 0, times: int = 1):
        """Defines if the user of the liked image should be followed"""
        if self.aborting:
            return self

        self.follow_times = times
        self.do_follow = enabled
        self.follow_percentage = percentage

        return self

    def set_do_like(self, enabled: bool = False, percentage: int = 0):
        if self.aborting:
            return self

        self.do_like = enabled
        self.like_percentage = min(percentage, 100)

        return self

    def set_do_story(
        self, enabled: bool = False, percentage: int = 0, simulate: bool = False
    ):
        """
            configure stories
            enabled: to add story to interact
            percentage: how much to watch
            simulate: if True, we will simulate watching (faster),
                      but nothing will be seen on the browser window
        """
        if self.aborting:
            return self

        self.do_story = enabled
        self.story_percentage = min(percentage, 100)
        self.story_simulate = simulate

        return self

    def set_dont_like(self, tags: list = []):
        """Changes the possible restriction tags, if one of this
         words is in the description, the image won't be liked but user
         still might be unfollowed"""
        if self.aborting:
            return self

        if not isinstance(tags, list):
            self.logger.warning("Unable to use your set_dont_like " "configuration!")
            self.aborting = True

        self.dont_like = tags

        return self

    def set_mandatory_words(self, tags: list = []):
        """Changes the possible restriction tags, if all of this
         hashtags is in the description, the image will be liked"""
        if self.aborting:
            return self

        if not isinstance(tags, list):
            self.logger.warning(
                "Unable to use your set_mandatory_words " "configuration!"
            )
            self.aborting = True

        self.mandatory_words = tags

        return self

    def set_user_interact(
        self,
        amount: int = 10,
        percentage: int = 100,
        randomize: bool = False,
        media: str = None,
    ):
        """Define if posts of given user should be interacted"""
        if self.aborting:
            return self

        self.user_interact_amount = amount
        self.user_interact_random = randomize
        self.user_interact_percentage = percentage
        self.user_interact_media = media

        return self

    def set_ignore_users(self, users: list = []):
        """Changes the possible restriction to users, if a user who posts
        is one of these, the image won't be liked"""
        if self.aborting:
            return self

        self.ignore_users = users

        return self

    def set_ignore_if_contains(self, words: list = []):
        """Ignores the don't likes if the description contains
        one of the given words"""
        if self.aborting:
            return self

        self.ignore_if_contains = words

        return self

    def set_dont_include(self, friends: list = None):
        """Defines which accounts should not be unfollowed"""
        if self.aborting:
            return self

        self.dont_include = set(friends) or set()
        self.white_list = set(friends) or set()

        return self

    def set_switch_language(self, option: bool = True):
        self.switch_language = option
        return self

    def set_use_clarifai(
        self,
        enabled: bool = False,
        api_key: str = None,
        models: list = ["general"],
        workflow: list = [],
        probability: float = 0.50,
        full_match: bool = False,
        check_video: bool = False,
        proxy: str = None,
    ):
        """
        Defines if the clarifai img api should be used
        Which 'project' will be used (only 5000 calls per month)

        Raises:
            InstaPyError if os is windows
        """
        if self.aborting:
            return self

        # if os.name == 'nt':
        #    raise InstaPyError('Clarifai is not supported on Windows')

        self.use_clarifai = enabled

        if api_key is None and self.clarifai_api_key is None:
            self.clarifai_api_key = os.environ.get("CLARIFAI_API_KEY")
        elif api_key is not None:
            self.clarifai_api_key = api_key

        self.clarifai_models = models
        self.clarifai_workflow = workflow
        self.clarifai_probability = probability
        self.clarifai_full_match = full_match
        self.clarifai_check_video = check_video

        if proxy is not None:
            self.clarifai_proxy = "https://" + proxy

        return self

    def set_smart_hashtags(
        self,
        tags: list = None,
        limit: int = 3,
        sort: str = "top",
        log_tags: bool = True,
    ):
        """Generate smart hashtags based on https://displaypurposes.com/"""
        """ranking, banned and spammy tags are filtered out."""

        if tags is None:
            print("set_smart_hashtags is misconfigured")
            return

        for tag in tags:
            req = requests.get(
                "https://d212rkvo8t62el.cloudfront.net/tag/{}".format(tag)
            )
            data = json.loads(req.text)

            if data["tagExists"] is True:
                if sort == "top":
                    # sort by ranking
                    ordered_tags_by_rank = sorted(
                        data["results"], key=lambda d: d["rank"], reverse=True
                    )
                    ranked_tags = ordered_tags_by_rank[:limit]
                    for item in ranked_tags:
                        # add smart hashtag to like list
                        self.smart_hashtags.append(item["tag"])

                elif sort == "random":
                    if len(data["results"]) < limit:
                        random_tags = random.sample(
                            data["results"], len(data["results"])
                        )
                    else:
                        random_tags = random.sample(data["results"], limit)
                    for item in random_tags:
                        self.smart_hashtags.append(item["tag"])

                if log_tags is True:
                    for item in self.smart_hashtags:
                        print("[smart hashtag generated: {}]".format(item))
            else:
                print("Too few results for #{} tag".format(tag))

        # delete duplicated tags
        self.smart_hashtags = list(set(self.smart_hashtags))
        return self

    def set_smart_location_hashtags(
        self, locations: list, radius: int = 10, limit: int = 3, log_tags: bool = True
    ):
        """Generate smart hashtags based on https://displaypurposes.com/map"""
        if locations is None:
            self.logger.error("set_smart_location_hashtags is misconfigured")
            return self

        for location in locations:
            lat, lon = get_cord_location(self.browser, location)

            bbox = get_bounding_box(
                lat, lon, logger=self.logger, half_side_in_miles=radius
            )
            bbox_url = "{},{},{},{}&zoom={}".format(
                bbox["lon_min"],
                bbox["lat_min"],
                bbox["lon_max"],
                bbox["lat_max"],
                radius,
            )
            url = "https://query.displaypurposes.com/local/?bbox={}".format(bbox_url)

            req = requests.get(url)
            data = json.loads(req.text)
            if int(data["count"]) == 0:
                self.logger.warning("Too few results for {} location".format(location))
                continue

            count = limit if limit < data["count"] else data["count"]
            i = 0
            tags = []
            while i < count:
                self.smart_location_hashtags.append(data["tags"][i]["tag"])
                i += 1

        self.smart_location_hashtags = list(set(self.smart_location_hashtags))

        if log_tags is True:
            self.logger.info(
                "[smart location hashtag generated: {}]\n".format(
                    self.smart_location_hashtags
                )
            )

        return self

    def set_mandatory_language(
        self, enabled: bool = False, character_set: list = ["LATIN"]
    ):
        """Restrict the description of the image to a character set"""

        if self.aborting:
            return self

        char_set = []

        if not isinstance(character_set, list):
            character_set = [character_set]

        for chr_set in character_set:
            if chr_set not in [
                "LATIN",
                "GREEK",
                "CYRILLIC",
                "ARABIC",
                "HEBREW",
                "CJK",
                "HANGUL",
                "HIRAGANA",
                "KATAKANA",
                "THAI",
                "MATHEMATICAL",
            ]:
                self.logger.warning('Unkown character set! Treating as "LATIN".')
                ch_set_name = "LATIN"
            else:
                ch_set_name = chr_set

            if ch_set_name not in char_set:
                char_set.append(ch_set_name)

        self.mandatory_language = enabled
        self.mandatory_character = char_set

        return self

    def clarifai_check_img_for(
        self,
        tags: list = None,
        tags_skip: list = None,
        comment: bool = False,
        comments: list = None,
    ):
        """Defines the tags the images should be checked for"""
        if self.aborting:
            return self

        if tags is None and not self.clarifai_img_tags:
            self.use_clarifai = False
        elif tags:
            self.clarifai_img_tags.append((tags, comment, comments))
            self.clarifai_img_tags_skip = tags_skip or []

        return self

    def query_clarifai(self):
        """Method for querying Clarifai using parameters set in
        clarifai_check_img_for"""
        return check_image(
            self.browser,
            self.clarifai_api_key,
            self.clarifai_img_tags,
            self.clarifai_img_tags_skip,
            self.logger,
            self.clarifai_models,
            self.clarifai_workflow,
            self.clarifai_probability,
            self.clarifai_full_match,
            self.clarifai_check_video,
            proxy=self.clarifai_proxy,
        )

    def follow_commenters(
        self,
        usernames: list,
        amount: int = 10,
        daysold: int = 365,
        max_pic: int = 50,
        sleep_delay: int = 600,
        interact: bool = False,
    ):
        """ Follows users' commenters """

        if self.aborting:
            return self

        message = "Starting to follow commenters.."
        highlight_print(self.username, message, "feature", "info", self.logger)

        if not isinstance(usernames, list):
            usernames = [usernames]

        followed_all = 0
        followed_new = 0

        # hold the current global values for differentiating at the end
        already_followed_init = self.already_followed
        not_valid_users_init = self.not_valid_users
        liked_init = self.liked_img
        already_liked_init = self.already_liked
        commented_init = self.commented
        inap_img_init = self.inap_img

        relax_point = random.randint(7, 14)  # you can use some plain value
        # `10` instead of this quitely randomized score
        self.quotient_breach = False

        for username in usernames:
            if self.quotient_breach:
                break

            self.logger.info(
                "Following commenters of '{}' from {} pictures in last {} "
                "days...\nScrapping wall..".format(username, max_pic, daysold)
            )
            commenters = extract_information(self.browser, username, daysold, max_pic)

            if len(commenters) > 0:
                self.logger.info("Going to follow top {} users.\n".format(amount))
                sleep(1)
                # This way of iterating will prevent sleep interference
                # between functions
                random.shuffle(commenters)
                for commenter in commenters[:amount]:
                    if self.quotient_breach:
                        self.logger.warning(
                            "--> Follow quotient reached its peak!"
                            "\t~leaving Follow-Commenters activity\n"
                        )
                        break

                    with self.feature_in_feature("follow_by_list", True):
                        followed = self.follow_by_list(
                            commenter, self.follow_times, sleep_delay, interact
                        )
                    if followed > 0:
                        followed_all += 1
                        followed_new += 1
                        self.logger.info("Total Follow: {}\n".format(str(followed_all)))
                        # Take a break after a good following
                        if followed_new >= relax_point:
                            delay_random = random.randint(
                                ceil(sleep_delay * 0.85), ceil(sleep_delay * 1.14)
                            )
                            sleep_time = (
                                "{} seconds".format(delay_random)
                                if delay_random < 60
                                else "{} minutes".format(
                                    truncate_float(delay_random / 60, 2)
                                )
                            )
                            self.logger.info(
                                "------=>  Followed {} new users ~sleeping "
                                "about {}".format(followed_new, sleep_time)
                            )
                            sleep(delay_random)
                            relax_point = random.randint(7, 14)
                            followed_new = 0
                            pass

            else:
                self.logger.info("Noone commented, noone to follow.\n")

            sleep(1)

        self.logger.info("Finished following Commenters!\n")

        # find the feature-wide action sizes by taking a difference
        already_followed = self.already_followed - already_followed_init
        not_valid_users = self.not_valid_users - not_valid_users_init
        liked = self.liked_img - liked_init
        already_liked = self.already_liked - already_liked_init
        commented = self.commented - commented_init
        inap_img = self.inap_img - inap_img_init

        # print results
        self.logger.info("Followed: {}".format(followed_all))
        self.logger.info("Already followed: {}".format(already_followed))
        self.logger.info("Not valid users: {}".format(not_valid_users))

        if interact is True:
            print("")
            # print results out of interactions
            self.logger.info("Liked: {}".format(liked))
            self.logger.info("Already Liked: {}".format(already_liked))
            self.logger.info("Commented: {}".format(commented))
            self.logger.info("Inappropriate: {}".format(inap_img))

        return self

    def follow_likers(
        self,
        usernames: list,
        photos_grab_amount: int = 3,
        follow_likers_per_photo: int = 3,
        randomize: bool = True,
        sleep_delay: int = 600,
        interact: bool = False,
    ):
        """ Follows users' likers """
        if self.aborting:
            return self

        message = "Starting to follow likers.."
        highlight_print(self.username, message, "feature", "info", self.logger)

        if not isinstance(usernames, list):
            usernames = [usernames]

        if photos_grab_amount > 12:
            self.logger.info(
                "Sorry, you can only grab likers from first 12 photos for "
                "given username now.\n"
            )
            photos_grab_amount = 12

        followed_all = 0
        followed_new = 0

        # hold the current global values for differentiating at the end
        already_followed_init = self.already_followed
        not_valid_users_init = self.not_valid_users
        liked_init = self.liked_img
        already_liked_init = self.already_liked
        commented_init = self.commented
        inap_img_init = self.inap_img

        relax_point = random.randint(7, 14)  # you can use some plain value
        # `10` instead of this quitely randomized score
        self.quotient_breach = False

        for username in usernames:
            if self.quotient_breach:
                break

            photo_urls = get_photo_urls_from_profile(
                self.browser, username, photos_grab_amount, randomize
            )
            sleep(1)
            if not isinstance(photo_urls, list):
                photo_urls = [photo_urls]

            for photo_url in photo_urls:
                if self.quotient_breach:
                    break

                likers = users_liked(self.browser, photo_url, follow_likers_per_photo)
                # This way of iterating will prevent sleep interference
                # between functions
                random.shuffle(likers)

                for liker in likers[:follow_likers_per_photo]:
                    if self.quotient_breach:
                        self.logger.warning(
                            "--> Follow quotient reached its peak!"
                            "\t~leaving Follow-Likers activity\n"
                        )
                        break

                    with self.feature_in_feature("follow_by_list", True):
                        followed = self.follow_by_list(
                            liker, self.follow_times, sleep_delay, interact
                        )
                    if followed > 0:
                        followed_all += 1
                        followed_new += 1
                        self.logger.info("Total Follow: {}\n".format(str(followed_all)))
                        # Take a break after a good following
                        if followed_new >= relax_point:
                            delay_random = random.randint(
                                ceil(sleep_delay * 0.85), ceil(sleep_delay * 1.14)
                            )
                            sleep_time = (
                                "{} seconds".format(delay_random)
                                if delay_random < 60
                                else "{} minutes".format(
                                    truncate_float(delay_random / 60, 2)
                                )
                            )
                            self.logger.info(
                                "------=>  Followed {} new users ~sleeping "
                                "about {}".format(followed_new, sleep_time)
                            )
                            sleep(delay_random)
                            relax_point = random.randint(7, 14)
                            followed_new = 0
                            pass

        self.logger.info("Finished following Likers!\n")

        # find the feature-wide action sizes by taking a difference
        already_followed = self.already_followed - already_followed_init
        not_valid_users = self.not_valid_users - not_valid_users_init
        liked = self.liked_img - liked_init
        already_liked = self.already_liked - already_liked_init
        commented = self.commented - commented_init
        inap_img = self.inap_img - inap_img_init

        # print results
        self.logger.info("Followed: {}".format(followed_all))
        self.logger.info("Already followed: {}".format(already_followed))
        self.logger.info("Not valid users: {}".format(not_valid_users))

        if interact is True:
            print("")
            # print results out of interactions
            self.logger.info("Liked: {}".format(liked))
            self.logger.info("Already Liked: {}".format(already_liked))
            self.logger.info("Commented: {}".format(commented))
            self.logger.info("Inappropriate: {}".format(inap_img))

        return self

    def follow_by_list(
        self,
        followlist: list,
        times: int = 1,
        sleep_delay: int = 600,
        interact: bool = False,
    ):
        """Allows to follow by any scrapped list"""
        if not isinstance(followlist, list):
            followlist = [followlist]

        if self.aborting:
            self.logger.info(">>> self aborting prevented")
            # return self

        # standalone means this feature is started by the user
        standalone = (
            True if "follow_by_list" not in self.internal_usage.keys() else False
        )
        # skip validation in case of it is already accomplished
        users_validated = (
            True
            if not standalone and not self.internal_usage["follow_by_list"]["validate"]
            else False
        )

        self.follow_times = times or 0

        followed_all = 0
        followed_new = 0
        already_followed = 0
        not_valid_users = 0

        # hold the current global values for differentiating at the end
        liked_init = self.liked_img
        already_liked_init = self.already_liked
        commented_init = self.commented
        inap_img_init = self.inap_img

        relax_point = random.randint(7, 14)  # you can use some plain value
        # `10` instead of this quitely randomized score
        self.quotient_breach = False

        for acc_to_follow in followlist:
            if self.jumps["consequent"]["follows"] >= self.jumps["limit"]["follows"]:
                self.logger.warning(
                    "--> Follow quotient reached its peak!\t~leaving "
                    "Follow-By-Tags activity\n"
                )
                # reset jump counter before breaking the loop
                self.jumps["consequent"]["follows"] = 0
                # turn on `quotient_breach` to break the internal iterators
                # of the caller
                self.quotient_breach = True if not standalone else False
                break

            if follow_restriction(
                "read", acc_to_follow, self.follow_times, self.logger
            ):
                print("")
                continue

            if not users_validated:
                # Verify if the user should be followed
                validation, details = self.validate_user_call(acc_to_follow)
                if validation is not True or acc_to_follow == self.username:
                    self.logger.info("--> Not a valid user: {}".format(details))
                    not_valid_users += 1
                    continue

            # Take a break after a good following
            if followed_new >= relax_point:
                delay_random = random.randint(
                    ceil(sleep_delay * 0.85), ceil(sleep_delay * 1.14)
                )
                sleep_time = (
                    "{} seconds".format(delay_random)
                    if delay_random < 60
                    else "{} minutes".format(truncate_float(delay_random / 60, 2))
                )
                self.logger.info(
                    "Followed {} new users  ~sleeping about {}\n".format(
                        followed_new, sleep_time
                    )
                )
                sleep(delay_random)
                followed_new = 0
                relax_point = random.randint(7, 14)
                pass

            if not follow_restriction(
                "read", acc_to_follow, self.follow_times, self.logger
            ):
                follow_state, msg = follow_user(
                    self.browser,
                    "profile",
                    self.username,
                    acc_to_follow,
                    None,
                    self.blacklist,
                    self.logger,
                    self.logfolder,
                )
                sleep(random.randint(1, 3))

                if follow_state is True:
                    followed_all += 1
                    followed_new += 1
                    # reset jump counter after a successful follow
                    self.jumps["consequent"]["follows"] = 0

                    if standalone:  # print only for external usage (
                        # internal callers have their printers)
                        self.logger.info("Total Follow: {}\n".format(str(followed_all)))

                    # Check if interaction is expected
                    if interact and self.do_like:
                        do_interact = (
                            random.randint(0, 100) <= self.user_interact_percentage
                        )
                        # Do interactions if any
                        if do_interact and self.user_interact_amount > 0:
                            # store original value of `self.do_follow`
                            original_do_follow = self.do_follow
                            # disable following temporarily
                            # cos the user is already followed
                            self.do_follow = False

                            # disable revalidating user in interact_by_users
                            with self.feature_in_feature("interact_by_users", False):
                                self.interact_by_users(
                                    acc_to_follow,
                                    self.user_interact_amount,
                                    self.user_interact_random,
                                    self.user_interact_media,
                                )

                            # revert back to original `self.do_follow` value
                            self.do_follow = original_do_follow

                elif msg == "already followed":
                    already_followed += 1

                elif msg == "jumped":
                    # will break the loop after certain consecutive jumps
                    self.jumps["consequent"]["follows"] += 1

                sleep(1)

        if standalone:  # print only for external usage (internal callers
            # have their printers)
            self.logger.info("Finished following by List!\n")
            # print summary
            self.logger.info("Followed: {}".format(followed_all))
            self.logger.info("Already followed: {}".format(already_followed))
            self.logger.info("Not valid users: {}".format(not_valid_users))

            if interact is True:
                print("")
                # find the feature-wide action sizes by taking a difference
                liked = self.liked_img - liked_init
                already_liked = self.already_liked - already_liked_init
                commented = self.commented - commented_init
                inap_img = self.inap_img - inap_img_init

                # print the summary out of interactions
                self.logger.info("Liked: {}".format(liked))
                self.logger.info("Already Liked: {}".format(already_liked))
                self.logger.info("Commented: {}".format(commented))
                self.logger.info("Inappropriate: {}".format(inap_img))

        # always sum up general objects regardless of the request size
        self.followed += followed_all
        self.already_followed += already_followed
        self.not_valid_users += not_valid_users

        return followed_all

    def set_relationship_bounds(
        self,
        enabled: bool = False,
        potency_ratio: float = None,
        delimit_by_numbers: bool = None,
        min_posts: int = None,
        max_posts: int = None,
        max_followers: int = None,
        max_following: int = None,
        min_followers: int = None,
        min_following: int = None,
    ):
        """Sets the potency ratio and limits to the provide an efficient
        activity between the targeted masses"""

        self.potency_ratio = potency_ratio if enabled is True else None
        self.delimit_by_numbers = delimit_by_numbers if enabled is True else None

        self.max_followers = max_followers
        self.min_followers = min_followers

        self.max_following = max_following
        self.min_following = min_following

        self.min_posts = min_posts if enabled is True else None
        self.max_posts = max_posts if enabled is True else None

    def validate_user_call(self, user_name: str):
        """ Short call of validate_username() function """
        validation, details = validate_username(
            self.browser,
            user_name,
            self.username,
            self.ignore_users,
            self.blacklist,
            self.potency_ratio,
            self.delimit_by_numbers,
            self.max_followers,
            self.max_following,
            self.min_followers,
            self.min_following,
            self.min_posts,
            self.max_posts,
            self.skip_private,
            self.skip_private_percentage,
            self.skip_no_profile_pic,
            self.skip_no_profile_pic_percentage,
            self.skip_business,
            self.skip_non_business,
            self.skip_business_percentage,
            self.skip_business_categories,
            self.dont_skip_business_categories,
            self.skip_bio_keyword,
            self.logger,
            self.logfolder,
        )
        return validation, details

    def fetch_smart_comments(self, is_video: bool, temp_comments: list):
        if temp_comments:
            # Use clarifai related comments only!
            comments = temp_comments
        elif is_video:
            comments = self.comments + self.video_comments
        else:
            comments = self.comments + self.photo_comments

        return comments

    def set_skip_users(
        self,
        skip_private: bool = True,
        private_percentage: int = 100,
        skip_no_profile_pic: bool = False,
        no_profile_pic_percentage: int = 100,
        skip_business: bool = False,
        business_percentage: int = 100,
        skip_business_categories: list = [],
        skip_bio_keyword: list = [],
        dont_skip_business_categories: list = [],
        skip_non_business: bool = False,
    ):

        self.skip_business = skip_business
        self.skip_private = skip_private
        self.skip_no_profile_pic = skip_no_profile_pic
        self.skip_business_percentage = business_percentage
        self.skip_no_profile_pic_percentage = no_profile_pic_percentage
        self.skip_private_percentage = private_percentage
        self.skip_non_business = skip_non_business
        self.skip_bio_keyword = skip_bio_keyword
        if skip_business:
            self.skip_business_categories = skip_business_categories
            if len(skip_business_categories) == 0:
                self.dont_skip_business_categories = dont_skip_business_categories
            else:
                if len(dont_skip_business_categories) != 0:
                    self.logger.warning(
                        "Both skip_business_categories and "
                        "dont_skip_business categories provided in "
                        "skip_business feature,"
                        + "will skip only the categories listed in "
                        "skip_business_categories parameter"
                    )
                    # dont_skip_business_categories = [] Setted by default
                    # in init

    def set_delimit_liking(
        self, enabled: bool = False, max_likes: int = None, min_likes: int = None
    ):

        self.delimit_liking = True if enabled is True else False
        self.max_likes = max_likes
        self.min_likes = min_likes

    def set_delimit_commenting(
        self,
        enabled: bool = False,
        max_comments: int = None,
        min_comments: int = None,
        comments_mandatory_words: list = [],
    ):

        self.delimit_commenting = True if enabled is True else False
        self.max_comments = max_comments
        self.min_comments = min_comments

        # comment only when the image description contain at least one of
        # those words
        self.comments_mandatory_words = comments_mandatory_words

    def set_simulation(self, enabled: bool = True, percentage: int = 100):
        """ Sets aside simulation parameters """
        if enabled not in [True, False]:
            self.logger.info(
                "Invalid simulation parameter! Please use correct syntax "
                "with accepted values."
            )

        elif enabled is False:
            self.simulation["enabled"] = False

        else:
            percentage = 0 if percentage is None else percentage
            self.simulation = {"enabled": True, "percentage": percentage}

    def like_by_locations(
        self,
        locations: list = None,
        amount: int = 50,
        media: str = None,
        skip_top_posts: bool = True,
    ):
        """Likes (default) 50 images per given locations"""
        if self.aborting:
            return self

        liked_img = 0
        already_liked = 0
        inap_img = 0
        commented = 0
        followed = 0
        not_valid_users = 0

        locations = locations or []
        self.quotient_breach = False

        for index, location in enumerate(locations):
            if self.quotient_breach:
                break

            self.logger.info("Location [{}/{}]".format(index + 1, len(locations)))
            self.logger.info("--> {}".format(location.encode("utf-8")))

            try:
                links = get_links_for_location(
                    self.browser, location, amount, self.logger, media, skip_top_posts
                )
            except NoSuchElementException as exc:
                self.logger.warning(
                    "Error occurred while getting images from location: {}  "
                    "~maybe too few images exist\n\t{}\n".format(
                        location, str(exc).encode("utf-8")
                    )
                )
                continue

            for i, link in enumerate(links):
                if self.jumps["consequent"]["likes"] >= self.jumps["limit"]["likes"]:
                    self.logger.warning(
                        "--> Like quotient reached its peak!\t~leaving "
                        "Like-By-Locations activity\n"
                    )
                    self.quotient_breach = True
                    # reset jump counter after a breach report
                    self.jumps["consequent"]["likes"] = 0
                    break

                self.logger.info("Like# [{}/{}]".format(i + 1, len(links)))
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason, scope = check_link(
                        self.browser,
                        link,
                        self.dont_like,
                        self.mandatory_words,
                        self.mandatory_language,
                        self.is_mandatory_character,
                        self.mandatory_character,
                        self.check_character_set,
                        self.ignore_if_contains,
                        self.logger,
                    )

                    if not inappropriate and self.delimit_liking:
                        self.liking_approved = verify_liking(
                            self.browser, self.max_likes, self.min_likes, self.logger
                        )

                    if not inappropriate and self.liking_approved:
                        # validate user
                        validation, details = self.validate_user_call(user_name)

                        if validation is not True:
                            self.logger.info("--> Not a valid user: {}".format(details))
                            not_valid_users += 1
                            continue
                        else:
                            web_address_navigator(self.browser, link)

                        # try to like
                        like_state, msg = like_image(
                            self.browser,
                            user_name,
                            self.blacklist,
                            self.logger,
                            self.logfolder,
                            liked_img,
                        )

                        if like_state is True:
                            liked_img += 1
                            # reset jump counter after a successful like
                            self.jumps["consequent"]["likes"] = 0

                            checked_img = True
                            temp_comments = []

                            commenting = (
                                random.randint(0, 100) <= self.comment_percentage
                            )
                            following = random.randint(0, 100) <= self.follow_percentage

                            if self.use_clarifai and (following or commenting):
                                try:
                                    checked_img, temp_comments, clarifai_tags = (
                                        self.query_clarifai()
                                    )

                                except Exception as err:
                                    self.logger.error(
                                        "Image check error: {}".format(err)
                                    )

                            # comments
                            if (
                                self.do_comment
                                and user_name not in self.dont_include
                                and checked_img
                                and commenting
                            ):

                                if self.delimit_commenting:
                                    (
                                        self.commenting_approved,
                                        disapproval_reason,
                                    ) = verify_commenting(
                                        self.browser,
                                        self.max_comments,
                                        self.min_comments,
                                        self.comments_mandatory_words,
                                        self.logger,
                                    )
                                if self.commenting_approved:
                                    # smart commenting
                                    comments = self.fetch_smart_comments(
                                        is_video, temp_comments
                                    )
                                    if comments:
                                        comment_state, msg = comment_image(
                                            self.browser,
                                            user_name,
                                            comments,
                                            self.blacklist,
                                            self.logger,
                                            self.logfolder,
                                        )
                                        if comment_state is True:
                                            commented += 1

                                else:
                                    self.logger.info(disapproval_reason)

                            else:
                                self.logger.info("--> Not commented")
                                sleep(1)

                            # following
                            if (
                                self.do_follow
                                and user_name not in self.dont_include
                                and checked_img
                                and following
                                and not follow_restriction(
                                    "read", user_name, self.follow_times, self.logger
                                )
                            ):

                                follow_state, msg = follow_user(
                                    self.browser,
                                    "post",
                                    self.username,
                                    user_name,
                                    None,
                                    self.blacklist,
                                    self.logger,
                                    self.logfolder,
                                )
                                if follow_state is True:
                                    followed += 1

                            else:
                                self.logger.info("--> Not following")
                                sleep(1)

                        elif msg == "already liked":
                            already_liked += 1

                        elif msg == "block on likes":
                            break

                        elif msg == "jumped":
                            # will break the loop after certain consecutive
                            # jumps
                            self.jumps["consequent"]["likes"] += 1

                    else:
                        self.logger.info(
                            "--> Image not liked: {}".format(reason.encode("utf-8"))
                        )
                        inap_img += 1

                except NoSuchElementException as err:
                    self.logger.error("Invalid Page: {}".format(err))

            self.logger.info("Location: {}".format(location.encode("utf-8")))
            self.logger.info("Liked: {}".format(liked_img))
            self.logger.info("Already Liked: {}".format(already_liked))
            self.logger.info("Commented: {}".format(commented))
            self.logger.info("Followed: {}".format(followed))
            self.logger.info("Inappropriate: {}".format(inap_img))
            self.logger.info("Not valid users: {}\n".format(not_valid_users))

        self.followed += followed
        self.liked_img += liked_img
        self.already_liked += already_liked
        self.commented += commented
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return self

    def comment_by_locations(
        self,
        locations: list = None,
        amount: int = 50,
        media: str = None,
        skip_top_posts: bool = True,
    ):
        """Likes (default) 50 images per given locations"""
        if self.aborting:
            return self

        commented = 0
        followed = 0
        inap_img = 0
        not_valid_users = 0

        locations = locations or []
        self.quotient_breach = False

        for index, location in enumerate(locations):
            if self.quotient_breach:
                break

            self.logger.info("Location [{}/{}]".format(index + 1, len(locations)))
            self.logger.info("--> {}".format(location.encode("utf-8")))

            try:
                links = get_links_for_location(
                    self.browser, location, amount, self.logger, media, skip_top_posts
                )
            except NoSuchElementException:
                self.logger.warning("Too few images, skipping this location")
                continue

            for i, link in enumerate(links):
                if (
                    self.jumps["consequent"]["comments"]
                    >= self.jumps["limit"]["comments"]
                ):
                    self.logger.warning(
                        "--> Comment quotient reached its peak!\t~leaving "
                        "Comment-By-Locations activity\n"
                    )
                    self.quotient_breach = True
                    # reset jump counter after a breach report
                    self.jumps["consequent"]["comments"] = 0
                    break

                self.logger.info("Comment# [{}/{}]".format(i + 1, len(links)))
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason, scope = check_link(
                        self.browser,
                        link,
                        self.dont_like,
                        self.mandatory_words,
                        self.mandatory_language,
                        self.is_mandatory_character,
                        self.mandatory_character,
                        self.check_character_set,
                        self.ignore_if_contains,
                        self.logger,
                    )
                    if not inappropriate:
                        # validate user
                        validation, details = self.validate_user_call(user_name)
                        if validation is not True:
                            self.logger.info(details)
                            not_valid_users += 1
                            continue
                        else:
                            web_address_navigator(self.browser, link)

                        # try to comment
                        self.logger.info(
                            "--> Image not liked: Likes are disabled for the "
                            "'Comment-By-Locations' feature"
                        )

                        checked_img = True
                        temp_comments = []
                        commenting = random.randint(0, 100) <= self.comment_percentage
                        following = random.randint(0, 100) <= self.follow_percentage

                        if not commenting:
                            self.logger.info(
                                "--> Image not commented: skipping out of "
                                "given comment percentage"
                            )
                            continue

                        if self.use_clarifai:
                            try:
                                checked_img, temp_comments, clarifai_tags = (
                                    self.query_clarifai()
                                )

                            except Exception as err:
                                self.logger.error("Image check error: {}".format(err))

                        if (
                            self.do_comment
                            and user_name not in self.dont_include
                            and checked_img
                        ):

                            if self.delimit_commenting:
                                (
                                    self.commenting_approved,
                                    disapproval_reason,
                                ) = verify_commenting(
                                    self.browser,
                                    self.max_comments,
                                    self.min_comments,
                                    self.comments_mandatory_words,
                                    self.logger,
                                )
                            if self.commenting_approved:
                                # smart commenting
                                comments = self.fetch_smart_comments(
                                    is_video, temp_comments
                                )
                                if comments:
                                    comment_state, msg = comment_image(
                                        self.browser,
                                        user_name,
                                        comments,
                                        self.blacklist,
                                        self.logger,
                                        self.logfolder,
                                    )
                                    if comment_state is True:
                                        commented += 1
                                        # reset jump counter after a
                                        # successful comment
                                        self.jumps["consequent"]["comments"] = 0

                                        # try to follow
                                        if (
                                            self.do_follow
                                            and user_name not in self.dont_include
                                            and checked_img
                                            and following
                                            and not follow_restriction(
                                                "read",
                                                user_name,
                                                self.follow_times,
                                                self.logger,
                                            )
                                        ):

                                            follow_state, msg = follow_user(
                                                self.browser,
                                                "post",
                                                self.username,
                                                user_name,
                                                None,
                                                self.blacklist,
                                                self.logger,
                                                self.logfolder,
                                            )
                                            if follow_state is True:
                                                followed += 1

                                        else:
                                            self.logger.info("--> Not following")
                                            sleep(1)

                                elif msg == "jumped":
                                    # will break the loop after certain
                                    # consecutive jumps
                                    self.jumps["consequent"]["comments"] += 1

                            else:
                                self.logger.info(disapproval_reason)

                        else:
                            self.logger.info("--> Not commented")
                            sleep(1)

                    else:
                        self.logger.info(
                            "--> Image not commented: {}".format(reason.encode("utf-8"))
                        )
                        inap_img += 1

                except NoSuchElementException as err:
                    self.logger.error("Invalid Page: {}".format(err))

        self.logger.info("Location: {}".format(location.encode("utf-8")))
        self.logger.info("Commented: {}".format(commented))
        self.logger.info("Followed: {}".format(followed))
        self.logger.info("Inappropriate: {}".format(inap_img))
        self.logger.info("Not valid users: {}\n".format(not_valid_users))

        self.followed += followed
        self.not_valid_users += not_valid_users

        return self

    def like_by_tags(
        self,
        tags: list = None,
        amount: int = 50,
        skip_top_posts: bool = True,
        use_smart_hashtags: bool = False,
        use_smart_location_hashtags: bool = False,
        interact: bool = False,
        randomize: bool = False,
        media: str = None,
    ):
        """Likes (default) 50 images per given tag"""
        if self.aborting:
            return self

        liked_img = 0
        already_liked = 0
        inap_img = 0
        commented = 0
        followed = 0
        not_valid_users = 0

        # if smart hashtag is enabled
        if use_smart_hashtags is True and self.smart_hashtags != []:
            self.logger.info("Using smart hashtags")
            tags = self.smart_hashtags
        elif use_smart_location_hashtags is True and self.smart_location_hashtags != []:
            self.logger.info("Using smart location hashtags")
            tags = self.smart_location_hashtags

        # deletes white spaces in tags
        tags = [tag.strip() for tag in tags]
        tags = tags or []
        self.quotient_breach = False

        for index, tag in enumerate(tags):
            if self.quotient_breach:
                break

            self.logger.info("Tag [{}/{}]".format(index + 1, len(tags)))
            self.logger.info("--> {}".format(tag.encode("utf-8")))

            try:
                links = get_links_for_tag(
                    self.browser,
                    tag,
                    amount,
                    skip_top_posts,
                    randomize,
                    media,
                    self.logger,
                )
            except NoSuchElementException:
                self.logger.info("Too few images, skipping this tag")
                continue

            for i, link in enumerate(links):
                if self.jumps["consequent"]["likes"] >= self.jumps["limit"]["likes"]:
                    self.logger.warning(
                        "--> Like quotient reached its peak!\t~leaving "
                        "Like-By-Tags activity\n"
                    )
                    self.quotient_breach = True
                    # reset jump counter after a breach report
                    self.jumps["consequent"]["likes"] = 0
                    break

                self.logger.info("Like# [{}/{}]".format(i + 1, len(links)))
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason, scope = check_link(
                        self.browser,
                        link,
                        self.dont_like,
                        self.mandatory_words,
                        self.mandatory_language,
                        self.is_mandatory_character,
                        self.mandatory_character,
                        self.check_character_set,
                        self.ignore_if_contains,
                        self.logger,
                    )

                    if not inappropriate and self.delimit_liking:
                        self.liking_approved = verify_liking(
                            self.browser, self.max_likes, self.min_likes, self.logger
                        )

                    if not inappropriate and self.liking_approved:
                        # validate user
                        validation, details = self.validate_user_call(user_name)
                        if validation is not True:
                            self.logger.info(details)
                            not_valid_users += 1
                            continue
                        else:
                            web_address_navigator(self.browser, link)

                        # try to like
                        like_state, msg = like_image(
                            self.browser,
                            user_name,
                            self.blacklist,
                            self.logger,
                            self.logfolder,
                            liked_img,
                        )

                        if like_state is True:
                            liked_img += 1
                            # reset jump counter after a successful like
                            self.jumps["consequent"]["likes"] = 0

                            checked_img = True
                            temp_comments = []

                            commenting = (
                                random.randint(0, 100) <= self.comment_percentage
                            )
                            following = random.randint(0, 100) <= self.follow_percentage

                            if self.use_clarifai and (following or commenting):
                                try:
                                    checked_img, temp_comments, clarifai_tags = (
                                        self.query_clarifai()
                                    )

                                except Exception as err:
                                    self.logger.error(
                                        "Image check error: {}".format(err)
                                    )

                            # comments
                            if (
                                self.do_comment
                                and user_name not in self.dont_include
                                and checked_img
                                and commenting
                            ):

                                if self.delimit_commenting:
                                    (
                                        self.commenting_approved,
                                        disapproval_reason,
                                    ) = verify_commenting(
                                        self.browser,
                                        self.max_comments,
                                        self.min_comments,
                                        self.comments_mandatory_words,
                                        self.logger,
                                    )
                                if self.commenting_approved:
                                    # smart commenting
                                    comments = self.fetch_smart_comments(
                                        is_video, temp_comments
                                    )
                                    if comments:
                                        comment_state, msg = comment_image(
                                            self.browser,
                                            user_name,
                                            comments,
                                            self.blacklist,
                                            self.logger,
                                            self.logfolder,
                                        )
                                        if comment_state is True:
                                            commented += 1

                                else:
                                    self.logger.info(disapproval_reason)

                            else:
                                self.logger.info("--> Not commented")
                                sleep(1)

                            # following
                            if (
                                self.do_follow
                                and user_name not in self.dont_include
                                and checked_img
                                and following
                                and not follow_restriction(
                                    "read", user_name, self.follow_times, self.logger
                                )
                            ):

                                follow_state, msg = follow_user(
                                    self.browser,
                                    "post",
                                    self.username,
                                    user_name,
                                    None,
                                    self.blacklist,
                                    self.logger,
                                    self.logfolder,
                                )
                                if follow_state is True:
                                    followed += 1
                            else:
                                self.logger.info("--> Not following")
                                sleep(1)

                            # interactions (if any)
                            if interact:
                                self.logger.info(
                                    "--> User gonna be interacted: '{}'".format(
                                        user_name
                                    )
                                )

                                # disable revalidating user in like_by_users
                                with self.feature_in_feature("like_by_users", False):
                                    self.like_by_users(
                                        user_name,
                                        self.user_interact_amount,
                                        self.user_interact_random,
                                        self.user_interact_media,
                                    )

                        elif msg == "already liked":
                            already_liked += 1

                        elif msg == "block on likes":
                            break

                        elif msg == "jumped":
                            # will break the loop after certain consecutive
                            # jumps
                            self.jumps["consequent"]["likes"] += 1

                    else:
                        self.logger.info(
                            "--> Image not liked: {}".format(reason.encode("utf-8"))
                        )
                        inap_img += 1

                except NoSuchElementException as err:
                    self.logger.error("Invalid Page: {}".format(err))

            self.logger.info("Tag: {}".format(tag.encode("utf-8")))

        self.logger.info("Liked: {}".format(liked_img))
        self.logger.info("Already Liked: {}".format(already_liked))
        self.logger.info("Commented: {}".format(commented))
        self.logger.info("Followed: {}".format(followed))
        self.logger.info("Inappropriate: {}".format(inap_img))
        self.logger.info("Not valid users: {}\n".format(not_valid_users))

        self.liked_img += liked_img
        self.already_liked += already_liked
        self.commented += commented
        self.followed += followed
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return self

    def like_by_users(
        self,
        usernames: list,
        amount: int = 10,
        randomize: bool = False,
        media: str = None,
    ):
        """Likes some amounts of images for each usernames"""
        if self.aborting:
            return self

        if not isinstance(usernames, list):
            usernames = [usernames]

        # standalone means this feature is started by the user
        standalone = (
            True if "like_by_users" not in self.internal_usage.keys() else False
        )
        # skip validation in case of it is already accomplished
        users_validated = (
            True
            if not standalone and not self.internal_usage["like_by_users"]["validate"]
            else False
        )

        liked_img = 0
        total_liked_img = 0
        already_liked = 0
        inap_img = 0
        commented = 0
        followed = 0
        not_valid_users = 0

        usernames = usernames or []
        self.quotient_breach = False

        for index, username in enumerate(usernames):
            if self.quotient_breach:
                break

            self.logger.info("Username [{}/{}]".format(index + 1, len(usernames)))
            self.logger.info("--> {}".format(username.encode("utf-8")))

            following = random.randint(0, 100) <= self.follow_percentage

            if not users_validated:
                validation, details = self.validate_user_call(username)
                if not validation:
                    self.logger.info("--> Not a valid user: {}".format(details))
                    not_valid_users += 1
                    continue

            try:
                links = get_links_for_username(
                    self.browser,
                    self.username,
                    username,
                    amount,
                    self.logger,
                    self.logfolder,
                    randomize,
                    media,
                )

            except NoSuchElementException:
                self.logger.error("Element not found, skipping this username")
                continue

            if (
                self.do_follow
                and username not in self.dont_include
                and following
                and not follow_restriction(
                    "read", username, self.follow_times, self.logger
                )
            ):
                follow_state, msg = follow_user(
                    self.browser,
                    "profile",
                    self.username,
                    username,
                    None,
                    self.blacklist,
                    self.logger,
                    self.logfolder,
                )
                if follow_state is True:
                    followed += 1
            else:
                self.logger.info("--> Not following")
                sleep(1)

            if links is False:
                continue

            # Reset like counter for every username
            liked_img = 0

            for i, link in enumerate(links):
                # Check if target has reached
                if liked_img >= amount:
                    self.logger.info("-------------")
                    self.logger.info(
                        "--> Total liked image reached it's "
                        "amount given: {}".format(liked_img)
                    )
                    break

                if self.jumps["consequent"]["likes"] >= self.jumps["limit"]["likes"]:
                    self.logger.warning(
                        "--> Like quotient reached its peak!\t~leaving "
                        "Like-By-Users activity\n"
                    )
                    self.quotient_breach = True
                    # reset jump counter after a breach report
                    self.jumps["consequent"]["likes"] = 0
                    break

                self.logger.info("Post [{}/{}]".format(liked_img + 1, amount))
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason, scope = check_link(
                        self.browser,
                        link,
                        self.dont_like,
                        self.mandatory_words,
                        self.mandatory_language,
                        self.is_mandatory_character,
                        self.mandatory_character,
                        self.check_character_set,
                        self.ignore_if_contains,
                        self.logger,
                    )

                    if not inappropriate and self.delimit_liking:
                        self.liking_approved = verify_liking(
                            self.browser, self.max_likes, self.min_likes, self.logger
                        )

                    if not inappropriate and self.liking_approved:
                        like_state, msg = like_image(
                            self.browser,
                            user_name,
                            self.blacklist,
                            self.logger,
                            self.logfolder,
                            total_liked_img,
                        )
                        if like_state is True:
                            total_liked_img += 1
                            liked_img += 1
                            # reset jump counter after a successful like
                            self.jumps["consequent"]["likes"] = 0

                            checked_img = True
                            temp_comments = []

                            commenting = (
                                random.randint(0, 100) <= self.comment_percentage
                            )

                            if self.use_clarifai and (following or commenting):
                                try:
                                    checked_img, temp_comments, clarifai_tags = (
                                        self.query_clarifai()
                                    )

                                except Exception as err:
                                    self.logger.error(
                                        "Image check error: {}".format(err)
                                    )

                            if (
                                self.do_comment
                                and user_name not in self.dont_include
                                and checked_img
                                and commenting
                            ):

                                if self.delimit_commenting:
                                    (
                                        self.commenting_approved,
                                        disapproval_reason,
                                    ) = verify_commenting(
                                        self.browser,
                                        self.max_comments,
                                        self.min_comments,
                                        self.comments_mandatory_words,
                                        self.logger,
                                    )
                                if self.commenting_approved:
                                    # smart commenting
                                    comments = self.fetch_smart_comments(
                                        is_video, temp_comments
                                    )
                                    if comments:
                                        comment_state, msg = comment_image(
                                            self.browser,
                                            user_name,
                                            comments,
                                            self.blacklist,
                                            self.logger,
                                            self.logfolder,
                                        )
                                        if comment_state is True:
                                            commented += 1

                                else:
                                    self.logger.info(disapproval_reason)

                            else:
                                self.logger.info("--> Not commented")
                                sleep(1)

                        elif msg == "already liked":
                            already_liked += 1

                        elif msg == "block on likes":
                            break

                        elif msg == "jumped":
                            # will break the loop after certain consecutive
                            # jumps
                            self.jumps["consequent"]["likes"] += 1

                    else:
                        self.logger.info(
                            "--> Image not liked: {}".format(reason.encode("utf-8"))
                        )
                        inap_img += 1

                except NoSuchElementException as err:
                    self.logger.error("Invalid Page: {}".format(err))

            if liked_img < amount:
                self.logger.info("-------------")
                self.logger.info(
                    "--> Given amount not fullfilled, " "image pool reached its end\n"
                )

        self.logger.info("User: {}".format(username.encode("utf-8")))
        self.logger.info("Liked: {}".format(total_liked_img))
        self.logger.info("Already Liked: {}".format(already_liked))
        self.logger.info("Commented: {}".format(commented))
        self.logger.info("Inappropriate: {}".format(inap_img))
        self.logger.info("Not valid users: {}\n".format(not_valid_users))

        self.liked_img += liked_img
        self.already_liked += already_liked
        self.commented += commented
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return self

    def interact_by_users(
        self,
        usernames: list,
        amount: int = 10,
        randomize: bool = False,
        media: str = None,
    ):
        """Likes some amounts of images for each usernames"""
        if self.aborting:
            return self

        message = "Starting to interact by users.."
        highlight_print(self.username, message, "feature", "info", self.logger)

        if not isinstance(usernames, list):
            usernames = [usernames]

        # standalone means this feature is started by the user
        standalone = (
            True if "interact_by_users" not in self.internal_usage.keys() else False
        )
        # skip validation in case of it is already accomplished
        users_validated = (
            True
            if not standalone
            and not self.internal_usage["interact_by_users"]["validate"]
            else False
        )

        total_liked_img = 0
        already_liked = 0
        inap_img = 0
        commented = 0
        followed = 0
        already_followed = 0
        not_valid_users = 0

        self.quotient_breach = False

        for index, username in enumerate(usernames):
            if self.quotient_breach:
                # keep `quotient_breach` active to break the internal
                # iterators of the caller
                self.quotient_breach = True if not standalone else False
                break

            self.logger.info("Username [{}/{}]".format(index + 1, len(usernames)))
            self.logger.info("--> {}".format(username.encode("utf-8")))

            if not users_validated:
                validation, details = self.validate_user_call(username)
                if not validation:
                    self.logger.info("--> not a valid user: {}".format(details))
                    not_valid_users += 1
                    continue

            track = "profile"
            # decision making
            # static conditions
            not_dont_include = username not in self.dont_include
            follow_restricted = follow_restriction(
                "read", username, self.follow_times, self.logger
            )
            counter = 0
            while True:
                following = (
                    random.randint(0, 100) <= self.follow_percentage
                    and self.do_follow
                    and not_dont_include
                    and not follow_restricted
                )
                commenting = (
                    random.randint(0, 100) <= self.comment_percentage
                    and self.do_comment
                    and not_dont_include
                )
                liking = random.randint(0, 100) <= self.like_percentage

                story = (
                    random.randint(0, 100) <= self.story_percentage and self.do_story
                )

                counter += 1

                # if we have only one image to like/comment
                if commenting and not liking and amount == 1:
                    continue

                if following or commenting or liking or story:
                    self.logger.info(
                        "username actions: following={} commenting={} "
                        "liking={} story={}".format(
                            following, commenting, liking, story
                        )
                    )
                    break

                # if for some reason we have no actions on this user
                if counter > 5:
                    self.logger.info(
                        "username={} could not get interacted".format(username)
                    )
                    break

            try:
                links = get_links_for_username(
                    self.browser,
                    self.username,
                    username,
                    amount,
                    self.logger,
                    self.logfolder,
                    randomize,
                    media,
                )
            except NoSuchElementException:
                self.logger.error("Element not found, skipping this username")
                continue

            if links is False:
                continue

            # Reset like counter for every username
            liked_img = 0

            for i, link in enumerate(links[:amount]):
                if self.jumps["consequent"]["likes"] >= self.jumps["limit"]["likes"]:
                    self.logger.warning(
                        "--> Like quotient reached its peak!\t~leaving "
                        "Interact-By-Users activity\n"
                    )
                    self.quotient_breach = True
                    # reset jump counter after a breach report
                    self.jumps["consequent"]["likes"] = 0
                    break

                # Check if target has reached
                if liked_img >= amount:
                    self.logger.info("-------------")
                    self.logger.info(
                        "--> Total liked image reached it's "
                        "amount given: {}".format(liked_img)
                    )
                    break

                self.logger.info("Post [{}/{}]".format(i + 1, len(links[:amount])))
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason, scope = check_link(
                        self.browser,
                        link,
                        self.dont_like,
                        self.mandatory_words,
                        self.mandatory_language,
                        self.is_mandatory_character,
                        self.mandatory_character,
                        self.check_character_set,
                        self.ignore_if_contains,
                        self.logger,
                    )
                    track = "post"

                    if not inappropriate:
                        # after first image we roll again
                        if i > 0:
                            liking = random.randint(0, 100) <= self.like_percentage
                            commenting = (
                                random.randint(0, 100) <= self.comment_percentage
                                and self.do_comment
                                and not_dont_include
                            )
                            story = (
                                random.randint(0, 100) <= self.story_percentage
                                and self.do_story
                            )

                        # like
                        if self.do_like and liking and self.delimit_liking:
                            self.liking_approved = verify_liking(
                                self.browser,
                                self.max_likes,
                                self.min_likes,
                                self.logger,
                            )

                        if self.do_like and liking and self.liking_approved:
                            like_state, msg = like_image(
                                self.browser,
                                user_name,
                                self.blacklist,
                                self.logger,
                                self.logfolder,
                                total_liked_img,
                            )
                            if like_state is True:
                                total_liked_img += 1
                                liked_img += 1
                                # reset jump counter after a successful like
                                self.jumps["consequent"]["likes"] = 0

                                # comment
                                checked_img = True
                                temp_comments = []

                                if self.use_clarifai and commenting:
                                    try:
                                        checked_img, temp_comments, clarifai_tags = (
                                            self.query_clarifai()
                                        )

                                    except Exception as err:
                                        self.logger.error(
                                            "Image check error: {}".format(err)
                                        )

                                if commenting and checked_img:

                                    if self.delimit_commenting:
                                        (
                                            self.commenting_approved,
                                            disapproval_reason,
                                        ) = verify_commenting(
                                            self.browser,
                                            self.max_comments,
                                            self.min_comments,
                                            self.comments_mandatory_words,
                                            self.logger,
                                        )
                                    if self.commenting_approved:
                                        # smart commenting
                                        comments = self.fetch_smart_comments(
                                            is_video, temp_comments
                                        )
                                        if comments:
                                            comment_state, msg = comment_image(
                                                self.browser,
                                                user_name,
                                                comments,
                                                self.blacklist,
                                                self.logger,
                                                self.logfolder,
                                            )
                                            if comment_state is True:
                                                commented += 1

                                    else:
                                        self.logger.info(disapproval_reason)

                                else:
                                    self.logger.info("--> Not commented")
                                    sleep(1)

                            elif msg == "already liked":
                                already_liked += 1

                            elif msg == "block on likes":
                                break

                            elif msg == "jumped":
                                # will break the loop after certain
                                # consecutive jumps
                                self.jumps["consequent"]["likes"] += 1

                    else:
                        self.logger.info(
                            "--> Image not liked: {}".format(reason.encode("utf-8"))
                        )
                        inap_img += 1

                except NoSuchElementException as err:
                    self.logger.info("Invalid Page: {}".format(err))

            # follow
            if following and not (self.dont_follow_inap_post and inap_img > 0):

                follow_state, msg = follow_user(
                    self.browser,
                    track,
                    self.username,
                    username,
                    None,
                    self.blacklist,
                    self.logger,
                    self.logfolder,
                )

                if follow_state is True:
                    followed += 1

                elif msg == "already followed":
                    already_followed += 1

            else:
                self.logger.info("--> Not following")
                sleep(1)

            # watch story if present
            if story:
                self.story_by_users([username])

            if liked_img < amount:
                self.logger.info("-------------")
                self.logger.info(
                    "--> Given amount not fullfilled, image pool " "reached its end\n"
                )

        if len(usernames) > 1:
            # final words
            interacted_media_size = len(usernames) * amount - inap_img
            self.logger.info(
                "Finished interacting on total of {} images from {} users! xD\n".format(
                    interacted_media_size, len(usernames)
                )
            )

            # print results
            self.logger.info("Liked: {}".format(total_liked_img))
            self.logger.info("Already Liked: {}".format(already_liked))
            self.logger.info("Commented: {}".format(commented))
            self.logger.info("Followed: {}".format(followed))
            self.logger.info("Already Followed: {}".format(already_followed))
            self.logger.info("Inappropriate: {}".format(inap_img))
            self.logger.info("Not valid users: {}\n".format(not_valid_users))

        self.liked_img += total_liked_img
        self.already_liked += already_liked
        self.commented += commented
        self.followed += followed
        self.already_followed += already_followed
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return self

    def interact_by_users_tagged_posts(
        self,
        usernames: list,
        amount: int = 10,
        randomize: bool = False,
        media: str = None,
    ):
        """Likes some amounts of tagged images for each usernames"""
        if self.aborting:
            return self

        if not isinstance(usernames, list):
            usernames = [usernames]

        # standalone means this feature is started by the user
        standalone = (
            True if "interact_by_users" not in self.internal_usage.keys() else False
        )
        # skip validation in case of it is already accomplished
        users_validated = (
            True
            if not standalone
            and not self.internal_usage["interact_by_users"]["validate"]
            else False
        )

        total_liked_img = 0
        already_liked = 0
        inap_img = 0
        commented = 0
        followed = 0
        already_followed = 0
        not_valid_users = 0

        self.quotient_breach = False

        for index, username in enumerate(usernames):
            if self.quotient_breach:
                # keep `quotient_breach` active to break the internal
                # iterators of the caller
                self.quotient_breach = True if not standalone else False
                break

            self.logger.info("Username [{}/{}]".format(index + 1, len(usernames)))
            self.logger.info("--> {}".format(username.encode("utf-8")))

            if not users_validated and username != self.username:
                validation, details = self.validate_user_call(username)
                if not validation:
                    self.logger.info("--> not a valid user: {}".format(details))
                    not_valid_users += 1
                    continue

            # decision making
            # static conditions
            not_dont_include = username not in self.dont_include
            follow_restricted = follow_restriction(
                "read", username, self.follow_times, self.logger
            )
            counter = 0
            while True:
                following = (
                    random.randint(0, 100) <= self.follow_percentage
                    and self.do_follow
                    and not_dont_include
                    and not follow_restricted
                )
                commenting = (
                    random.randint(0, 100) <= self.comment_percentage
                    and self.do_comment
                    and not_dont_include
                )
                liking = random.randint(0, 100) <= self.like_percentage

                counter += 1

                # if we have only one image to like/comment
                if commenting and not liking and amount == 1:
                    continue
                if following or commenting or liking:
                    self.logger.info(
                        "username actions: following={} commenting={} "
                        "liking={}".format(following, commenting, liking)
                    )
                    break
                # if for some reason we have no actions on this user
                if counter > 5:
                    self.logger.info(
                        "username={} could not get interacted".format(username)
                    )
                    break

            try:
                links = get_links_for_username(
                    self.browser,
                    self.username,
                    username,
                    amount,
                    self.logger,
                    self.logfolder,
                    randomize,
                    media,
                    taggedImages=True,
                )
            except NoSuchElementException:
                self.logger.error("Element not found, skipping this username")
                continue

            if links is False:
                continue

            # Reset like counter for every username
            liked_img = 0

            for i, link in enumerate(links[:amount]):
                if self.jumps["consequent"]["likes"] >= self.jumps["limit"]["likes"]:
                    self.logger.warning(
                        "--> Like quotient reached its peak!\t~leaving "
                        "Interact-By-Users activity\n"
                    )
                    self.quotient_breach = True
                    # reset jump counter after a breach report
                    self.jumps["consequent"]["likes"] = 0
                    break

                # Check if target has reached
                if liked_img >= amount:
                    self.logger.info("-------------")
                    self.logger.info(
                        "--> Total liked image reached it's "
                        "amount given: {}".format(liked_img)
                    )
                    break

                self.logger.info(
                    "Post [{}/{}]".format(liked_img + 1, len(links[:amount]))
                )
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason, scope = check_link(
                        self.browser,
                        link,
                        self.dont_like,
                        self.mandatory_words,
                        self.mandatory_language,
                        self.is_mandatory_character,
                        self.mandatory_character,
                        self.check_character_set,
                        self.ignore_if_contains,
                        self.logger,
                    )

                    if not inappropriate:
                        # after first image we roll again
                        if i > 0:
                            liking = random.randint(0, 100) <= self.like_percentage
                            commenting = (
                                random.randint(0, 100) <= self.comment_percentage
                                and self.do_comment
                                and not_dont_include
                            )

                        # like
                        if self.do_like and liking and self.delimit_liking:
                            self.liking_approved = verify_liking(
                                self.browser,
                                self.max_likes,
                                self.min_likes,
                                self.logger,
                            )

                        if self.do_like and liking and self.liking_approved:
                            like_state, msg = like_image(
                                self.browser,
                                user_name,
                                self.blacklist,
                                self.logger,
                                self.logfolder,
                                total_liked_img,
                            )
                            if like_state is True:
                                total_liked_img += 1
                                liked_img += 1
                                # reset jump counter after a successful like
                                self.jumps["consequent"]["likes"] = 0

                                # comment
                                checked_img = True
                                temp_comments = []

                                if self.use_clarifai and commenting:
                                    try:
                                        (
                                            checked_img,
                                            temp_comments,
                                            clarifai_tags,
                                        ) = self.query_clarifai()
                                    except Exception as err:
                                        self.logger.error(
                                            "Image check error: {}".format(err)
                                        )

                                if commenting and checked_img:

                                    if self.delimit_commenting:
                                        (
                                            self.commenting_approved,
                                            disapproval_reason,
                                        ) = verify_commenting(
                                            self.browser,
                                            self.max_comments,
                                            self.min_comments,
                                            self.comments_mandatory_words,
                                            self.logger,
                                        )
                                    if self.commenting_approved:
                                        if temp_comments:
                                            # use clarifai related comments
                                            # only!
                                            comments = temp_comments

                                        elif is_video:
                                            comments = (
                                                self.comments + self.video_comments
                                            )

                                        else:
                                            comments = (
                                                self.comments + self.photo_comments
                                            )

                                        comment_state, msg = comment_image(
                                            self.browser,
                                            user_name,
                                            comments,
                                            self.blacklist,
                                            self.logger,
                                            self.logfolder,
                                        )
                                        if comment_state is True:
                                            commented += 1

                                    else:
                                        self.logger.info(disapproval_reason)

                                else:
                                    self.logger.info("--> Not commented")
                                    sleep(1)

                            elif msg == "already liked":
                                already_liked += 1

                            elif msg == "block on likes":
                                break

                            elif msg == "jumped":
                                # will break the loop after certain
                                # consecutive jumps
                                self.jumps["consequent"]["likes"] += 1

                    else:
                        self.logger.info(
                            "--> Image not liked: {}".format(reason.encode("utf-8"))
                        )
                        inap_img += 1

                except NoSuchElementException as err:
                    self.logger.info("Invalid Page: {}".format(err))

            # follow
            if following and not (self.dont_follow_inap_post and inap_img > 0):

                follow_state, msg = follow_user(
                    self.browser,
                    "profile",
                    self.username,
                    username,
                    None,
                    self.blacklist,
                    self.logger,
                    self.logfolder,
                )
                if follow_state is True:
                    followed += 1

                elif msg == "already followed":
                    already_followed += 1

            else:
                self.logger.info("--> Not following")
                sleep(1)

            if liked_img < amount:
                self.logger.info("-------------")
                self.logger.info(
                    "--> Given amount not fullfilled, image pool " "reached its end\n"
                )

        # final words
        interacted_media_size = len(usernames) * amount - inap_img
        self.logger.info(
            "Finished interacting on total of {} images from {} users! xD\n".format(
                interacted_media_size, len(usernames)
            )
        )

        # print results
        self.logger.info("Liked: {}".format(total_liked_img))
        self.logger.info("Already Liked: {}".format(already_liked))
        self.logger.info("Commented: {}".format(commented))
        self.logger.info("Followed: {}".format(followed))
        self.logger.info("Already Followed: {}".format(already_followed))
        self.logger.info("Inappropriate: {}".format(inap_img))
        self.logger.info("Not valid users: {}\n".format(not_valid_users))

        self.liked_img += total_liked_img
        self.already_liked += already_liked
        self.commented += commented
        self.followed += followed
        self.already_followed += already_followed
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return self

    def like_from_image(self, url: str, amount: int = 50, media: str = None):
        """Gets the tags from an image and likes 50 images for each tag"""
        if self.aborting:
            return self

        try:
            if not url:
                urls = self.browser.find_elements_by_xpath(
                    read_xpath(self.__class__.__name__, "main_article")
                )
                url = urls[0].get_attribute("href")
                self.logger.info("new url {}".format(url))
            tags = get_tags(self.browser, url)
            self.logger.info(tags)
            self.like_by_tags(tags, amount, media)
        except TypeError as err:
            self.logger.error("Sorry, an error occurred: {}".format(err))
            self.aborting = True
            return self

        return self

    def interact_user_followers(
        self, usernames: list, amount: int = 10, randomize: bool = False
    ):
        """
        Interact with the people that a given user is followed by.

        set_do_comment, set_do_follow and set_do_like are applicable.

        :param usernames: List of users to interact with their followers.
        :param amount: Amount of followers to interact with.
        :param randomize: If followers should be chosen randomly.
        """

        if self.aborting:
            return self

        if self.do_follow is not True and self.do_like is not True:
            self.logger.info(
                "Please enable following or liking in settings in order to "
                "do interactions."
            )
            return self

        elif self.user_interact_amount <= 0:
            self.logger.info(
                "Please choose an amount higher than zero in "
                "`set_user_interact` in order to do interactions."
            )
            return self

        if not isinstance(usernames, list):
            usernames = [usernames]

        interacted_all = 0
        not_valid_users = 0
        simulated_unfollow = 0

        # hold the current global values for differentiating at the end
        liked_init = self.liked_img
        already_liked_init = self.already_liked
        commented_init = self.commented
        followed_init = self.followed
        inap_img_init = self.inap_img

        self.quotient_breach = False

        for index, user in enumerate(usernames):
            if self.quotient_breach:
                break

            self.logger.info(
                "User '{}' [{}/{}]".format((user), index + 1, len(usernames))
            )
            try:
                person_list, simulated_list = get_given_user_followers(
                    self.browser,
                    self.username,
                    user,
                    amount,
                    self.dont_include,
                    randomize,
                    self.blacklist,
                    self.follow_times,
                    self.simulation,
                    self.jumps,
                    self.logger,
                    self.logfolder,
                )

            except (TypeError, RuntimeWarning) as err:
                if isinstance(err, RuntimeWarning):
                    self.logger.warning(
                        "Warning: {} , skipping to next user".format(err)
                    )
                    continue

                else:
                    self.logger.error("Sorry, an error occurred: {}".format(err))
                    self.aborting = True
                    return self

            print("")
            self.logger.info(
                "Grabbed {} usernames from '{}'s `Followers` to do "
                "interaction.".format(len(person_list), user)
            )

            interacted_personal = 0

            for index, person in enumerate(person_list):
                if self.quotient_breach:
                    self.logger.warning(
                        "--> Like quotient reached its peak!"
                        "\t~leaving Interact-User-Followers activity\n"
                    )
                    break

                self.logger.info(
                    "User '{}' [{}/{}]".format((person), index + 1, len(person_list))
                )

                validation, details = self.validate_user_call(person)
                if not validation:
                    self.logger.info(details)
                    not_valid_users += 1

                    if person in simulated_list:
                        self.logger.warning(
                            "--> Simulated Unfollow {}:"
                            " unfollowing '{}' due to mismatching "
                            "validation...".format(simulated_unfollow + 1, person)
                        )
                        unfollow_state, msg = unfollow_user(
                            self.browser,
                            "profile",
                            self.username,
                            person,
                            None,
                            None,
                            self.relationship_data,
                            self.logger,
                            self.logfolder,
                        )
                        if unfollow_state:
                            simulated_unfollow += 1

                    continue

                # Do interactions if any
                do_interact = random.randint(0, 100) <= self.user_interact_percentage

                if not do_interact:
                    self.logger.info(
                        "Skipping user '{}' due to the interaction "
                        "percentage of {}".format(person, self.user_interact_percentage)
                    )
                    continue

                else:
                    interacted_all += 1
                    interacted_personal += 1

                    self.logger.info(
                        "Interaction [{}/{}]  |  Total Interaction: {}".format(
                            interacted_personal, len(person_list), interacted_all
                        )
                    )

                    with self.feature_in_feature("interact_by_users", False):
                        self.interact_by_users(
                            person,
                            self.user_interact_amount,
                            self.user_interact_random,
                            self.user_interact_media,
                        )
                    if self.aborting:
                        return self
                    sleep(1)

        # final words
        self.logger.info(
            "Finished interacting {} people from {} users' `Followers`! xD\n".format(
                interacted_all, len(usernames)
            )
        )

        # find the feature-wide action sizes by taking a difference
        liked = self.liked_img - liked_init
        already_liked = self.already_liked - already_liked_init
        commented = self.commented - commented_init
        followed = self.followed - followed_init
        inap_img = self.inap_img - inap_img_init

        # print results
        self.logger.info("Liked: {}".format(liked))
        self.logger.info("Already Liked: {}".format(already_liked))
        self.logger.info("Commented: {}".format(commented))
        self.logger.info("Followed: {}".format(followed))
        self.logger.info("Inappropriate: {}".format(inap_img))
        self.logger.info("Not valid users: {}\n".format(not_valid_users))

        self.not_valid_users += not_valid_users

        return self

    def interact_user_following(
        self, usernames: list, amount: int = 10, randomize: bool = False
    ):

        if self.aborting:
            return self

        if self.do_follow is not True and self.do_like is not True:
            self.logger.info(
                "Please enable following or liking in settings"
                " in order to do interactions."
            )
            return self

        elif self.user_interact_amount <= 0:
            self.logger.info(
                "Please choose an amount higher than zero in"
                " `set_user_interact` in order to do interactions."
            )
            return self

        if not isinstance(usernames, list):
            usernames = [usernames]

        interacted_all = 0
        not_valid_users = 0
        simulated_unfollow = 0

        # hold the current global values for differentiating at the end
        liked_init = self.liked_img
        already_liked_init = self.already_liked
        commented_init = self.commented
        followed_init = self.followed
        inap_img_init = self.inap_img

        self.quotient_breach = False

        for index, user in enumerate(usernames):
            if self.quotient_breach:
                break

            self.logger.info(
                "User '{}' [{}/{}]".format((user), index + 1, len(usernames))
            )
            try:
                person_list, simulated_list = get_given_user_following(
                    self.browser,
                    self.username,
                    user,
                    amount,
                    self.dont_include,
                    randomize,
                    self.blacklist,
                    self.follow_times,
                    self.simulation,
                    self.jumps,
                    self.logger,
                    self.logfolder,
                )

            except (TypeError, RuntimeWarning) as err:
                if isinstance(err, RuntimeWarning):
                    self.logger.warning(
                        "Warning: {} , skipping to next user".format(err)
                    )
                    continue

                else:
                    self.logger.error("Sorry, an error occurred: {}".format(err))
                    self.aborting = True
                    return self

            print("")
            self.logger.info(
                "Grabbed {} usernames from '{}'s `Following` to do "
                "interaction.".format(len(person_list), user)
            )
            interacted_personal = 0

            for index, person in enumerate(person_list):
                if self.quotient_breach:
                    self.logger.warning(
                        "--> Like quotient reached its peak!"
                        "\t~leaving Interact-User-Following activity\n"
                    )
                    break

                self.logger.info(
                    "User '{}' [{}/{}]".format((person), index + 1, len(person_list))
                )

                validation, details = self.validate_user_call(person)
                if validation is not True:
                    self.logger.info(details)
                    not_valid_users += 1

                    if person in simulated_list:
                        self.logger.warning(
                            "--> Simulated Unfollow {}:"
                            " unfollowing '{}' due to mismatching "
                            "validation...".format(simulated_unfollow + 1, person)
                        )

                        unfollow_state, msg = unfollow_user(
                            self.browser,
                            "profile",
                            self.username,
                            person,
                            None,
                            None,
                            self.relationship_data,
                            self.logger,
                            self.logfolder,
                        )
                        if unfollow_state is True:
                            simulated_unfollow += 1

                    continue

                # Do interactions if any
                do_interact = random.randint(0, 100) <= self.user_interact_percentage

                if do_interact is False:
                    self.logger.info(
                        "Skipping user '{}' due to"
                        " the interaction percentage of {}".format(
                            person, self.user_interact_percentage
                        )
                    )
                    continue

                else:
                    interacted_all += 1
                    interacted_personal += 1

                    self.logger.info(
                        "Interaction [{}/{}]  |  Total Interaction: {}".format(
                            interacted_personal, len(person_list), interacted_all
                        )
                    )

                    with self.feature_in_feature("interact_by_users", False):
                        self.interact_by_users(
                            person,
                            self.user_interact_amount,
                            self.user_interact_random,
                            self.user_interact_media,
                        )
                    if self.aborting:
                        return self
                    sleep(1)

        # final words
        self.logger.info(
            "Finished interacting {} people"
            " from {} users' `Following`! xD\n".format(interacted_all, len(usernames))
        )

        # find the feature-wide action sizes by taking a difference
        liked = self.liked_img - liked_init
        already_liked = self.already_liked - already_liked_init
        commented = self.commented - commented_init
        followed = self.followed - followed_init
        inap_img = self.inap_img - inap_img_init

        # print results
        self.logger.info("Liked: {}".format(liked))
        self.logger.info("Already Liked: {}".format(already_liked))
        self.logger.info("Commented: {}".format(commented))
        self.logger.info("Followed: {}".format(followed))
        self.logger.info("Inappropriate: {}".format(inap_img))
        self.logger.info("Not valid users: {}\n".format(not_valid_users))

        self.not_valid_users += not_valid_users

        return self

    def follow_user_followers(
        self,
        usernames: list,
        amount: int = 10,
        randomize: bool = False,
        interact: bool = False,
        sleep_delay: int = 600,
    ):
        """ Follow the `Followers` of given users """
        if self.aborting:
            return self

        message = "Starting to follow user `Followers`.."
        highlight_print(self.username, message, "feature", "info", self.logger)

        if not isinstance(usernames, list):
            usernames = [usernames]

        followed_all = 0
        followed_new = 0
        not_valid_users = 0

        # below, you can use some static value `10` instead of random ones..
        relax_point = random.randint(7, 14)

        # hold the current global values for differentiating at the end
        already_followed_init = self.already_followed
        liked_init = self.liked_img
        already_liked_init = self.already_liked
        commented_init = self.commented
        inap_img_init = self.inap_img

        self.quotient_breach = False

        for index, user in enumerate(usernames):
            if self.quotient_breach:
                break

            self.logger.info(
                "User '{}' [{}/{}]".format((user), index + 1, len(usernames))
            )

            try:
                person_list, simulated_list = get_given_user_followers(
                    self.browser,
                    self.username,
                    user,
                    amount,
                    self.dont_include,
                    randomize,
                    self.blacklist,
                    self.follow_times,
                    self.simulation,
                    self.jumps,
                    self.logger,
                    self.logfolder,
                )

            except (TypeError, RuntimeWarning) as err:
                if isinstance(err, RuntimeWarning):
                    self.logger.warning(
                        "Warning: {} , skipping to next user".format(err)
                    )
                    continue

                else:
                    self.logger.error("Sorry, an error occurred: {}".format(err))
                    self.aborting = True
                    return self

            print("")
            self.logger.info(
                "Grabbed {} usernames from '{}'s `Followers` to do following\n".format(
                    len(person_list), user
                )
            )

            followed_personal = 0
            simulated_unfollow = 0

            for index, person in enumerate(person_list):
                if self.quotient_breach:
                    self.logger.warning(
                        "--> Follow quotient reached its peak!"
                        "\t~leaving Follow-User-Followers activity\n"
                    )
                    break

                self.logger.info(
                    "Ongoing Follow [{}/{}]: now following '{}'...".format(
                        index + 1, len(person_list), person
                    )
                )

                validation, details = self.validate_user_call(person)
                if validation is not True:
                    self.logger.info(details)
                    not_valid_users += 1

                    if person in simulated_list:
                        self.logger.warning(
                            "--> Simulated Unfollow {}: unfollowing"
                            " '{}' due to mismatching validation...\n".format(
                                simulated_unfollow + 1, person
                            )
                        )

                        unfollow_state, msg = unfollow_user(
                            self.browser,
                            "profile",
                            self.username,
                            person,
                            None,
                            None,
                            self.relationship_data,
                            self.logger,
                            self.logfolder,
                        )
                        if unfollow_state is True:
                            simulated_unfollow += 1
                    # skip this [non-validated] user
                    continue

                # go ahead and follow, then interact (if any)
                with self.feature_in_feature("follow_by_list", False):
                    followed = self.follow_by_list(
                        person, self.follow_times, sleep_delay, interact
                    )
                sleep(1)

                if followed > 0:
                    followed_all += 1
                    followed_new += 1
                    followed_personal += 1

                self.logger.info(
                    "Follow per user: {}  |  Total Follow: {}\n".format(
                        followed_personal, followed_all
                    )
                )

                # take a break after a good following
                if followed_new >= relax_point:
                    delay_random = random.randint(
                        ceil(sleep_delay * 0.85), ceil(sleep_delay * 1.14)
                    )
                    sleep_time = (
                        "{} seconds".format(delay_random)
                        if delay_random < 60
                        else "{} minutes".format(truncate_float(delay_random / 60, 2))
                    )
                    self.logger.info(
                        "------=>  Followed {} new users ~sleeping about {}\n".format(
                            followed_new, sleep_time
                        )
                    )
                    sleep(delay_random)
                    relax_point = random.randint(7, 14)
                    followed_new = 0

        # final words
        self.logger.info(
            "Finished following {} users' `Followers`! xD\n".format(len(usernames))
        )
        # find the feature-wide action sizes by taking a difference
        already_followed = self.already_followed - already_followed_init
        inap_img = self.inap_img - inap_img_init
        liked = self.liked_img - liked_init
        already_liked = self.already_liked - already_liked_init
        commented = self.commented - commented_init

        # print results
        self.logger.info("Followed: {}".format(followed_all))
        self.logger.info("Already followed: {}".format(already_followed))
        self.logger.info("Not valid users: {}".format(not_valid_users))

        if interact is True:
            print("")
            # print results out of interactions
            self.logger.info("Liked: {}".format(liked))
            self.logger.info("Already Liked: {}".format(already_liked))
            self.logger.info("Commented: {}".format(commented))
            self.logger.info("Inappropriate: {}".format(inap_img))

        self.not_valid_users += not_valid_users

        return self

    def follow_user_following(
        self,
        usernames: list,
        amount: int = 10,
        randomize: bool = False,
        interact: bool = False,
        sleep_delay: int = 600,
    ):
        """ Follow the `Following` of given users """
        if self.aborting:
            return self

        message = "Starting to follow user `Following`.."
        highlight_print(self.username, message, "feature", "info", self.logger)

        if not isinstance(usernames, list):
            usernames = [usernames]

        followed_all = 0
        followed_new = 0
        not_valid_users = 0

        # hold the current global values for differentiating at the end
        already_followed_init = self.already_followed
        liked_init = self.liked_img
        already_liked_init = self.already_liked
        commented_init = self.commented
        inap_img_init = self.inap_img

        # below, can use a static value instead of from random range..
        relax_point = random.randint(7, 14)
        self.quotient_breach = False

        for index, user in enumerate(usernames):
            if self.quotient_breach:
                break

            self.logger.info(
                "User '{}' [{}/{}]".format((user), index + 1, len(usernames))
            )
            try:
                person_list, simulated_list = get_given_user_following(
                    self.browser,
                    self.username,
                    user,
                    amount,
                    self.dont_include,
                    randomize,
                    self.blacklist,
                    self.follow_times,
                    self.simulation,
                    self.jumps,
                    self.logger,
                    self.logfolder,
                )

            except (TypeError, RuntimeWarning) as err:
                if isinstance(err, RuntimeWarning):
                    self.logger.warning(
                        "Warning: {} , skipping to next user".format(err)
                    )
                    continue

                else:
                    self.logger.error("Sorry, an error occurred: {}".format(err))
                    self.aborting = True
                    return self

            print("")
            self.logger.info(
                "Grabbed {} usernames from '{}'s `Following` to do following\n".format(
                    len(person_list), user
                )
            )

            followed_personal = 0
            simulated_unfollow = 0

            for index, person in enumerate(person_list):
                if self.quotient_breach:
                    self.logger.warning(
                        "--> Follow quotient reached its peak!"
                        "\t~leaving Follow-User-Following activity\n"
                    )
                    break

                self.logger.info(
                    "Ongoing Follow [{}/{}]: now following '{}'...".format(
                        index + 1, len(person_list), person
                    )
                )

                validation, details = self.validate_user_call(person)
                if validation is not True:
                    self.logger.info(details)
                    not_valid_users += 1

                    if person in simulated_list:
                        self.logger.warning(
                            "--> Simulated Unfollow {}:"
                            " unfollowing '{}' due to mismatching "
                            "validation...\n".format(simulated_unfollow + 1, person)
                        )

                        unfollow_state, msg = unfollow_user(
                            self.browser,
                            "profile",
                            self.username,
                            person,
                            None,
                            None,
                            self.relationship_data,
                            self.logger,
                            self.logfolder,
                        )
                        if unfollow_state is True:
                            simulated_unfollow += 1
                    # skip the [non-validated] user
                    continue

                # go ahead and follow, then interact (if any)
                with self.feature_in_feature("follow_by_list", False):
                    followed = self.follow_by_list(
                        person, self.follow_times, sleep_delay, interact
                    )
                sleep(1)

                if followed > 0:
                    followed_all += 1
                    followed_new += 1
                    followed_personal += 1

                self.logger.info(
                    "Follow per user: {}  |  Total Follow: {}\n".format(
                        followed_personal, followed_all
                    )
                )

                # take a break after a good following
                if followed_new >= relax_point:
                    delay_random = random.randint(
                        ceil(sleep_delay * 0.85), ceil(sleep_delay * 1.14)
                    )
                    sleep_time = (
                        "{} seconds".format(delay_random)
                        if delay_random < 60
                        else "{} minutes".format(truncate_float(delay_random / 60, 2))
                    )
                    self.logger.info(
                        "------=>  Followed {} new users ~sleeping about {}\n".format(
                            followed_new, sleep_time
                        )
                    )
                    sleep(delay_random)
                    relax_point = random.randint(7, 14)
                    followed_new = 0

        # final words
        self.logger.info(
            "Finished following {} users' `Following`! xD\n".format(len(usernames))
        )

        # find the feature-wide action sizes by taking a difference
        already_followed = self.already_followed - already_followed_init
        inap_img = self.inap_img - inap_img_init
        liked = self.liked_img - liked_init
        already_liked = self.already_liked - already_liked_init
        commented = self.commented - commented_init

        # print results
        self.logger.info("Followed: {}".format(followed_all))
        self.logger.info("Already followed: {}".format(already_followed))
        self.logger.info("Not valid users: {}".format(not_valid_users))

        if interact is True:
            print("")
            # print results out of interactions
            self.logger.info("Liked: {}".format(liked))
            self.logger.info("Already Liked: {}".format(already_liked))
            self.logger.info("Commented: {}".format(commented))
            self.logger.info("Inappropriate: {}".format(inap_img))

        self.not_valid_users += not_valid_users

        return self

    def unfollow_users(
        self,
        amount: int = 10,
        custom_list_enabled: bool = False,
        custom_list: list = [],
        custom_list_param: str = "all",
        instapy_followed_enabled: bool = False,
        instapy_followed_param: str = "all",
        nonFollowers: bool = False,
        allFollowing: bool = False,
        style: str = "FIFO",
        unfollow_after: int = None,
        delay_followbackers: int = 0,  # 864000 = 10 days, 0 = don't delay
        sleep_delay: int = 600,
    ):
        """Unfollows (default) 10 users from your following list"""

        if self.aborting:
            return self

        message = "Starting to unfollow users.."
        highlight_print(self.username, message, "feature", "info", self.logger)

        if unfollow_after is not None:
            if not python_version().startswith(("2.7", "3")):
                self.logger.warning(
                    "`unfollow_after` parameter is not"
                    " available for Python versions below 2.7"
                )
                unfollow_after = None

        self.automatedFollowedPool = set_automated_followed_pool(
            self.username,
            unfollow_after,
            self.logger,
            self.logfolder,
            delay_followbackers,
        )

        try:
            unfollowed = unfollow(
                self.browser,
                self.username,
                amount,
                (custom_list_enabled, custom_list, custom_list_param),
                (instapy_followed_enabled, instapy_followed_param),
                nonFollowers,
                allFollowing,
                style,
                self.automatedFollowedPool,
                self.relationship_data,
                self.dont_include,
                self.white_list,
                sleep_delay,
                self.jumps,
                delay_followbackers,
                self.logger,
                self.logfolder,
            )
            self.logger.info("--> Total people unfollowed : {}\n".format(unfollowed))
            self.unfollowed += unfollowed

        except Exception as exc:
            if isinstance(exc, RuntimeWarning):
                self.logger.warning("Warning: {} , stopping unfollow_users".format(exc))
                return self

            else:
                self.logger.error("Sorry, an error occurred: {}".format(exc))
                self.aborting = True
                return self

        return self

    def remove_follow_requests(self, amount: int = 200, sleep_delay: int = 600):
        """Remove user unaccepted follow requests"""

        if self.aborting:
            return self

        message = "Starting to get follow requests.."
        highlight_print(self.username, message, "feature", "info", self.logger)

        follow_requests = get_follow_requests(
            self.browser, amount, sleep_delay, self.logger, self.logfolder
        )

        unfollow_count = 0

        for person in follow_requests:
            self.logger.warning(
                "--> Unfollow {}/{}:"
                " Removing request for: '{}' ".format(
                    unfollow_count + 1, len(follow_requests), person
                )
            )

            unfollow_state, msg = unfollow_user(
                self.browser,
                "profile",
                self.username,
                person,
                None,
                None,
                self.relationship_data,
                self.logger,
                self.logfolder,
            )

            if unfollow_state is True:
                unfollow_count += 1
                self.unfollowed += 1

        return self

    def like_by_feed(self, **kwargs):
        """Like the users feed"""

        if self.aborting:
            return self

        for i in self.like_by_feed_generator(**kwargs):
            pass

        return self

    def like_by_feed_generator(
        self,
        amount: int = 50,
        randomize: bool = False,
        unfollow: bool = False,
        interact: bool = False,
    ):
        """Like the users feed"""

        if self.aborting:
            return

        liked_img = 0
        already_liked = 0
        inap_img = 0
        inap_unfollow = 0
        commented = 0
        followed = 0
        skipped_img = 0
        num_of_search = 0
        not_valid_users = 0
        link_not_found_loop_error = 0

        history = []
        self.quotient_breach = False

        while liked_img < amount:
            if self.quotient_breach:
                break

            try:
                # Gets another load of links to be tested
                links = get_links_from_feed(
                    self.browser, amount, num_of_search, self.logger
                )

                if len(links) > 0:
                    link_not_found_loop_error = 0

                if len(links) == 0:
                    link_not_found_loop_error += 1
                    if link_not_found_loop_error >= 10:
                        self.logger.warning(
                            "Loop error, 0 links"
                            " for 10 times consecutively, exit loop"
                        )
                        break

            except NoSuchElementException:
                self.logger.warning("Too few images, aborting")
                self.aborting = True
                return

            num_of_search += 1

            for i, link in enumerate(links):
                if liked_img == amount:
                    break

                if self.jumps["consequent"]["likes"] >= self.jumps["limit"]["likes"]:
                    self.logger.warning(
                        "--> Like quotient reached its peak!"
                        "\t~leaving Like-By-Feed activity\n"
                    )
                    self.quotient_breach = True
                    # reset jump counter after a breach report
                    self.jumps["consequent"]["likes"] = 0
                    break

                if randomize and random.choice([True, False]):
                    self.logger.warning("Post Randomly Skipped...\n")
                    skipped_img += 1
                    continue
                else:
                    if link in history:
                        self.logger.info(
                            "This link has already " "been visited: {}".format(link)
                        )
                        continue
                    else:
                        self.logger.info("New link found...")
                        history.append(link)
                        self.logger.info(
                            "[{} posts liked /{} amount]".format(liked_img, amount)
                        )
                        self.logger.info(link)

                        try:
                            (
                                inappropriate,
                                user_name,
                                is_video,
                                reason,
                                scope,
                            ) = check_link(
                                self.browser,
                                link,
                                self.dont_like,
                                self.mandatory_words,
                                self.mandatory_language,
                                self.is_mandatory_character,
                                self.mandatory_character,
                                self.check_character_set,
                                self.ignore_if_contains,
                                self.logger,
                            )

                            if not inappropriate and self.delimit_liking:
                                self.liking_approved = verify_liking(
                                    self.browser,
                                    self.max_likes,
                                    self.min_likes,
                                    self.logger,
                                )
                            if not inappropriate and self.liking_approved:
                                # validate user
                                validation, details = self.validate_user_call(user_name)
                                if validation is not True:
                                    self.logger.info(details)
                                    not_valid_users += 1
                                    continue
                                else:
                                    web_address_navigator(self.browser, link)

                                # try to like
                                like_state, msg = like_image(
                                    self.browser,
                                    user_name,
                                    self.blacklist,
                                    self.logger,
                                    self.logfolder,
                                    liked_img,
                                )

                                if like_state is True:
                                    liked_img += 1
                                    # reset jump counter after a successful
                                    # like
                                    self.jumps["consequent"]["likes"] = 0

                                    checked_img = True
                                    temp_comments = []

                                    commenting = (
                                        random.randint(0, 100)
                                        <= self.comment_percentage
                                    )
                                    following = (
                                        random.randint(0, 100) <= self.follow_percentage
                                    )

                                    if self.use_clarifai and (following or commenting):
                                        try:
                                            (
                                                checked_img,
                                                temp_comments,
                                                clarifai_tags,
                                            ) = self.query_clarifai()

                                        except Exception as err:
                                            self.logger.error(
                                                "Image check error:" " {}".format(err)
                                            )

                                    # commenting
                                    if (
                                        self.do_comment
                                        and user_name not in self.dont_include
                                        and checked_img
                                        and commenting
                                    ):
                                        if self.delimit_commenting:
                                            (
                                                self.commenting_approved,
                                                disapproval_reason,
                                            ) = verify_commenting(
                                                self.browser,
                                                self.max_comments,
                                                self.min_comments,
                                                self.comments_mandatory_words,
                                                self.logger,
                                            )

                                        if self.commenting_approved:
                                            # smart commenting
                                            comments = self.fetch_smart_comments(
                                                is_video, temp_comments
                                            )
                                            if comments:
                                                comment_state, msg = comment_image(
                                                    self.browser,
                                                    user_name,
                                                    comments,
                                                    self.blacklist,
                                                    self.logger,
                                                    self.logfolder,
                                                )
                                            if comment_state is True:
                                                commented += 1

                                        else:
                                            self.logger.info(disapproval_reason)

                                    else:
                                        self.logger.info("--> Not commented")
                                        sleep(1)

                                    # following
                                    if (
                                        self.do_follow
                                        and user_name not in self.dont_include
                                        and checked_img
                                        and following
                                        and not follow_restriction(
                                            "read",
                                            user_name,
                                            self.follow_times,
                                            self.logger,
                                        )
                                    ):
                                        follow_state, msg = follow_user(
                                            self.browser,
                                            "post",
                                            self.username,
                                            user_name,
                                            None,
                                            self.blacklist,
                                            self.logger,
                                            self.logfolder,
                                        )
                                        if follow_state is True:
                                            followed += 1
                                    else:
                                        self.logger.info("--> Not following")
                                        sleep(1)

                                    # interactions (if any)
                                    if interact:
                                        self.logger.info(
                                            "--> User gonna be interacted: "
                                            "'{}'".format(user_name)
                                        )

                                        self.like_by_users(
                                            user_name,
                                            self.user_interact_amount,
                                            self.user_interact_random,
                                            self.user_interact_media,
                                        )
                                    # :P
                                    yield self

                                elif msg == "already liked":
                                    already_liked += 1

                                elif msg == "block on likes":
                                    break

                                elif msg == "jumped":
                                    # will break the loop after
                                    # certain consecutive jumps
                                    self.jumps["consequent"]["likes"] += 1

                            elif inappropriate:
                                inap_img += 1
                                self.logger.info(
                                    "--> Image not liked: {}".format(
                                        reason.encode("utf-8")
                                    )
                                )

                                if "Inappropriate" in reason and unfollow:
                                    # example of unfollowing
                                    # directly from a post page (faster)
                                    self.logger.warning(
                                        "--> Ongoing Unfollow {}: unfollowing"
                                        " '{}' due to inappropriate content...".format(
                                            inap_unfollow + 1, user_name
                                        )
                                    )

                                    unfollow_state, msg = unfollow_user(
                                        self.browser,
                                        "post",
                                        self.username,
                                        user_name,
                                        None,
                                        None,
                                        self.relationship_data,
                                        self.logger,
                                        self.logfolder,
                                    )

                                    if unfollow_state is True:
                                        inap_unfollow += 1

                        except NoSuchElementException as err:
                            self.logger.error("Invalid Page: {}".format(err))

        self.logger.info("Liked: {}".format(liked_img))
        self.logger.info("Already Liked: {}".format(already_liked))
        self.logger.info("Commented: {}".format(commented))
        self.logger.info("Followed: {}".format(followed))
        self.logger.info("Inappropriate: {}".format(inap_img))
        self.logger.info("Not valid users: {}".format(not_valid_users))
        self.logger.info("Randomly Skipped: {}\n".format(skipped_img))

        self.liked_img += liked_img
        self.already_liked += already_liked
        self.commented += commented
        self.followed += followed
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return

    def set_dont_unfollow_active_users(
        self, enabled: bool = False, posts: int = 4, boundary: int = 500
    ):
        """Prevents unfollow followers who have liked one of
        your latest X posts"""

        if self.aborting:
            return

        # do nothing
        if not enabled:
            return

        # list of users who liked our media
        active_users = get_active_users(
            self.browser, self.username, posts, boundary, self.logger
        )

        # include active user to not unfollow list
        self.dont_include.update(active_users)

    def set_blacklist(self, enabled: bool, campaign: str):
        """
         Enable/disable blacklist. If enabled, adds users to a blacklist
        after interact with and adds users to dont_include list
        """

        if enabled is False:
            self.dont_include = self.white_list
            return

        self.blacklist["enabled"] = True
        self.blacklist["campaign"] = campaign

        try:
            with open("{}blacklist.csv".format(self.logfolder), "r") as blacklist:
                reader = csv.DictReader(blacklist)
                for row in reader:
                    if row["campaign"] == campaign:
                        self.dont_include.add(row["username"])
        # except:
        except Exception:
            self.logger.info("Campaign {} first run".format(campaign))

    def grab_followers(
        self,
        username: str = None,
        amount: int = None,
        live_match: bool = False,
        store_locally: bool = True,
    ):
        """
         Gets and returns `followers` information of given user
        in desired amount, also, saves locally
        """

        message = "Starting to get the `Followers` data.."
        highlight_print(self.username, message, "feature", "info", self.logger)

        if username is None:
            self.logger.warning(
                "Please provide a username to grab `Followers` data"
                "  ~e.g. your own username or somebody else's"
            )
            return self

        elif amount is None:
            self.logger.warning("Please put amount to grab `Followers` data")
            return self

        elif amount != "full" and (
            type(amount) != int or ((type(amount) == int and amount <= 0))
        ):
            self.logger.info(
                "Please provide a valid amount bigger than"
                " zero (0) to grab `Followers` data"
            )
            return self

        # Get `followers` data
        grabbed_followers = get_followers(
            self.browser,
            username,
            amount,
            self.relationship_data,
            live_match,
            store_locally,
            self.logger,
            self.logfolder,
        )
        return grabbed_followers

    def grab_following(
        self,
        username: str = None,
        amount: int = None,
        live_match: bool = False,
        store_locally: bool = True,
    ):
        """
         Gets and returns `following` information of given user
        in desired amount, also, saves locally
        """

        message = "Starting to get the `Following` data.."
        highlight_print(self.username, message, "feature", "info", self.logger)

        if username is None:
            self.logger.warning(
                "Please provide a username to grab `Following` data"
                "  ~e.g. your own username or somebody else's"
            )
            return self

        elif amount is None:
            self.logger.warning("Please put amount to grab `Following` data")
            return self

        elif amount != "full" and (
            type(amount) != int or ((type(amount) == int and amount <= 0))
        ):
            self.logger.info(
                "Please provide a valid amount bigger than"
                " zero (0) to grab `Following` data"
            )
            return self

        # get `following` data
        grabbed_following = get_following(
            self.browser,
            username,
            amount,
            self.relationship_data,
            live_match,
            store_locally,
            self.logger,
            self.logfolder,
        )
        return grabbed_following

    def pick_unfollowers(
        self,
        username: str = None,
        compare_by: str = "latest",
        compare_track: str = "first",
        live_match: bool = False,
        store_locally: bool = True,
        print_out: bool = True,
    ):
        """
         Compares the `followers` stored in a latest local
        copy against either lively generated data or previous
        local copy and returns absent followers
        """

        message = "Starting to pick Unfollowers of {}..".format(username)
        highlight_print(self.username, message, "feature", "info", self.logger)

        # get all and active Unfollowers
        all_unfollowers, active_unfollowers = get_unfollowers(
            self.browser,
            username,
            compare_by,
            compare_track,
            self.relationship_data,
            live_match,
            store_locally,
            print_out,
            self.logger,
            self.logfolder,
        )

        return all_unfollowers, active_unfollowers

    def pick_nonfollowers(
        self, username: str = None, live_match: bool = False, store_locally: bool = True
    ):
        """ Returns Nonfollowers data of a given user """

        message = "Starting to pick Nonfollowers of {}..".format(username)
        highlight_print(self.username, message, "feature", "info", self.logger)

        # get Nonfollowers
        nonfollowers = get_nonfollowers(
            self.browser,
            username,
            self.relationship_data,
            live_match,
            store_locally,
            self.logger,
            self.logfolder,
        )

        return nonfollowers

    def pick_fans(
        self, username: str = None, live_match: bool = False, store_locally: bool = True
    ):
        """
         Returns Fans data- all of the usernames who do follow
        the user WHOM user itself do not follow back
        """

        message = "Starting to pick Fans of {}..".format(username)
        highlight_print(self.username, message, "feature", "info", self.logger)

        # get Fans
        fans = get_fans(
            self.browser,
            username,
            self.relationship_data,
            live_match,
            store_locally,
            self.logger,
            self.logfolder,
        )

        return fans

    def pick_mutual_following(
        self, username: str = None, live_match: bool = False, store_locally: bool = True
    ):
        """
         Returns Mutual Following data- all of the usernames who
        do follow the user WHOM user itself also do follow back
        """

        message = "Starting to pick Mutual Following of {}..".format(username)
        highlight_print(self.username, message, "feature", "info", self.logger)

        # get Mutual Following
        mutual_following = get_mutual_following(
            self.browser,
            username,
            self.relationship_data,
            live_match,
            store_locally,
            self.logger,
            self.logfolder,
        )

        return mutual_following

    def end(self, threaded_session: bool = False):
        """Closes the current session"""

        Settings.InstaPy_is_running = False
        close_browser(self.browser, threaded_session, self.logger)

        with interruption_handler(threaded=threaded_session):
            # close virtual display
            if self.nogui:
                self.display.stop()

            # write useful information
            dump_follow_restriction(self.username, self.logger, self.logfolder)
            dump_record_activity(self.username, self.logger, self.logfolder)

            with open("{}followed.txt".format(self.logfolder), "w") as followFile:
                followFile.write(str(self.followed))

            # output live stats before leaving
            self.live_report()

            message = "Session ended!"
            highlight_print(self.username, message, "end", "info", self.logger)
            print("\n\n")

    def follow_by_locations(
        self,
        locations: list = [],
        amount: int = 50,
        media: str = None,
        skip_top_posts: bool = True,
    ):
        if self.aborting:
            return self

        inap_img = 0
        followed = 0
        not_valid_users = 0

        locations = locations
        self.quotient_breach = False

        for index, location in enumerate(locations):
            if self.quotient_breach:
                break

            self.logger.info("Location [{}/{}]".format(index + 1, len(locations)))
            self.logger.info("--> {}".format(location.encode("utf-8")))

            try:
                links = get_links_for_location(
                    self.browser, location, amount, self.logger, media, skip_top_posts
                )
            except NoSuchElementException:
                self.logger.warning("Too few images, skipping this location")
                continue

            for i, link in enumerate(links):
                if (
                    self.jumps["consequent"]["follows"]
                    >= self.jumps["limit"]["follows"]
                ):
                    self.logger.warning(
                        "--> Follow quotient reached its peak!"
                        "\t~leaving Follow-By-Locations activity\n"
                    )
                    self.quotient_breach = True
                    # reset jump counter after a breach report
                    self.jumps["consequent"]["follows"] = 0
                    break

                self.logger.info("Follow# [{}/{}]".format(i + 1, len(links)))
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason, scope = check_link(
                        self.browser,
                        link,
                        self.dont_like,
                        self.mandatory_words,
                        self.mandatory_language,
                        self.is_mandatory_character,
                        self.mandatory_character,
                        self.check_character_set,
                        self.ignore_if_contains,
                        self.logger,
                    )

                    if not inappropriate:
                        # validate user
                        validation, details = self.validate_user_call(user_name)
                        if validation is not True:
                            self.logger.info(details)
                            not_valid_users += 1
                            continue
                        else:
                            web_address_navigator(self.browser, link)

                        # try to follow
                        follow_state, msg = follow_user(
                            self.browser,
                            "post",
                            self.username,
                            user_name,
                            None,
                            self.blacklist,
                            self.logger,
                            self.logfolder,
                        )
                        if follow_state is True:
                            followed += 1
                            # reset jump counter after a successful follow
                            self.jumps["consequent"]["follows"] = 0

                        elif msg == "jumped":
                            # will break the loop after certain consecutive
                            # jumps
                            self.jumps["consequent"]["follows"] += 1

                    else:
                        self.logger.info("--> User not followed: {}".format(reason))
                        inap_img += 1

                except NoSuchElementException as err:
                    self.logger.error("Invalid Page: {}".format(err))

        self.logger.info("Followed: {}".format(followed))
        self.logger.info("Inappropriate: {}".format(inap_img))
        self.logger.info("Not valid users: {}\n".format(not_valid_users))

        self.followed += followed
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return self

    def follow_by_tags(
        self,
        tags: list = [],
        amount: int = 50,
        skip_top_posts: bool = True,
        use_smart_hashtags: bool = False,
        use_smart_location_hashtags: bool = False,
        randomize: bool = False,
        media: str = None,
        interact: bool = False,
    ):

        if self.aborting:
            return self

        inap_img = 0
        followed = 0
        not_valid_users = 0

        # if smart hashtag is enabled
        if use_smart_hashtags is True and self.smart_hashtags != []:
            self.logger.info("Using smart hashtags")
            tags = self.smart_hashtags
        elif use_smart_location_hashtags is True and self.smart_location_hashtags != []:
            self.logger.info("Using smart location hashtags")
            tags = self.smart_location_hashtags

        # deletes white spaces in tags
        tags = [tag.strip() for tag in tags]
        tags = tags
        self.quotient_breach = False

        for index, tag in enumerate(tags):
            if self.quotient_breach:
                break

            self.logger.info("Tag [{}/{}]".format(index + 1, len(tags)))
            self.logger.info("--> {}".format(tag.encode("utf-8")))

            try:
                links = get_links_for_tag(
                    self.browser,
                    tag,
                    amount,
                    skip_top_posts,
                    randomize,
                    media,
                    self.logger,
                )
            except NoSuchElementException:
                self.logger.info("Too few images, skipping this tag")
                continue

            for i, link in enumerate(links):
                if (
                    self.jumps["consequent"]["follows"]
                    >= self.jumps["limit"]["follows"]
                ):
                    self.logger.warning(
                        "--> Follow quotient reached its peak!"
                        "\t~leaving Follow-By-Tags activity\n"
                    )
                    self.quotient_breach = True
                    # reset jump counter after a breach report
                    self.jumps["consequent"]["follows"] = 0
                    break

                self.logger.info("Follow# [{}/{}]".format(i + 1, len(links)))
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason, scope = check_link(
                        self.browser,
                        link,
                        self.dont_like,
                        self.mandatory_words,
                        self.mandatory_language,
                        self.is_mandatory_character,
                        self.mandatory_character,
                        self.check_character_set,
                        self.ignore_if_contains,
                        self.logger,
                    )

                    if not inappropriate:
                        # validate user
                        validation, details = self.validate_user_call(user_name)
                        if validation is not True:
                            self.logger.info(details)
                            not_valid_users += 1
                            continue
                        else:
                            web_address_navigator(self.browser, link)

                        # try to follow
                        follow_state, msg = follow_user(
                            self.browser,
                            "post",
                            self.username,
                            user_name,
                            None,
                            self.blacklist,
                            self.logger,
                            self.logfolder,
                        )
                        if follow_state is True:
                            followed += 1
                            # reset jump counter after a successful follow
                            self.jumps["consequent"]["follows"] = 0

                            # Check if interaction is expected
                            if interact and self.do_like:
                                do_interact = (
                                    random.randint(0, 100)
                                    <= self.user_interact_percentage
                                )
                                # Do interactions if any
                                if do_interact and self.user_interact_amount > 0:
                                    # store the original value
                                    original_do_follow = self.do_follow
                                    # disable following temporarily
                                    self.do_follow = False
                                    self.interact_by_users(
                                        user_name,
                                        self.user_interact_amount,
                                        self.user_interact_random,
                                        self.user_interact_media,
                                    )
                                    # back original `self.do_follow` value
                                    self.do_follow = original_do_follow
                        elif msg == "jumped":
                            # will break the loop after certain consecutive
                            # jumps
                            self.jumps["consequent"]["follows"] += 1

                    else:
                        self.logger.info("--> User not followed: {}".format(reason))
                        inap_img += 1

                except NoSuchElementException as err:
                    self.logger.error("Invalid Page: {}".format(err))

        self.logger.info("Followed: {}".format(followed))
        self.logger.info("Inappropriate: {}".format(inap_img))
        self.logger.info("Not valid users: {}\n".format(not_valid_users))

        self.followed += followed
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return self

    def interact_by_URL(
        self, urls: list = [], randomize: bool = False, interact: bool = False
    ):
        """ Interact on posts at given URLs """

        if self.aborting:
            return self

        message = "Starting to interact by given URLs.."
        highlight_print(self.username, message, "feature", "info", self.logger)

        if not isinstance(urls, list):
            urls = [urls]

        if randomize is True:
            random.shuffle(urls)

        liked_img = 0
        already_liked = 0
        inap_img = 0
        commented = 0
        followed = 0
        not_valid_users = 0

        for index, url in enumerate(urls):
            if self.jumps["consequent"]["likes"] >= self.jumps["limit"]["likes"]:
                self.logger.warning(
                    "--> Like quotient reached its peak!"
                    "\t~leaving Interact-By-URL activity\n"
                )
                # reset jump counter before breaking the loop
                self.jumps["consequent"]["likes"] = 0
                # we have not used `quotient_breach` here
                # cos this method has just one iterator
                break

            if "https://www.instagram.com/p/" not in url:
                url = "https://www.instagram.com/p/" + url

            self.logger.info("URL [{}/{}]".format(index + 1, len(urls)))
            self.logger.info("--> {}".format(url.encode("utf-8")))

            try:
                inappropriate, user_name, is_video, reason, scope = check_link(
                    self.browser,
                    url,
                    self.dont_like,
                    self.mandatory_words,
                    self.mandatory_language,
                    self.is_mandatory_character,
                    self.mandatory_character,
                    self.check_character_set,
                    self.ignore_if_contains,
                    self.logger,
                )

                if not inappropriate and self.delimit_liking:
                    self.liking_approved = verify_liking(
                        self.browser, self.max_likes, self.min_likes, self.logger
                    )

                if not inappropriate and self.liking_approved:
                    # validate user
                    validation, details = self.validate_user_call(user_name)
                    if validation is not True:
                        self.logger.info(details)
                        not_valid_users += 1
                        continue
                    else:
                        web_address_navigator(self.browser, url)

                    # try to like
                    like_state, msg = like_image(
                        self.browser,
                        user_name,
                        self.blacklist,
                        self.logger,
                        self.logfolder,
                        liked_img,
                    )

                    if like_state is True:
                        liked_img += 1
                        # reset jump counter after a successful like
                        self.jumps["consequent"]["likes"] = 0

                        checked_img = True
                        temp_comments = []

                        commenting = random.randint(0, 100) <= self.comment_percentage
                        following = random.randint(0, 100) <= self.follow_percentage

                        if self.use_clarifai and (following or commenting):
                            try:
                                (
                                    checked_img,
                                    temp_comments,
                                    clarifai_tags,
                                ) = self.query_clarifai()

                            except Exception as err:
                                self.logger.error("Image check error: {}".format(err))

                        if (
                            self.do_comment
                            and user_name not in self.dont_include
                            and checked_img
                            and commenting
                        ):

                            if self.delimit_commenting:
                                (
                                    self.commenting_approved,
                                    disapproval_reason,
                                ) = verify_commenting(
                                    self.browser,
                                    self.max_comments,
                                    self.min_comments,
                                    self.comments_mandatory_words,
                                    self.logger,
                                )
                            if self.commenting_approved:
                                # smart commenting
                                comments = self.fetch_smart_comments(
                                    is_video, temp_comments
                                )
                                if comments:
                                    comment_state, msg = comment_image(
                                        self.browser,
                                        user_name,
                                        comments,
                                        self.blacklist,
                                        self.logger,
                                        self.logfolder,
                                    )

                                    if comment_state is True:
                                        commented += 1
                            else:
                                self.logger.info(disapproval_reason)

                        else:
                            self.logger.info("--> Not commented")
                            sleep(1)

                        if (
                            self.do_follow
                            and user_name not in self.dont_include
                            and checked_img
                            and following
                            and not follow_restriction(
                                "read", user_name, self.follow_times, self.logger
                            )
                        ):
                            follow_state, msg = follow_user(
                                self.browser,
                                "post",
                                self.username,
                                user_name,
                                None,
                                self.blacklist,
                                self.logger,
                                self.logfolder,
                            )

                            if follow_state is True:
                                followed += 1
                        else:
                            self.logger.info("--> Not following")
                            sleep(1)

                        # check if interaction is expected
                        if interact is True:
                            do_interact = (
                                random.randint(0, 100) <= self.user_interact_percentage
                            )
                            # do interactions if any
                            if do_interact and self.user_interact_amount > 0:
                                self.interact_by_users(
                                    user_name,
                                    self.user_interact_amount,
                                    self.user_interact_random,
                                    self.user_interact_media,
                                )

                    elif msg == "already liked":
                        already_liked += 1

                    elif msg == "block on likes":
                        break

                    elif msg == "jumped":
                        # will break the loop after certain consecutive jumps
                        self.jumps["consequent"]["likes"] += 1

                else:
                    self.logger.info(
                        "--> Image not liked: {}".format(reason.encode("utf-8"))
                    )
                    inap_img += 1

            except NoSuchElementException as err:
                self.logger.error("Invalid Page: {}".format(err))

        self.logger.info("Liked: {}".format(liked_img))
        self.logger.info("Already Liked: {}".format(already_liked))
        self.logger.info("Commented: {}".format(commented))
        self.logger.info("Followed: {}".format(followed))
        self.logger.info("Inappropriate: {}".format(inap_img))
        self.logger.info("Not valid users: {}\n".format(not_valid_users))

        self.liked_img += liked_img
        self.already_liked += already_liked
        self.commented += commented
        self.followed += followed
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return self

    def set_quota_supervisor(
        self,
        enabled: bool = False,
        sleep_after: list = [],
        sleepyhead: bool = False,
        stochastic_flow: bool = False,
        notify_me: bool = False,
        peak_likes_hourly: int = None,
        peak_likes_daily: int = None,
        peak_comments_hourly: int = None,
        peak_comments_daily: int = None,
        peak_follows_hourly: int = None,
        peak_follows_daily: int = None,
        peak_unfollows_hourly: int = None,
        peak_unfollows_daily: int = None,
        peak_server_calls_hourly: int = None,
        peak_server_calls_daily: int = None,
    ):
        """
         Sets aside QS configuration ANY time in a session
        """

        # take a reference of the global configuration
        configuration = Settings.QS_config

        peaks = {
            "likes": {"hourly": peak_likes_hourly, "daily": peak_likes_daily},
            "comments": {"hourly": peak_comments_hourly, "daily": peak_comments_daily},
            "follows": {"hourly": peak_follows_hourly, "daily": peak_follows_daily},
            "unfollows": {
                "hourly": peak_unfollows_hourly,
                "daily": peak_unfollows_daily,
            },
            "server_calls": {
                "hourly": peak_server_calls_hourly,
                "daily": peak_server_calls_daily,
            },
        }

        if not isinstance(sleep_after, list):
            sleep_after = [sleep_after]

        rt = time.time()
        latesttime = {"hourly": rt, "daily": rt}
        orig_peaks = deepcopy(peaks)  # original peaks always remain static
        stochasticity = {
            "enabled": stochastic_flow,
            "latesttime": latesttime,
            "original_peaks": orig_peaks,
        }

        if platform.startswith("win32") and python_version() < "2.7.15":
            # UPDATE ME: remove this block once plyer is
            # verified to work on [very] old versions of Python 2
            notify_me = False

        # update QS configuration with the fresh settings
        configuration.update(
            {
                "state": enabled,
                "sleep_after": sleep_after,
                "sleepyhead": sleepyhead,
                "stochasticity": stochasticity,
                "notify": notify_me,
                "peaks": peaks,
            }
        )

    @contextmanager
    def feature_in_feature(self, feature, validate_users):
        """
         Use once a host feature calls a guest
        feature WHERE guest needs special behaviour(s)
        """

        try:
            # add the guest which is gonna be used by the host :)
            self.internal_usage[feature] = {"validate": validate_users}
            yield

        finally:
            # remove the guest just after using it
            self.internal_usage.pop(feature)

    def live_report(self):
        """ Report live sessional statistics """

        print("")

        stats = [
            self.liked_img,
            self.already_liked,
            self.commented,
            self.followed,
            self.already_followed,
            self.unfollowed,
            self.stories_watched,
            self.reels_watched,
            self.inap_img,
            self.not_valid_users,
        ]

        if self.following_num and self.followed_by:
            owner_relationship_info = (
                "On session start was FOLLOWING {} users"
                " & had {} FOLLOWERS".format(self.following_num, self.followed_by)
            )
        else:
            owner_relationship_info = ""

        sessional_run_time = self.run_time()
        run_time_info = (
            "{} seconds".format(sessional_run_time)
            if sessional_run_time < 60
            else "{} minutes".format(truncate_float(sessional_run_time / 60, 2))
            if sessional_run_time < 3600
            else "{} hours".format(truncate_float(sessional_run_time / 60 / 60, 2))
        )
        run_time_msg = "[Session lasted {}]".format(run_time_info)

        if any(stat for stat in stats):
            self.logger.info(
                "Sessional Live Report:\n"
                "\t|> LIKED {} images  |  ALREADY LIKED: {}\n"
                "\t|> COMMENTED on {} images\n"
                "\t|> FOLLOWED {} users  |  ALREADY FOLLOWED: {}\n"
                "\t|> UNFOLLOWED {} users\n"
                "\t|> LIKED {} comments\n"
                "\t|> REPLIED to {} comments\n"
                "\t|> INAPPROPRIATE images: {}\n"
                "\t|> NOT VALID users: {}\n"
                "\t|> WATCHED {} story(ies)  |  WATCHED {} reel(s)\n"
                "\n{}\n{}".format(
                    self.liked_img,
                    self.already_liked,
                    self.commented,
                    self.followed,
                    self.already_followed,
                    self.unfollowed,
                    self.liked_comments,
                    self.replied_to_comments,
                    self.inap_img,
                    self.not_valid_users,
                    self.stories_watched,
                    self.reels_watched,
                    owner_relationship_info,
                    run_time_msg,
                )
            )
        else:
            self.logger.info(
                "Sessional Live Report:\n"
                "\t|> No any statistics to show\n"
                "\n{}\n{}".format(owner_relationship_info, run_time_msg)
            )

    def set_do_reply_to_comments(self, enabled: bool = False, percentage: int = 0):
        """ Define if the comments on posts should be replied """

        self.do_reply_to_comments = enabled
        self.reply_to_comments_percent = percentage

        return self

    def set_comment_replies(self, replies: list = [], media: str = None):
        """ Set the replies to comments """

        if not replies:
            self.logger.info("Please, provide some comment replies for use next time.")
            self.comment_replies = None
            self.photo_comment_replies = None
            self.video_comment_replies = None

            return self

        if media in ["Photo", "Video"]:
            attr = "{}_comment_replies".format(media.lower())
            setattr(self, attr, replies)

        else:
            if media is not None:
                self.logger.warning(
                    "Unkown media type set at" " comment replies! Treating as 'any'."
                )

            self.comment_replies = replies

    def set_use_meaningcloud(
        self,
        enabled: bool = False,
        license_key: str = None,
        polarity: str = "P",
        agreement: str = None,
        subjectivity: str = None,
        confidence: bool = 100,
    ):
        """ Set MeaningCloud Sentiment Analysis API configuration """

        if license_key is None:
            license_key = os.environ.get("MEANINGCLOUD_LIC_KEY")

        if polarity.upper() not in ["P", "P+", "NEU", "N", "N+"]:
            self.logger.info(
                "Oh no! Please provide a valid polarity "
                "score tag for MeaningCloud"
                "\t~service will not operate"
            )
            polarity = None

        if enabled and license_key and polarity:
            Settings.meaningcloud_config.update(
                enabled=enabled,
                license_key=license_key,
                score_tag=polarity.upper(),
                agreement=agreement.upper() if agreement else None,
                subjectivity=subjectivity.upper() if subjectivity else None,
                confidence=int(confidence) if confidence else None,
            )

        else:
            # turn off MeaningCloud service if not enabled or wrongly
            # configured
            Settings.meaningcloud_config.update(enabled=False)

    def set_use_yandex(
        self,
        enabled: bool = False,
        API_key: str = None,
        match_language: bool = False,
        language_code: str = "en",
    ):
        """ Set Yandex Translate API configuration """

        if API_key is None:
            API_key = os.environ.get("YANDEX_API_KEY")

        if enabled and API_key:
            Settings.yandex_config.update(enabled=enabled, API_key=API_key)

            if match_language is True and language_code:
                supported_langs = yandex_supported_languages()

                if not supported_langs or language_code.lower() not in supported_langs:
                    msg = (
                        "Oh no! Failed to get the list of supported"
                        " languages by Yandex Translate :("
                        if not supported_langs
                        else "Oh no! The language with '{}' code is not"
                        " supported by Yandex Translate :/".format(language_code)
                    )
                    self.logger.info("{}\t~text language won't be matched".format(msg))
                    match_language = False

            Settings.yandex_config.update(
                match_language=match_language if language_code else False,
                language_code=language_code.lower() if language_code else None,
            )

        else:
            # turn off Yandex service if not enabled or wrongly configured
            Settings.yandex_config.update(enabled=False)

    def interact_by_comments(
        self,
        usernames: list = None,
        posts_amount: int = 10,
        comments_per_post: int = 1,
        reply: bool = False,
        interact: bool = False,
        randomize: bool = False,
        media: str = None,
    ):
        """
         Like comments of people on posts, reply to them
        and also interact with those commenters
        """
        if self.aborting:
            return self
        message = "Starting to interact by comments.."
        highlight_print(self.username, message, "feature", "info", self.logger)

        if not isinstance(usernames, list):
            usernames = [usernames]

        if media not in ["Photo", "Video", None]:
            self.logger.warning(
                "Unkown media type- '{}' set at"
                " Interact-By-Comments!\t~treating as any..".format(media)
            )
            media = None

        # hold the current global values for differentiating at the end
        liked_init = self.liked_img
        already_liked_init = self.already_liked
        liked_comments_init = self.liked_comments
        commented_init = self.commented
        replied_to_comments_init = self.replied_to_comments
        followed_init = self.followed
        already_followed_init = self.already_followed
        inap_img_init = self.inap_img
        not_valid_users_init = self.not_valid_users

        overall_posts_count = 0
        self.quotient_breach = False
        like_failures_tracker = {
            "consequent": {"post_likes": 0, "comment_likes": 0},
            "limit": {"post_likes": 5, "comment_likes": 10},
        }

        leave_msg = "\t~leaving Interact-By-Comments activity\n"

        # start the interaction!
        for s, username in enumerate(usernames):
            if self.quotient_breach:
                break

            message = "User: [{}/{}]".format(s + 1, len(usernames))
            highlight_print(
                self.username, message, "user iteration", "info", self.logger
            )

            if username != self.username:
                validation, details = self.validate_user_call(username)
                if validation is not True:
                    self.logger.info("--> Not a valid user: {}".format(details))
                    self.not_valid_users += 1
                    continue

            per_user_liked_comments = 0
            per_user_replied_to_comments = 0
            per_user_used_replies = []

            try:
                links = get_links_for_username(
                    self.browser,
                    self.username,
                    username,
                    posts_amount,
                    self.logger,
                    self.logfolder,
                    randomize,
                    media,
                )
            except NoSuchElementException:
                self.logger.error("Element not found, skipping this user.")
                continue

            if links is False:
                continue

            else:
                if randomize:
                    random.shuffle(links)
                links = links[:posts_amount]
                overall_posts_count += len(links)

            for i, link in enumerate(links):
                if self.quotient_breach:
                    break

                elif (
                    self.jumps["consequent"]["comments"]
                    >= self.jumps["limit"]["comments"]
                ):
                    self.logger.warning(
                        "--> Comment quotient reached its peak!{}".format(leave_msg)
                    )
                    self.quotient_breach = True
                    # reset jump counter after a breach report
                    self.jumps["consequent"]["comments"] = 0
                    break

                elif (
                    like_failures_tracker["consequent"]["post_likes"]
                    >= like_failures_tracker["limit"]["post_likes"]
                ):
                    self.logger.warning(
                        "--> Too many failures to like posts!{}".format(leave_msg)
                    )
                    # this example shows helpful usage of
                    # quotient breach outside QS needs..
                    self.quotient_breach = True
                    break

                message = "Post: [{}/{}]".format(i + 1, len(links))
                highlight_print(
                    self.username, message, "post iteration", "info", self.logger
                )

                (inappropriate, user_name, is_video, reason, scope) = check_link(
                    self.browser,
                    link,
                    self.dont_like,
                    self.mandatory_words,
                    self.mandatory_language,
                    self.is_mandatory_character,
                    self.mandatory_character,
                    self.check_character_set,
                    self.ignore_if_contains,
                    self.logger,
                )

                if inappropriate:
                    self.logger.info(
                        "--> Post not interacted. {}\n".format(reason.encode("utf-8"))
                    )
                    self.inap_img += 1
                    continue

                # go go!
                per_post_liked_comments = 0
                per_post_replied_to_comments = 0
                per_post_interacted_commenters = []

                # get comments (if any)
                comment_data = get_comments_on_post(
                    self.browser,
                    self.username,
                    username,
                    comments_per_post,
                    link,
                    self.ignore_users,
                    randomize,
                    self.logger,
                )
                if not comment_data:
                    self.logger.info("No interaction did happen.\n")
                    continue

                # like the post before interacting on comments
                image_like_state, msg = like_image(
                    self.browser,
                    user_name,
                    self.blacklist,
                    self.logger,
                    self.logfolder,
                    self.liked_img,
                )
                if image_like_state is True:
                    like_failures_tracker["consequent"]["post_likes"] = 0
                    self.liked_img += 1

                elif msg == "already liked":
                    self.already_liked += 1

                elif msg == "block on likes":
                    break

                else:
                    self.logger.info(
                        "Can't interact by comments unless"
                        " the post is liked! :(\t~skipping this post\n"
                    )
                    like_failures_tracker["consequent"]["post_likes"] += 1
                    continue

                # perfect! now going to work with comments...
                for commenter, comment in comment_data:
                    if per_post_liked_comments >= comments_per_post:
                        break

                    elif (
                        like_failures_tracker["consequent"]["comment_likes"]
                        >= like_failures_tracker["limit"]["comment_likes"]
                    ):
                        self.logger.warning(
                            "--> Too many failures to like comments!{}".format(
                                leave_msg
                            )
                        )
                        # this example shows helpful usage of
                        # quotient breach outside QS needs..
                        self.quotient_breach = True
                        break

                    # verify the comment content by sentiment analysis &
                    # language detection if enabled
                    text_analysis_state = text_analysis(comment, "comment", self.logger)
                    if text_analysis_state is False:
                        # comment is inappropriate to be liked [and replied]
                        continue

                    # like the comment
                    comment_like_state, msg = like_comment(
                        self.browser, comment, self.logger
                    )
                    if comment_like_state is not True:
                        like_failures_tracker["consequent"]["comment_likes"] += 1
                        continue

                    else:
                        per_post_interacted_commenters.append(commenter)
                        self.liked_comments += 1
                        per_user_liked_comments += 1
                        per_post_liked_comments += 1
                        like_failures_tracker["consequent"]["comment_likes"] = 0

                        # send a reply to the comment if is appropriate
                        if (
                            self.do_reply_to_comments
                            and reply
                            and text_analysis_state is True
                        ):
                            do_reply_to_comment = (
                                self.reply_to_comments_percent >= random.randint(0, 100)
                            )

                            comment_replies_base = self.comment_replies + (
                                self.video_comment_replies
                                if is_video
                                else self.photo_comment_replies
                            )
                            # dismiss the already used replies per each user
                            comment_replies_base = [
                                reply
                                for reply in comment_replies_base
                                if reply not in per_user_used_replies
                            ]

                            if do_reply_to_comment and comment_replies_base:
                                chosen_reply = random.choice(comment_replies_base)
                                # mention the commenter to make a reply :)
                                reply_msg = ["@{} {}".format(commenter, chosen_reply)]

                                reply_to_comment_state, msg = comment_image(
                                    self.browser,
                                    commenter,
                                    reply_msg,
                                    self.blacklist,
                                    self.logger,
                                    self.logfolder,
                                )

                                if reply_to_comment_state is True:
                                    per_user_used_replies.extend(chosen_reply)
                                    self.replied_to_comments += 1
                                    self.commented += 1
                                    per_user_replied_to_comments += 1
                                    per_post_replied_to_comments += 1
                                    # reset jump counter after a successful
                                    # comment
                                    self.jumps["consequent"]["comments"] = 0

                                elif msg == "jumped":
                                    # will break the loop after
                                    # certain consecutive jumps
                                    self.jumps["consequent"]["comments"] += 1

                post_No_ending = (
                    "st"
                    if str(i + 1).endswith("1")
                    else "nd"
                    if str(i + 1).endswith("2")
                    else "rd"
                    if str(i + 1).endswith("3")
                    else "th"
                    if str(i + 1).endswith("4")
                    else ""
                )
                post_No = "{}{}".format(str(i + 1), post_No_ending)

                # quick log after interacting on a post
                print("")
                self.logger.info(
                    "Finished interacting on {} post's comments!".format(post_No)
                )
                self.logger.info("\tLiked comments: {}".format(per_post_liked_comments))
                self.logger.info(
                    "\tReplied to comments: {}\n".format(per_post_replied_to_comments)
                )

                # standalone interaction with commenters whose
                # comment was liked on the post
                if interact and per_post_interacted_commenters:
                    with self.feature_in_feature("interact_by_users", True):
                        self.interact_by_users(
                            per_post_interacted_commenters,
                            self.user_interact_amount,
                            self.user_interact_random,
                            self.user_interact_media,
                        )

            # quick log after interacting with a user
            print("")
            self.logger.info(
                "Finished interacting on {} posts' comments of '{}'!".format(
                    len(links), username
                )
            )
            self.logger.info("\tLiked comments: {}".format(per_user_liked_comments))
            self.logger.info(
                "\tReplied to comments: {}\n".format(per_user_replied_to_comments)
            )

        # full log after finishing whole work
        self.logger.info(
            "Finished interacting on {} posts' comments from {} users!".format(
                overall_posts_count, len(usernames)
            )
        )

        # find the feature-wide action sizes by taking a difference
        liked_img = self.liked_img - liked_init
        already_liked = self.already_liked - already_liked_init
        liked_comments = self.liked_comments - liked_comments_init
        replied_to_comments = self.replied_to_comments - replied_to_comments_init
        commented = (self.commented - commented_init) - replied_to_comments
        followed = self.followed - followed_init
        already_followed = self.already_followed - already_followed_init
        inap_img = self.inap_img - inap_img_init
        not_valid_users = self.not_valid_users - not_valid_users_init

        if self.liked_comments:
            # output results
            self.logger.info("\tLiked comments: {}".format(liked_comments))
            self.logger.info("\tReplied to comments: {}".format(replied_to_comments))
            self.logger.info("\tLiked posts: {}".format(liked_img))
            self.logger.info("\tAlready liked posts: {}".format(already_liked))
            self.logger.info("\tCommented posts: {}".format(commented))
            self.logger.info("\tFollowed users: {}".format(followed))
            self.logger.info("\tAlready followed users: {}".format(already_followed))
            self.logger.info("\tInappropriate posts: {}".format(inap_img))
            self.logger.info("\tNot valid users: {}".format(not_valid_users))

    def is_mandatory_character(self, uchr):
        if self.aborting:
            return self
        try:
            return self.check_letters[uchr]
        except KeyError:
            return self.check_letters.setdefault(
                uchr,
                any(
                    mandatory_char in unicodedata.name(uchr)
                    for mandatory_char in self.mandatory_character
                ),
            )

    def run_time(self):
        """ Get the time session lasted in seconds """

        real_time = time.time()
        run_time = real_time - self.start_time
        run_time = truncate_float(run_time, 2)

        return run_time

    def check_character_set(self, unistr):
        self.check_letters = {}
        if self.aborting:
            return self
        return all(
            self.is_mandatory_character(uchr) for uchr in unistr if uchr.isalpha()
        )

    def accept_follow_requests(self, amount: int = 100, sleep_delay: int = 1):
        """Accept pending follow requests from activity feed"""

        if self.aborting:
            return self

        message = "Starting to get follow requests.."
        highlight_print(self.username, message, "feature", "info", self.logger)

        accepted = 0
        while accepted < amount:

            feed_link = "https://www.instagram.com/accounts/activity/?followRequests=1"
            web_address_navigator(self.browser, feed_link)

            requests_to_confirm = self.browser.find_elements_by_xpath(
                "//button[text()='Confirm']"
            )

            if len(requests_to_confirm) == 0:
                self.logger.info("There are no follow requests in activity feed")
                break

            for request in requests_to_confirm:
                request.click()
                sleep(sleep_delay)
                accepted += 1
                if accepted >= amount:
                    self.logger.info(
                        "Reached accepted accounts limit of {} requests".format(amount)
                    )
                    break

        self.logger.info("Accepted {} follow requests".format(accepted))

        return self

    def join_pods(self, topic: str = "general", engagement_mode: str = "normal"):
        """ Join pods """
        if topic not in self.allowed_pod_topics:
            self.logger.error(
                "You have entered an invalid topic for pods, allowed topics are : {}. Exiting...".format(
                    self.allowed_pod_topics
                )
            )
            return self

        if engagement_mode not in self.allowed_pod_engagement_modes:
            self.logger.error(
                "You have entered an invalid engagement_mode for pods, allowed engagement_modes are : {}. Exiting...".format(
                    self.allowed_pod_engagement_modes
                )
            )
            return self

        if self.comments is not None and len(self.comments) < 10:
            self.logger.error(
                "You have too few comments, please set at least 10 distinct comments to avoid looking suspicious."
            )
            return self

        user_link = "https://www.instagram.com/{}/".format(self.username)
        web_address_navigator(self.browser, user_link)
        try:
            pod_posts = get_recent_posts_from_pods(topic, self.logger)
            self.logger.info("Downloaded pod_posts : {}".format(pod_posts))

            sleep(2)
            post_link_elems = self.browser.find_elements_by_xpath(
                "//a[contains(@href, '/p/')]"
            )
            post_links = []

            for post_link_elem in post_link_elems:
                try:
                    post_link = post_link_elem.get_attribute("href")
                    post_links.append(post_link)
                except Exception as e:
                    self.logger.error(
                        "Can not get href for {} - {}".format(post_link, e)
                    )
                    continue

            post_links = list(set(post_links))
            my_recent_post_ids = []
            for post_link in post_links:
                try:
                    web_address_navigator(self.browser, post_link)
                    sleep(2)
                    time_element = self.browser.find_element_by_xpath("//div/a/time")
                    post_datetime_str = time_element.get_attribute("datetime")
                    post_datetime = datetime.strptime(
                        post_datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ"
                    )
                    postid = post_link.split("/")[4]
                    self.logger.info(
                        "Post: {}, Instaposted at: {}".format(postid, post_datetime)
                    )
                    share_restricted = share_with_pods_restriction(
                        "read", postid, self.share_times, self.logger
                    )
                    if (
                        datetime.now() - post_datetime < timedelta(hours=12, minutes=30)
                        and not share_restricted
                    ):
                        my_recent_post_ids.append(postid)
                        if share_my_post_with_pods(
                            postid, topic, engagement_mode, self.logger
                        ):
                            share_with_pods_restriction(
                                "write", postid, None, self.logger
                            )
                except Exception as err:
                    self.logger.error(
                        "Failed for {} with Error {}".format(post_link, err)
                    )

            if len(my_recent_post_ids) > 0:
                self.logger.info(
                    "I have recent post(s): {}, so I will now help pod members actively.".format(
                        my_recent_post_ids
                    )
                )
                nposts = 200
            else:
                self.logger.info(
                    "I don't have any recent post, so I will just help a few pod posts and move on."
                )
                nposts = 40

            if len(pod_posts) <= nposts:
                pod_posts = pod_posts
            else:
                pod_posts = random.sample(pod_posts, nposts)

            no_comments_posts, light_posts, normal_posts, heavy_posts = group_posts(
                pod_posts, self.logger
            )

            self.logger.error("no_comments_posts : {} ".format(no_comments_posts))
            self.logger.error("light_posts : {} ".format(light_posts))
            self.logger.error("normal_posts : {} ".format(normal_posts))
            self.logger.error("heavy_posts : {} ".format(heavy_posts))

            self.engage_with_posts(no_comments_posts, 0)
            self.engage_with_posts(light_posts, 10)
            self.engage_with_posts(normal_posts, 30)
            self.engage_with_posts(heavy_posts, 90)

        except Exception as err:
            self.logger.error(err)

        return self

    def engage_with_posts(self, pod_posts, modespecific_comment_percentage):
        for pod_post in pod_posts:
            try:
                pod_post_id = pod_post["postid"]
                post_link = "https://www.instagram.com/p/{}".format(pod_post_id)
                web_address_navigator(self.browser, post_link)

                inappropriate, user_name, is_video, reason, scope = check_link(
                    self.browser,
                    post_link,
                    self.dont_like,
                    self.mandatory_words,
                    self.mandatory_language,
                    self.is_mandatory_character,
                    self.mandatory_character,
                    self.check_character_set,
                    self.ignore_if_contains,
                    self.logger,
                )

                if user_name != self.username:
                    follow_state, msg = follow_user(
                        self.browser,
                        "post",
                        self.username,
                        user_name,
                        None,
                        self.blacklist,
                        self.logger,
                        self.logfolder,
                    )

                    self.dont_include.add(user_name)

                if not inappropriate and user_name != self.username:
                    pods_like_percent = max(90, min(100, self.like_percentage))
                    liking = random.randint(0, 100) <= pods_like_percent
                    commenting = (
                        random.randint(0, 100) <= modespecific_comment_percentage
                    )

                    if liking:
                        like_state, msg = like_image(
                            self.browser,
                            user_name,
                            self.blacklist,
                            self.logger,
                            self.logfolder,
                            self.liked_img,
                        )

                        if like_state is True:
                            self.liked_img += 1

                        elif msg == "block on likes":
                            break

                    commenting_restricted = comment_restriction(
                        "read", pod_post_id, self.comment_times, self.logger
                    )

                    if commenting and not commenting_restricted:
                        comments = self.fetch_smart_comments(is_video, temp_comments=[])

                        comment_state, msg = comment_image(
                            self.browser,
                            user_name,
                            comments,
                            self.blacklist,
                            self.logger,
                            self.logfolder,
                        )
                        if comment_state:
                            comment_restriction("write", pod_post_id, None, self.logger)

            except Exception as err:
                self.logger.error("Failed for {} with Error {}".format(pod_post, err))

    def story_by_tags(self, tags: list = None):
        """ Watch stories for specific tag(s) """
        if self.aborting:
            return self

        if tags is None:
            self.logger.info("No Tags set")
        else:
            # iterate over available tags
            for index, tag in enumerate(tags):
                # Quota Supervisor peak check
                if self.quotient_breach:
                    break

                # inform user whats happening
                if len(tags) > 1:
                    self.logger.info("Tag [{}/{}]".format(index + 1, len(tags)))
                self.logger.info(
                    "Loading stories with Tag --> {}".format(tag.encode("utf-8"))
                )

                try:
                    reels = watch_story(
                        self.browser, tag, self.logger, "tag", self.story_simulate
                    )
                except NoSuchElementException:
                    self.logger.info("No stories skipping this tag")
                    continue
                if reels > 0:
                    self.stories_watched += 1
                    self.reels_watched += reels

    def story_by_users(self, users: list = None):
        """ Watch stories for specific user(s)"""
        if self.aborting:
            return self

        if users is None:
            self.logger.info("No users passed to story_by_users")
        else:
            # iterate over available users
            for index, user in enumerate(users):
                # Quota Supervisor peak check
                if self.quotient_breach:
                    break

                # inform user whats happening
                if len(users) > 1:
                    self.logger.info("User [{}/{}]".format(index + 1, len(users)))
                self.logger.info(
                    "Loading stories with User --> {}".format(user.encode("utf-8"))
                )

                try:
                    reels = watch_story(
                        self.browser, user, self.logger, "user", self.story_simulate
                    )
                except NoSuchElementException:
                    self.logger.info("No stories skipping this user")
                    continue
                if reels > 0:
                    self.stories_watched += 1
                    self.reels_watched += reels
