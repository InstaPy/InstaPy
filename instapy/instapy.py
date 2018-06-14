"""OS Modules environ method to get the setup vars from the Environment"""
import csv
import json
import logging
import re
from math import ceil
import os
from platform import python_version
from datetime import datetime
import random

import selenium
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
import requests

from .clarifai_util import check_image
from .comment_util import comment_image
from .like_util import check_link
from .like_util import verify_liking
from .comment_util import verify_commenting
from .like_util import get_links_for_tag
from .like_util import get_links_from_feed
from .like_util import get_tags
from .like_util import get_links_for_location
from .like_util import like_image
from .like_util import get_links_for_username
from .login_util import login_user
from .print_log_writer import log_follower_num
from .settings import Settings
from .print_log_writer import log_following_num
from .time_util import sleep
from .time_util import set_sleep_percentage
from .util import get_active_users
from .util import validate_username
from .util import web_adress_navigator
from .unfollow_util import get_given_user_followers
from .unfollow_util import get_given_user_following
from .unfollow_util import unfollow
from .unfollow_util import unfollow_user
from .unfollow_util import follow_user
from .unfollow_util import follow_given_user
from .unfollow_util import load_follow_restriction
from .unfollow_util import dump_follow_restriction
from .unfollow_util import set_automated_followed_pool
from .feed_util import get_like_on_feed
from .commenters_util import extract_post_info     
from .commenters_util import extract_information
from .commenters_util import users_liked
from .commenters_util import get_photo_urls_from_profile



class InstaPyError(Exception):
    """General error for InstaPy exceptions"""


class InstaPy:
    """Class to be instantiated to use the script"""

    def __init__(self,
                 username=None,
                 password=None,
                 nogui=False,
                 selenium_local_session=True,
                 use_firefox=False,
                 browser_profile_path=None,
                 page_delay=25,
                 show_logs=True,
                 headless_browser=False,
                 proxy_address=None,
                 proxy_chrome_extension=None,
                 proxy_port=0,
                 bypass_suspicious_attempt=False,
                 multi_logs=False):

        if nogui:
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()

        self.browser = None
        self.headless_browser = headless_browser
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self.proxy_chrome_extension = proxy_chrome_extension

        self.username = username or os.environ.get('INSTA_USER')
        self.password = password or os.environ.get('INSTA_PW')
        self.nogui = nogui
        self.logfolder = Settings.log_location + os.path.sep
        if multi_logs is True:
            self.logfolder = '{0}{1}{2}{1}'.format(
                Settings.log_location, os.path.sep, self.username)
        if not os.path.exists(self.logfolder):
            os.makedirs(self.logfolder)

        self.page_delay = page_delay
        self.switch_language = True
        self.use_firefox = use_firefox
        self.browser_profile_path = browser_profile_path

        self.do_comment = False
        self.comment_percentage = 0
        self.comments = ['Cool!', 'Nice!', 'Looks good!']
        self.photo_comments = []
        self.video_comments = []

        self.followed = 0
        self.liked_img = 0
        self.already_liked = 0
        self.already_Visited = 0
        self.inap_img = 0
        self.commented = 0
        self.followed_by = 0
        self.unfollowNumber = 0
        self.not_valid_users = 0

        self.follow_restrict = load_follow_restriction(self.logfolder)

        self.follow_times = 1
        self.do_follow = False
        self.follow_percentage = 0
        self.dont_include = []
        self.blacklist = {'enabled': 'True', 'campaign': ''}
        self.automatedFollowedPool = []
        self.do_like = False
        self.like_percentage = 0
        self.smart_hashtags = []

        self.dont_like = ['sex', 'nsfw']
        self.ignore_if_contains = []
        self.ignore_users = []

        self.user_interact_amount = 0
        self.user_interact_media = None
        self.user_interact_percentage = 0
        self.user_interact_random = False

        self.use_clarifai = False
        self.clarifai_api_key = None
        self.clarifai_img_tags = []
        self.clarifai_img_tags_skip = []
        self.clarifai_full_match = False
        
        self.potency_ratio = 1.3466
        self.delimit_by_numbers = True
        
        self.max_followers = 90000
        self.max_following = 66834
        self.min_followers = 35
        self.min_following = 27
        
        self.delimit_liking = False
        self.liking_approved = True
        self.max_likes = 1000
        self.min_likes = 0
        
        self.delimit_commenting = False
        self.commenting_approved = True
        self.max_comments = 35
        self.min_comments = 0

        self.bypass_suspicious_attempt = bypass_suspicious_attempt

        self.aborting = False

        # Assign logger
        self.logger = self.get_instapy_logger(show_logs)

        if selenium_local_session:
            self.set_selenium_local_session()


    def get_instapy_logger(self, show_logs):
        """
        Handles the creation and retrieval of loggers to avoid re-instantiation.
        """

        existing_logger = Settings.loggers.get(__name__)
        if existing_logger is not None:
            return existing_logger
        else:
            # initialize and setup logging system for the InstaPy object
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)
            file_handler = logging.FileHandler('{}general.log'.format(self.logfolder))
            file_handler.setLevel(logging.DEBUG)
            extra = {"username": self.username}
            logger_formatter = logging.Formatter('%(levelname)s [%(asctime)s] [%(username)s]  %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(logger_formatter)
            logger.addHandler(file_handler)

            if show_logs is True:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                console_handler.setFormatter(logger_formatter)
                logger.addHandler(console_handler)

            logger = logging.LoggerAdapter(logger, extra)

            Settings.loggers[__name__] = logger
            Settings.logger = logger
            return logger

    def set_selenium_local_session(self):
        """Starts local session for a selenium server.
        Default case scenario."""
        if self.aborting:
            return self

        if self.use_firefox:
            if self.browser_profile_path is not None:
                firefox_profile = webdriver.FirefoxProfile(
                    self.browser_profile_path)
            else:
                firefox_profile = webdriver.FirefoxProfile()

            # permissions.default.image = 2: Disable images load,
            # this setting can improve pageload & save bandwidth
            firefox_profile.set_preference('permissions.default.image', 2)

            if self.proxy_address and self.proxy_port > 0:
                firefox_profile.set_preference('network.proxy.type', 1)
                firefox_profile.set_preference('network.proxy.http',
                                               self.proxy_address)
                firefox_profile.set_preference('network.proxy.http_port',
                                               self.proxy_port)
                firefox_profile.set_preference('network.proxy.ssl',
                                               self.proxy_address)
                firefox_profile.set_preference('network.proxy.ssl_port',
                                               self.proxy_port)

            self.browser = webdriver.Firefox(firefox_profile=firefox_profile)

        else:
            chromedriver_location = Settings.chromedriver_location
            chrome_options = Options()
            #chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--mute-audio")
            chrome_options.add_argument('--dns-prefetch-disable')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--lang=en-US')
            chrome_options.add_argument('--disable-setuid-sandbox')

            # this option implements Chrome Headless, a new (late 2017)
            # GUI-less browser. chromedriver 2.9 and above required
            if self.headless_browser:
                chrome_options.add_argument('--headless')
                # Replaces browser User Agent from "HeadlessChrome".
                user_agent = "Chrome"
                chrome_options.add_argument('user-agent={user_agent}'
                                            .format(user_agent=user_agent))
            capabilities = DesiredCapabilities.CHROME
            # Proxy for chrome
            if self.proxy_address and self.proxy_port > 0:
                prox = Proxy()
                proxy = ":".join([self.proxy_address, self.proxy_port])
                prox.proxy_type = ProxyType.MANUAL
                prox.http_proxy = proxy
                prox.socks_proxy = proxy
                prox.ssl_proxy = proxy
                prox.add_to_capabilities(capabilities)

            # add proxy extension
            if self.proxy_chrome_extension and not self.headless_browser:
                chrome_options.add_extension(self.proxy_chrome_extension)

            if self.browser_profile_path is not None:
                chrome_options.add_argument('user-data-dir={}'.format(self.browser_profile_path))

            chrome_prefs = {
                'intl.accept_languages': 'en-US'
            }
            chrome_options.add_experimental_option('prefs', chrome_prefs)
            try:
                self.browser = webdriver.Chrome(chromedriver_location,
                                                desired_capabilities=capabilities,
                                                chrome_options=chrome_options)
            except selenium.common.exceptions.WebDriverException as exc:
                self.logger.exception(exc)
                raise InstaPyError('ensure chromedriver is installed at {}'.format(
                    Settings.chromedriver_location))

            # prevent: Message: unknown error: call function result missing 'value'
            matches = re.match(r'^(\d+\.\d+)',
                               self.browser.capabilities['chrome']['chromedriverVersion'])
            if float(matches.groups()[0]) < Settings.chromedriver_min_version:
                raise InstaPyError('chromedriver {} is not supported, expects {}+'.format(
                    float(matches.groups()[0]), Settings.chromedriver_min_version))

        self.browser.implicitly_wait(self.page_delay)
        self.logger.info('Session started - %s'
                         % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        return self

    def set_selenium_remote_session(self, selenium_url=''):
        """Starts remote session for a selenium server.
         Useful for docker setup."""
        if self.aborting:
            return self

        if self.use_firefox:
            self.browser = webdriver.Remote(
                command_executor=selenium_url,
                desired_capabilities=DesiredCapabilities.FIREFOX)
        else:
            self.browser = webdriver.Remote(
                command_executor=selenium_url,
                desired_capabilities=DesiredCapabilities.CHROME)

        self.logger.info('Session started - %s'
                         % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        return self

    def login(self):
        """Used to login the user either with the username and password"""
        if not login_user(self.browser,
                          self.username,
                          self.password,
                          self.logfolder,
                          self.switch_language,
                          self.bypass_suspicious_attempt):
            self.logger.critical('Wrong login data!')

            self.aborting = True
        else:
            self.logger.info('Logged in successfully!')

        self.followed_by = log_follower_num(self.browser, self.username, self.logfolder)
        self.following_num = log_following_num(self.browser, self.username, self.logfolder)

        return self

    def set_sleep_reduce(self, percentage):
        set_sleep_percentage(percentage)

        return self

    def set_do_comment(self, enabled=False, percentage=0):
        """Defines if images should be commented or not
        percentage=25 -> ~ every 4th picture will be commented"""
        if self.aborting:
            return self

        self.do_comment = enabled
        self.comment_percentage = percentage

        return self

    def set_comments(self, comments=None, media=None):
        """Changes the possible comments"""
        if self.aborting:
            return self

        if (media not in [None, 'Photo', 'Video']):
            self.logger.warning('Unkown media type! Treating as "any".')
            media = None

        self.comments = comments or []

        if media is None:
            self.comments = comments
        else:
            attr = '{}_comments'.format(media.lower())
            setattr(self, attr, comments)

        return self

    def set_do_follow(self, enabled=False, percentage=0, times=1):
        """Defines if the user of the liked image should be followed"""
        if self.aborting:
            return self

        self.follow_times = times
        self.do_follow = enabled
        self.follow_percentage = percentage

        return self

    def set_do_like(self, enabled=False, percentage=0):
        if self.aborting:
            return self

        self.do_like = enabled
        self.like_percentage = percentage

        return self

    def set_dont_like(self, tags=None):
        """Changes the possible restriction tags, if one of this
         words is in the description, the image won't be liked"""
        if self.aborting:
            return self

        if not isinstance(tags, list):
            self.logger.warning('Unable to use your set_dont_like '
                                'configuration!')
            self.aborting = True

        self.dont_like = tags or []

        return self

    def set_user_interact(self,
                          amount=10,
                          percentage=100,
                          randomize=False,
                          media=None):
        """Define if posts of given user should be interacted"""
        if self.aborting:
            return self

        self.user_interact_amount = amount
        self.user_interact_random = randomize
        self.user_interact_percentage = percentage
        self.user_interact_media = media

        return self

    def set_ignore_users(self, users=None):
        """Changes the possible restriction to users, if a user who posts
        is one of these, the image won't be liked"""
        if self.aborting:
            return self

        self.ignore_users = users or []

        return self

    def set_ignore_if_contains(self, words=None):
        """Ignores the don't likes if the description contains
        one of the given words"""
        if self.aborting:
            return self

        self.ignore_if_contains = words or []

        return self

    def set_dont_include(self, friends=None):
        """Defines which accounts should not be unfollowed"""
        if self.aborting:
            return self

        self.dont_include = friends or []

        return self

    def set_switch_language(self, option=True):
        self.switch_language = option
        return self

    def set_use_clarifai(self, enabled=False, api_key=None, full_match=False):
        """
        Defines if the clarifai img api should be used
        Which 'project' will be used (only 5000 calls per month)

        Raises:
            InstaPyError if os is windows
        """
        if self.aborting:
            return self

        #if os.name == 'nt':
        #    raise InstaPyError('Clarifai is not supported on Windows')

        self.use_clarifai = enabled

        if api_key is None and self.clarifai_api_key is None:
            self.clarifai_api_key = os.environ.get('CLARIFAI_API_KEY')
        elif api_key is not None:
            self.clarifai_api_key = api_key

        self.clarifai_full_match = full_match

        return self

    def set_smart_hashtags(self,
                           tags=None,
                           limit=3,
                           sort='top',
                           log_tags=True):
        """Generate smart hashtags based on https://displaypurposes.com/"""
        """ranking, banned and spammy tags are filtered out."""

        if tags is None:
            print('set_smart_hashtags is misconfigured')
            return

        for tag in tags:
            req = requests.get(
                u'https://d212rkvo8t62el.cloudfront.net/tag/{}'.format(tag))
            data = json.loads(req.text)

            if data['tagExists'] is True:
                if sort == 'top':
                    # sort by ranking
                    ordered_tags_by_rank = sorted(
                        data['results'], key=lambda d: d['rank'], reverse=True)
                    ranked_tags = (ordered_tags_by_rank[:limit])
                    for item in ranked_tags:
                        # add smart hashtag to like list
                        self.smart_hashtags.append(item['tag'])

                elif sort == 'random':
                    random_tags = random.sample(data['results'], limit)
                    for item in random_tags:
                        self.smart_hashtags.append(item['tag'])

                if log_tags is True:
                    for item in self.smart_hashtags:
                        print(u'[smart hashtag generated: {}]'.format(item))
            else:
                print(u'Too few results for #{} tag'.format(tag))

        # delete duplicated tags
        self.smart_hashtags = list(set(self.smart_hashtags))
        return self

    def clarifai_check_img_for(self, tags=None, tags_skip=None, comment=False, comments=None):
        """Defines the tags, the images should be checked for"""
        if self.aborting:
            return self

        if tags is None and not self.clarifai_img_tags:
            self.use_clarifai = False
        elif tags:
            self.clarifai_img_tags.append((tags, comment, comments))
            self.clarifai_img_tags_skip = tags_skip


        return self


    def follow_commenters(self, usernames, amount=10, daysold=365, max_pic=50, sleep_delay=600, interact=False):
        """ Follows users' commenters """
        self.logger.info ("Starting to follow commenters..")

        if not isinstance(usernames, list):
            usernames = [usernames]

        followed_all = 0
        followed_new = 0
        relax_point = random.randint(7, 14)   # you can use some plain value `10` instead of this quitely randomized score

        for username in usernames:
            self.logger.info("Following commenters of '{}' from pictures in last {} days...\nScrapping wall..".format(username, daysold))
            commenters = extract_information(self.browser, username, daysold, max_pic)

            if len(commenters)>0:  
                self.logger.info("Going to follow top {} users.\n".format(amount))
                sleep(1)
                # This way of iterating will prevent sleep interference between functions
                random.shuffle(commenters)
                for commenter in commenters[:amount] :
                    followed = self.follow_by_list(commenter, self.follow_times, sleep_delay, interact)
                    if followed > 0:
                        followed_all += 1
                        followed_new += 1
                        self.logger.info('Total Follow: {}'.format(str(followed_all)))
                        # Take a break after a good following
                        if followed_new >= relax_point:
                            delay_random = random.randint(ceil(sleep_delay*0.85), ceil(sleep_delay*1.14))
                            self.logger.info('------=>  Followed {} new users ~sleeping about {}'.format(followed_new,
                                                                        '{} seconds'.format(delay_random) if delay_random < 60 else
                                                                        '{} minutes'.format(float("{0:.2f}".format(delay_random/60)))))
                            sleep(delay_random)
                            relax_point = random.randint(7, 14)
                            followed_new = 0
                            pass

            else:
                self.logger.info("Noone commented, noone to follow.\n")

            sleep(1)

        self.logger.info("Finished following commenters!\n")

        return self


    def follow_likers (self, usernames, photos_grab_amount=3, follow_likers_per_photo=3, randomize=True, sleep_delay=600, interact=False):
        """ Follows users' likers """
        self.logger.info("Starting to follow likers..")

        if not isinstance(usernames, list):
            usernames = [usernames]

        if photos_grab_amount>12:
            self.logger.info("Sorry, you can only grab likers from first 12 photos for given username now.\n")
            photos_grab_amount = 12

        followed_all = 0
        followed_new = 0
        relax_point = random.randint(7, 14)   # you can use some plain value `10` instead of this quitely randomized score

        for username in usernames:
            photo_urls = get_photo_urls_from_profile(self.browser, username, photos_grab_amount, randomize)
            sleep(1)
            if not isinstance(photo_urls, list):
                photo_urls = [photo_urls]

            for photo_url in photo_urls:
                likers = users_liked(self.browser, photo_url, follow_likers_per_photo)
                # This way of iterating will prevent sleep interference between functions
                random.shuffle(likers)

                for liker in likers[:follow_likers_per_photo] :
                    followed = self.follow_by_list(liker, self.follow_times, sleep_delay, interact)
                    if followed > 0:
                        followed_all += 1
                        followed_new += 1
                        self.logger.info('Total Follow: {}'.format(str(followed_all)))
                        # Take a break after a good following
                        if followed_new >= relax_point:
                            delay_random = random.randint(ceil(sleep_delay*0.85), ceil(sleep_delay*1.14))
                            self.logger.info('------=>  Followed {} new users ~sleeping about {}'.format(followed_new,
                                                                        '{} seconds'.format(delay_random) if delay_random < 60 else
                                                                        '{} minutes'.format(float("{0:.2f}".format(delay_random/60)))))
                            sleep(delay_random)
                            relax_point = random.randint(7, 14)
                            followed_new=0
                            pass

        self.logger.info("Finished following likers!\n")    

        return self


    def follow_by_list(self, followlist, times=1, sleep_delay=600, interact=False): 
        """Allows to follow by any scrapped list"""
        if not isinstance(followlist, list):
            followlist = [followlist]
        
        self.follow_times = times or 0
        if self.aborting:
            self.logger.info(">>> self aborting prevented")
            #return self

        followed_all = 0
        followed_new = 0
        not_valid_users = 0
        relax_point = random.randint(7, 14)   # you can use some plain value `10` instead of this quitely randomized score

        for acc_to_follow in followlist:
            # Verify if the user should be followed
            validation, details = validate_username(self.browser,
                                           acc_to_follow,
                                           self.username,
                                           self.ignore_users,
                                           self.blacklist,
                                           self.potency_ratio,
                                           self.delimit_by_numbers,
                                           self.max_followers,
                                           self.max_following,
                                           self.min_followers,
                                           self.min_following,
                                           self.logger)
            if validation != True or acc_to_follow==self.username:
                self.logger.info(details)
                not_valid_users += 1
                continue

            # Take a break after a good following
            if followed_new >= relax_point:
                delay_random = random.randint(ceil(sleep_delay*0.85), ceil(sleep_delay*1.14))
                self.logger.info('Followed {} new users ~sleeping about {}'.format(followed_new,
                                                            '{} seconds'.format(delay_random) if delay_random < 60 else
                                                            '{} minutes'.format(float("{0:.2f}".format(delay_random/60)))))
                sleep(delay_random)
                followed_new = 0
                relax_point = random.randint(7, 14)
                pass

            if self.follow_restrict.get(acc_to_follow, 0) < self.follow_times:
                followed = follow_given_user(self.browser,
                                              self.username,
                                              acc_to_follow,
                                              self.follow_restrict,
                                              self.blacklist,
                                              self.logger,
                                              self.logfolder)
                sleep(random.randint(1, 3))

                if followed:
                    self.followed += 1
                    followed_all += 1
                    followed_new += 1
                    if len(followlist) > 1:   #print only for multiple follows, the others has own printers
                        self.logger.info('Total Follow: {}'.format(str(followed_all)))

                    # Check if interaction is expected
                    if interact and self.do_like: 
                        do_interact = random.randint(0, 100) <= self.user_interact_percentage
                        # Do interactions if any
                        if do_interact and self.user_interact_amount>0:
                            interaction_user = [acc_to_follow]
                            original_do_follow = self.do_follow   # store the original value of `self.do_follow`
                            self.do_follow = False   # disable following temporarily cos the user is already followed above
                            self.interact_by_users(interaction_user,
                                                     self.user_interact_amount,
                                                      self.user_interact_random,
                                                        self.user_interact_media)
                            self.do_follow = original_do_follow   # revert back original `self.do_follow` value (either it was `False` or `True`)
            else:
                self.logger.info('---> {} has already been followed more than '
                                 '{} times'.format(
                                    acc_to_follow, str(self.follow_times)))
                sleep(1)

        self.not_valid_users += not_valid_users

        return followed_all


    def set_relationship_bounds (self,
                                  enabled=None,
                                   potency_ratio=None,
                                    delimit_by_numbers=None,
                                     max_followers=None,
                                      max_following=None, 
                                       min_followers=None, 
                                        min_following=None):
        """Sets the potency ratio and limits to the provide an efficient activity between the targeted masses"""
        self.potency_ratio = potency_ratio if enabled==True else None
        self.delimit_by_numbers = delimit_by_numbers if enabled==True else None
        
        self.max_followers = max_followers
        self.min_followers = min_followers
        
        self.max_following = max_following
        self.min_following = min_following



    def set_delimit_liking(self,
                            enabled=None,
                             max=None,
                              min=None):

        self.delimit_liking = True if enabled==True else False
        self.max_likes = max
        self.min_likes = min
        


    def set_delimit_commenting(self,
                                enabled=False,
                                 max=None,
                                  min=None):

        self.delimit_commenting = True if enabled==True else False
        self.max_comments = max
        self.min_comments = min



    def like_by_locations(self,
                          locations=None,
                          amount=50,
                          media=None,
                          skip_top_posts=True):
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

        for index, location in enumerate(locations):
            self.logger.info('Location [{}/{}]'
                             .format(index + 1, len(locations)))
            self.logger.info('--> {}'.format(location.encode('utf-8')))

            try:
                links = get_links_for_location(self.browser,
                                               location,
                                               amount,
                                               self.logger,
                                               media,
                                               skip_top_posts)
            except NoSuchElementException as exc:
                self.logger.warning("Error occured while getting images from location: {}  "
                                    "~maybe too few images exist\n\t{}\n".format(location, exc.encode("utf-8")))
                continue

            for i, link in enumerate(links):
                self.logger.info('[{}/{}]'.format(i + 1, len(links)))
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason, scope = (
                        check_link(self.browser,
                                   link,
                                   self.dont_like,
                                   self.ignore_if_contains,
                                   self.logger)
                    )

                    if not inappropriate and self.delimit_liking:
                        self.liking_approved = verify_liking(self.browser, self.max_likes, self.min_likes, self.logger)
                    
                    if not inappropriate and self.liking_approved:
                        #validate user
                        validation, details = validate_username(self.browser,
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
                                                       self.logger)
                        if validation != True:
                            self.logger.info(details)
                            not_valid_users += 1
                            continue
                        else:
                            web_adress_navigator(self.browser, link)

                        #try to like
                        liked = like_image(self.browser,
                                           user_name,
                                           self.blacklist,
                                           self.logger,
                                           self.logfolder)

                        if liked:
                            liked_img += 1
                            checked_img = True
                            temp_comments = []
                            commenting = random.randint(
                                0, 100) <= self.comment_percentage
                            following = random.randint(
                                0, 100) <= self.follow_percentage

                            if self.use_clarifai and (following or commenting):
                                try:
                                    checked_img, temp_comments = (
                                        check_image(self.browser,
                                                    self.clarifai_api_key,
                                                    self.clarifai_img_tags,
                                                    self.clarifai_img_tags_skip,
                                                    self.logger,
                                                    self.clarifai_full_match)
                                    )
                                except Exception as err:
                                    self.logger.error(
                                        'Image check error: {}'.format(err))

                            # comments
                            if (self.do_comment and
                                user_name not in self.dont_include and
                                checked_img and
                                    commenting):
                                
                                if self.delimit_commenting:
                                    self.commenting_approved, disapproval_reason = verify_commenting(self.browser, self.max_comments, self.min_comments, self.logger)

                                if self.commenting_approved:
                                    if temp_comments:
                                        # Use clarifai related comments only!
                                        comments = temp_comments
                                    elif is_video:
                                        comments = (self.comments +
                                                    self.video_comments)
                                    else:
                                        comments = (self.comments +
                                                    self.photo_comments)
                                    commented += comment_image(self.browser,
                                                               user_name,
                                                               comments,
                                                               self.blacklist,
                                                               self.logger,
                                                               self.logfolder)
                                else:
                                    self.logger.info(disapproval_reason)
                            else:
                                self.logger.info('--> Not commented')
                                sleep(1)

                            # following
                            if (self.do_follow and
                                user_name not in self.dont_include and
                                checked_img and
                                following and
                                self.follow_restrict.get(user_name, 0) <
                                    self.follow_times):

                                followed += follow_user(self.browser,
                                                        self.follow_restrict,
                                                        self.username,
                                                        user_name,
                                                        self.blacklist,
                                                        self.logger,
                                                        self.logfolder)

                            else:
                                self.logger.info('--> Not following')
                                sleep(1)
                        else:
                            already_liked += 1
                    else:
                        self.logger.info(
                            '--> Image not liked: {}'.format(reason.encode('utf-8')))
                        inap_img += 1
                except NoSuchElementException as err:
                    self.logger.error('Invalid Page: {}'.format(err))

        self.logger.info('Liked: {}'.format(liked_img))
        self.logger.info('Already Liked: {}'.format(already_liked))
        self.logger.info('Commented: {}'.format(commented))
        self.logger.info('Followed: {}'.format(followed))
        self.logger.info('Inappropriate: {}'.format(inap_img))
        self.logger.info('Not valid users: {}\n'.format(not_valid_users))

        self.followed += followed
        self.liked_img += liked_img
        self.already_liked += already_liked
        self.commented += commented
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return self

    def comment_by_locations(self,
                      locations=None,
                      amount=50,
                      media=None,
                      skip_top_posts=True):
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

        for index, location in enumerate(locations):
            self.logger.info('Location [{}/{}]'
                             .format(index + 1, len(locations)))
            self.logger.info('--> {}'.format(location.encode('utf-8')))

            try:
                links = get_links_for_location(self.browser,
                                               location,
                                               amount,
                                               self.logger,
                                               media,
                                               skip_top_posts)
            except NoSuchElementException:
                self.logger.warning('Too few images, skipping this location')
                continue

            for i, link in enumerate(links):
                self.logger.info('[{}/{}]'.format(i + 1, len(links)))
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason, scope = (
                        check_link(self.browser,
                                   link,
                                   self.dont_like,
                                   self.ignore_if_contains,
                                   self.logger)
                    )

                    if not inappropriate:
                        #validate user
                        validation, details = validate_username(self.browser,
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
                                                       self.logger)
                        if validation != True:
                            self.logger.info(details)
                            not_valid_users += 1
                            continue
                        else:
                            web_adress_navigator(self.browser, link)

                        #try to comment
                        liked = True

                        self.logger.info('--> Image not liked: Likes are disabled for method \'comment_by_locations\'')

                        if liked:
                            liked_img += 1
                            checked_img = True
                            temp_comments = []
                            commenting = random.randint(
                                0, 100) <= self.comment_percentage
                            following = random.randint(
                                0, 100) <= self.follow_percentage

                            if self.use_clarifai and (following or commenting):
                                try:
                                    checked_img, temp_comments = (
                                        check_image(self.browser,
                                                    self.clarifai_api_key,
                                                    self.clarifai_img_tags,
                                                    self.clarifai_img_tags_skip,
                                                    self.logger,
                                                    self.clarifai_full_match)
                                    )
                                except Exception as err:
                                    self.logger.error(
                                        'Image check error: {}'.format(err))


                            if (self.do_comment and
                                user_name not in self.dont_include and
                                checked_img and
                                    commenting):

                                if self.delimit_commenting:
                                    self.commenting_approved, disapproval_reason = verify_commenting(self.browser, self.max_comments, self.min_comments, self.logger)

                                if self.commenting_approved:
                                    if temp_comments:
                                        # Use clarifai related comments only!
                                        comments = temp_comments
                                    elif is_video:
                                        comments = (self.comments +
                                                    self.video_comments)
                                    else:
                                        comments = (self.comments +
                                                    self.photo_comments)
                                    commented += comment_image(self.browser,
                                                               user_name,
                                                               comments,
                                                               self.blacklist,
                                                               self.logger,
                                                               self.logfolder)
                                else:
                                    self.logger.info(disapproval_reason)
                            else:
                                self.logger.info('--> Not commented')
                                sleep(1)

                            if (self.do_follow and
                                user_name not in self.dont_include and
                                checked_img and
                                following and
                                self.follow_restrict.get(user_name, 0) <
                                    self.follow_times):

                                followed += follow_user(self.browser,
                                                        self.follow_restrict,
                                                        self.username,
                                                        user_name,
                                                        self.blacklist,
                                                        self.logger,
                                                        self.logfolder)

                            else:
                                self.logger.info('--> Not following')
                                sleep(1)
                        else:
                            already_liked += 1
                    else:
                        self.logger.info(
                            '--> Image not liked: {}'.format(reason.encode('utf-8')))
                        inap_img += 1
                except NoSuchElementException as err:
                    self.logger.error('Invalid Page: {}'.format(err))

        self.logger.info('Liked: {}'.format(liked_img))
        self.logger.info('Already Liked: {}'.format(already_liked))
        self.logger.info('Commented: {}'.format(commented))
        self.logger.info('Followed: {}'.format(followed))
        self.logger.info('Inappropriate: {}'.format(inap_img))
        self.logger.info('Not valid users: {}\n'.format(not_valid_users))

        self.followed += followed
        self.not_valid_users += not_valid_users

        return self

    def like_by_tags(self,
                     tags=None,
                     amount=50,
                     media=None,
                     skip_top_posts=True,
                     use_smart_hashtags=False,
                     interact=False):
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
        if use_smart_hashtags is True and self.smart_hashtags is not []:
            print('Using smart hashtags')
            tags = self.smart_hashtags

        # deletes white spaces in tags
        tags = [tag.strip() for tag in tags]

        tags = tags or []

        for index, tag in enumerate(tags):
            self.logger.info('Tag [{}/{}]'.format(index + 1, len(tags)))
            self.logger.info('--> {}'.format(tag.encode('utf-8')))

            try:
                links = get_links_for_tag(self.browser,
                                          tag,
                                          amount,
                                          self.logger,
                                          media,
                                          skip_top_posts)
            except NoSuchElementException:
                self.logger.info('Too few images, skipping this tag')
                continue

            for i, link in enumerate(links):
                self.logger.info('[{}/{}]'.format(i + 1, len(links)))
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason, scope = (
                        check_link(self.browser,
                                   link,
                                   self.dont_like,
                                   self.ignore_if_contains,
                                   self.logger)
                    )

                    if not inappropriate and self.delimit_liking:
                        self.liking_approved = verify_liking(self.browser, self.max_likes, self.min_likes, self.logger)

                    if not inappropriate and self.liking_approved:
                        #validate user
                        validation, details = validate_username(self.browser,
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
                                                       self.logger)
                        if validation != True:
                            self.logger.info(details)
                            not_valid_users += 1
                            continue
                        else:
                            web_adress_navigator(self.browser, link)

                        #try to like
                        liked = like_image(self.browser,
                                           user_name,
                                           self.blacklist,
                                           self.logger,
                                           self.logfolder)

                        if liked:

                            if interact:
                                username = (self.browser.
                                    find_element_by_xpath(
                                        '//article/header/div[2]/'
                                        'div[1]/div/a'))

                                username = username.get_attribute("title")
                                name = []
                                name.append(username)

                                self.logger.info(
                                    '--> User followed: {}'
                                    .format(name))
                                self.like_by_users(
                                    name,
                                    self.user_interact_amount,
                                    self.user_interact_random,
                                    self.user_interact_media)

                            liked_img += 1
                            checked_img = True
                            temp_comments = []
                            commenting = (random.randint(0, 100) <=
                                          self.comment_percentage)
                            following = (random.randint(0, 100) <=
                                         self.follow_percentage)

                            if self.use_clarifai and (following or commenting):
                                try:
                                    checked_img, temp_comments = (
                                        check_image(self.browser,
                                                    self.clarifai_api_key,
                                                    self.clarifai_img_tags,
                                                    self.clarifai_img_tags_skip,
                                                    self.logger,
                                                    self.clarifai_full_match)
                                    )
                                except Exception as err:
                                    self.logger.error(
                                        'Image check error: {}'.format(err))


                            if (self.do_comment and
                                user_name not in self.dont_include and
                                checked_img and
                                    commenting):
                                
                                if self.delimit_commenting:
                                    self.commenting_approved, disapproval_reason = verify_commenting(self.browser, self.max_comments, self.min_comments, self.logger)

                                if self.commenting_approved:
                                    if temp_comments:
                                        # Use clarifai related comments only!
                                        comments = temp_comments
                                    elif is_video:
                                        comments = (self.comments +
                                                    self.video_comments)
                                    else:
                                        comments = (self.comments +
                                                    self.photo_comments)
                                    commented += comment_image(self.browser,
                                                               user_name,
                                                               comments,
                                                               self.blacklist,
                                                               self.logger,
                                                               self.logfolder)
                                else:
                                    self.logger.info(disapproval_reason)
                            else:
                                self.logger.info('--> Not commented')
                                sleep(1)

                            if (self.do_follow and
                                user_name not in self.dont_include and
                                checked_img and
                                following and
                                self.follow_restrict.get(user_name, 0) <
                                    self.follow_times):

                                followed += follow_user(self.browser,
                                                        self.follow_restrict,
                                                        self.username,
                                                        user_name,
                                                        self.blacklist,
                                                        self.logger,
                                                        self.logfolder)
                            else:
                                self.logger.info('--> Not following')
                                sleep(1)
                        else:
                            already_liked += 1
                    else:
                        self.logger.info(
                            '--> Image not liked: {}'.format(reason.encode('utf-8')))
                        inap_img += 1
                except NoSuchElementException as err:
                    self.logger.error('Invalid Page: {}'.format(err))

        self.logger.info('Liked: {}'.format(liked_img))
        self.logger.info('Already Liked: {}'.format(already_liked))
        self.logger.info('Commented: {}'.format(commented))
        self.logger.info('Followed: {}'.format(followed))
        self.logger.info('Inappropriate: {}'.format(inap_img))
        self.logger.info('Not valid users: {}\n'.format(not_valid_users))

        self.liked_img += liked_img
        self.already_liked += already_liked
        self.commented += commented
        self.followed += followed
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return self

    def like_by_users(self, usernames, amount=10, randomize=False, media=None):
        """Likes some amounts of images for each usernames"""
        if self.aborting:
            return self

        liked_img = 0
        total_liked_img = 0
        already_liked = 0
        inap_img = 0
        commented = 0
        followed = 0
        not_valid_users = 0
        usernames = usernames or []

        for index, username in enumerate(usernames):

            self.logger.info(
                'Username [{}/{}]'.format(index + 1, len(usernames)))
            self.logger.info('--> {}'.format(username.encode('utf-8')))
            following = random.randint(0, 100) <= self.follow_percentage

            validation, details = validate_username(self.browser,
                                           username,
                                           self.username,
                                           self.ignore_users,
                                           self.blacklist,
                                           self.potency_ratio,
                                           self.delimit_by_numbers,
                                           self.max_followers,
                                           self.max_following,
                                           self.min_followers,
                                           self.min_following,
                                           self.logger)
            if validation != True:
                self.logger.info(details)
                not_valid_users += 1
                continue

            try:
                links = get_links_for_username(
                    self.browser,
                    username,
                    amount,
                    self.logger,
                    randomize,
                    media)
            except NoSuchElementException:
                self.logger.error('Element not found, skipping this username')
                continue

            if (self.do_follow and
                username not in self.dont_include and
                following and
                    self.follow_restrict.get(username, 0) < self.follow_times):
                followed += follow_user(self.browser,
                                        self.follow_restrict,
                                        self.username,
                                        username,
                                        self.blacklist,
                                        self.logger,
                                        self.logfolder)
            else:
                self.logger.info('--> Not following')
                sleep(1)

            if links is False:
                continue

            # Reset like counter for every username
            liked_img = 0

            for i, link in enumerate(links):
                # Check if target has reached
                if liked_img >= amount:
                    self.logger.info('-------------')
                    self.logger.info("--> Total liked image reached it's "
                                     "amount given: {}".format(liked_img))
                    break

                self.logger.info('Post [{}/{}]'.format(liked_img + 1, amount))
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason, scope = (
                        check_link(self.browser,
                                   link,
                                   self.dont_like,
                                   self.ignore_if_contains,
                                   self.logger)
                    )

                    if not inappropriate and self.delimit_liking:
                        self.liking_approved = verify_liking(self.browser, self.max_likes, self.min_likes, self.logger)

                    if not inappropriate and self.liking_approved:
                        liked = like_image(self.browser,
                                           user_name,
                                           self.blacklist,
                                           self.logger,
                                           self.logfolder)

                        if liked:
                            total_liked_img += 1
                            liked_img += 1
                            checked_img = True
                            temp_comments = []
                            commenting = random.randint(
                                0, 100) <= self.comment_percentage

                            if self.use_clarifai and (following or commenting):
                                try:
                                    checked_img, temp_comments = (
                                        check_image(self.browser,
                                                    self.clarifai_api_key,
                                                    self.clarifai_img_tags,
                                                    self.clarifai_img_tags_skip,
                                                    self.logger,
                                                    self.clarifai_full_match)
                                    )
                                except Exception as err:
                                    self.logger.error(
                                        'Image check error: {}'.format(err))


                            if (self.do_comment and
                                user_name not in self.dont_include and
                                checked_img and
                                    commenting):

                                if self.delimit_commenting:
                                    self.commenting_approved, disapproval_reason = verify_commenting(self.browser, self.max_comments, self.min_comments, self.logger)

                                if self.commenting_approved:
                                    if temp_comments:
                                        # use clarifai related comments only!
                                        comments = temp_comments
                                    elif is_video:
                                        comments = (self.comments +
                                                    self.video_comments)
                                    else:
                                        comments = (self.comments +
                                                    self.photo_comments)
                                    commented += comment_image(self.browser,
                                                               user_name,
                                                               comments,
                                                               self.blacklist,
                                                               self.logger,
                                                               self.logfolder)
                                else:
                                    self.logger.info(disapproval_reason)

                            else:
                                self.logger.info('--> Not commented')
                                sleep(1)

                        else:
                            already_liked += 1

                    else:
                        self.logger.info(
                            '--> Image not liked: {}'.format(reason.encode('utf-8')))
                        inap_img += 1
                except NoSuchElementException as err:
                    self.logger.error('Invalid Page: {}'.format(err))

            if liked_img < amount:
                self.logger.info('-------------')
                self.logger.info("--> Given amount not fullfilled, "
                                 "image pool reached its end\n")

        self.logger.info('Liked: {}'.format(total_liked_img))
        self.logger.info('Already Liked: {}'.format(already_liked))
        self.logger.info('Commented: {}'.format(commented))
        self.logger.info('Inappropriate: {}'.format(inap_img))
        self.logger.info('Not valid users: {}\n'.format(not_valid_users))

        self.liked_img += liked_img
        self.already_liked += already_liked
        self.commented += commented
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return self

    def interact_by_users(self,
                          usernames,
                          amount=10,
                          randomize=False,
                          media=None):
        """Likes some amounts of images for each usernames"""
        if self.aborting:
            return self

        total_liked_img = 0
        already_liked = 0
        inap_img = 0
        commented = 0
        followed = 0
        not_valid_users = 0

        usernames = usernames or []

        for index, username in enumerate(usernames):
            self.logger.info(
                'Username [{}/{}]'.format(index + 1, len(usernames)))
            self.logger.info('--> {}'.format(username.encode('utf-8')))
            
            validation, details = validate_username(self.browser,
                                           username,
                                           self.username,
                                           self.ignore_users,
                                           self.blacklist,
                                           self.potency_ratio,
                                           self.delimit_by_numbers,
                                           self.max_followers,
                                           self.max_following,
                                           self.min_followers,
                                           self.min_following,
                                           self.logger)
            if validation != True:
                self.logger.info(details)
                not_valid_users += 1
                continue

            try:
                links = get_links_for_username(self.browser,
                                               username,
                                               amount,
                                               self.logger,
                                               randomize,
                                               media)
            except NoSuchElementException:
                self.logger.error('Element not found, skipping this username')
                continue

            if links is False:
                continue

            # Reset like counter for every username
            liked_img = 0

            # Will we follow this user?
            following = random.randint(0, 100) <= self.follow_percentage

            for i, link in enumerate(links[:amount]):
                # Check if target has reached
                if liked_img >= amount:
                    self.logger.info('-------------')
                    self.logger.info("--> Total liked image reached it's "
                                     "amount given: {}".format(liked_img))
                    break

                self.logger.info('Post [{}/{}]'.format(liked_img + 1, amount))
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason, scope = (
                        check_link(self.browser,
                                   link,
                                   self.dont_like,
                                   self.ignore_if_contains,
                                   self.logger)
                    )

                    if not inappropriate:

                        if (self.do_follow and
                            username not in self.dont_include and
                            following and
                            self.follow_restrict.get(
                                username, 0) < self.follow_times):

                            followed += follow_user(
                                self.browser,
                                self.follow_restrict,
                                self.username,
                                username,
                                self.blacklist,
                                self.logger,
                                self.logfolder)

                            following = False
                        else:
                            self.logger.info('--> Not following')
                            sleep(1)

                        liking = random.randint(0, 100) <= self.like_percentage
                        
                        if self.do_like and liking and self.delimit_liking:
                            self.liking_approved = verify_liking(self.browser, self.max_likes, self.min_likes, self.logger)
                        
                        if self.do_like and liking and self.liking_approved:
                            liked = like_image(self.browser,
                                               user_name,
                                               self.blacklist,
                                               self.logger,
                                               self.logfolder)
                        else:
                            liked = True

                        if liked:
                            total_liked_img += 1
                            liked_img += 1
                            checked_img = True
                            temp_comments = []
                            commenting = random.randint(
                                0, 100) <= self.comment_percentage

                            if self.use_clarifai and (following or commenting):
                                try:
                                    checked_img, temp_comments = (
                                        check_image(self.browser,
                                                    self.clarifai_api_key,
                                                    self.clarifai_img_tags,
                                                    self.clarifai_img_tags_skip,
                                                    self.logger,
                                                    self.clarifai_full_match)
                                    )
                                except Exception as err:
                                    self.logger.error(
                                        'Image check error: {}'.format(err))

                            if (self.do_comment and
                                user_name not in self.dont_include and
                                checked_img and
                                    commenting):

                                if self.delimit_commenting:
                                    self.commenting_approved, disapproval_reason = verify_commenting(self.browser, self.max_comments, self.min_comments, self.logger)

                                if self.commenting_approved:
                                    if temp_comments:
                                        # use clarifai related comments only!
                                        comments = temp_comments
                                    elif is_video:
                                        comments = (self.comments +
                                                    self.video_comments)
                                    else:
                                        comments = (self.comments +
                                                    self.photo_comments)
                                    commented += comment_image(self.browser,
                                                               user_name,
                                                               comments,
                                                               self.blacklist,
                                                               self.logger,
                                                               self.logfolder)
                                else:
                                    self.logger.info(disapproval_reason)
                            else:
                                self.logger.info('--> Not commented')
                                sleep(1)
                        else:
                            already_liked += 1

                    else:
                        self.logger.info(
                            '--> Image not liked: {}'.format(reason.encode('utf-8')))
                        inap_img += 1
                except NoSuchElementException as err:
                    self.logger.info('Invalid Page: {}'.format(err))

            if liked_img < amount:
                self.logger.info('-------------')
                self.logger.info("--> Given amount not fullfilled, image pool "
                                 "reached its end\n")

        self.logger.info('Liked: {}'.format(total_liked_img))
        self.logger.info('Already Liked: {}'.format(already_liked))
        self.logger.info('Commented: {}'.format(commented))
        self.logger.info('Inappropriate: {}'.format(inap_img))
        self.logger.info('Not valid users: {}\n'.format(not_valid_users))

        self.liked_img += total_liked_img
        self.already_liked += already_liked
        self.commented += commented
        self.followed += followed
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return self

    def like_from_image(self, url, amount=50, media=None):
        """Gets the tags from an image and likes 50 images for each tag"""
        if self.aborting:
            return self

        try:
            if not url:
                urls = self.browser.find_elements_by_xpath(
                    "//main//article//div//div[1]//div[1]//a[1]")
                url = urls[0].get_attribute("href")
                self.logger.info("new url {}".format(url))
            tags = get_tags(self.browser, url)
            self.logger.info(tags)
            self.like_by_tags(tags, amount, media)
        except TypeError as err:
            self.logger.error('Sorry, an error occured: {}'.format(err))
            self.aborting = True
            return self

        return self

    def interact_user_followers(self, usernames, amount=10, randomize=False):

        if self.do_follow != True and self.do_like != True:
            self.logger.info("Please enable following or liking in settings in order to do interactions.")
            return self
        elif self.user_interact_amount <= 0:
            self.logger.info("Please choose an amount higher than zero in `set_user_interact` in order to do interactions.")
            return self

        if not isinstance(usernames, list):
            usernames = [usernames]

        interacted_all = 0
        simulated_unfollow = 0
        not_valid_users = 0

        for index, user in enumerate(usernames):
            self.logger.info("User '{}' [{}/{}]".format((user), index+1, len(usernames)))
            try:
                person_list, simulated_list = get_given_user_followers(self.browser,
                                                                        self.username,
                                                                        user,
                                                                        amount,
                                                                        self.dont_include,
                                                                        randomize,
                                                                        self.follow_restrict,
                                                                        self.blacklist,
                                                                        self.follow_times,
                                                                        self.logger,
                                                                        self.logfolder)
            except (TypeError, RuntimeWarning) as err:
                
                if isinstance(err, RuntimeWarning):
                    self.logger.warning(
                        u'Warning: {} , skipping to next user'.format(err))
                    continue
                
                else:
                    self.logger.error(
                        'Sorry, an error occured: {}'.format(err))
                    self.aborting = True
                    return self

            interacted_personal = 0
            
            for person in person_list:
                if person in simulated_list:
                    validation, details = validate_username(self.browser,
                               person,
                               self.username,
                               self.ignore_users,
                               self.blacklist,
                               self.potency_ratio,
                               self.delimit_by_numbers,
                               self.max_followers,
                               self.max_following,
                               self.min_followers,
                               self.min_following,
                               self.logger)
                    if validation != True:
                        self.logger.info(details)
                        not_valid_users += 1
                        simulated_unfollow += 1
                        self.logger.info("Simulated unfollow: {}  ~not valid user".format(simulated_unfollow))
                        unfollow_user(self.browser, self.username, person, self.logger, self.logfolder)
                        continue
                # Do interactions if any
                do_interact = random.randint(0, 100) <= self.user_interact_percentage
                if do_interact==False:
                    self.logger.info("Skipping user '{}' due to the interaction percentage of {}".format(person, self.user_interact_percentage))
                    continue
                else:
                    interacted_all += 1
                    interacted_personal += 1
                    self.logger.info('Interaction [{}/{}]  |  Total Interaction: {}'.format(interacted_personal, len(person_list), interacted_all))
                    interaction_user = [person]
                    self.interact_by_users(interaction_user,
                                             self.user_interact_amount,
                                              self.user_interact_random,
                                                self.user_interact_media)
                    sleep(1)

        self.logger.info(
            "--> Interacted total of {} people\n".format(interacted_all))

        self.not_valid_users += not_valid_users
        
        return self


    def interact_user_following(self, usernames, amount=10, randomize=False):

        if self.do_follow != True and self.do_like != True:
            self.logger.info("Please enable following or liking in settings in order to do interactions.")
            return self
        elif self.user_interact_amount <= 0:
            self.logger.info("Please choose an amount higher than zero in `set_user_interact` in order to do interactions.")
            return self

        if not isinstance(usernames, list):
            usernames = [usernames]

        interacted_all = 0
        simulated_unfollow = 0
        not_valid_users = 0

        for index, user in enumerate(usernames):
            self.logger.info("User '{}' [{}/{}]".format((user), index+1, len(usernames)))
            try:
                person_list, simulated_list = get_given_user_following(self.browser,
                                                                        self.username,
                                                                        user,
                                                                        amount,
                                                                        self.dont_include,
                                                                        randomize,
                                                                        self.follow_restrict,
                                                                        self.blacklist,
                                                                        self.follow_times,
                                                                        self.logger,
                                                                        self.logfolder)
            except (TypeError, RuntimeWarning) as err:
                
                if isinstance(err, RuntimeWarning):
                    self.logger.warning(
                        u'Warning: {} , skipping to next user'.format(err))
                    continue
                
                else:
                    self.logger.error(
                        'Sorry, an error occured: {}'.format(err))
                    self.aborting = True
                    return self

            interacted_personal = 0
            
            for person in person_list:
                if person in simulated_list:
                    validation, details = validate_username(self.browser,
                               person,
                               self.username,
                               self.ignore_users,
                               self.blacklist,
                               self.potency_ratio,
                               self.delimit_by_numbers,
                               self.max_followers,
                               self.max_following,
                               self.min_followers,
                               self.min_following,
                               self.logger)
                    if validation != True:
                        self.logger.info(details)
                        not_valid_users += 1
                        simulated_unfollow += 1
                        self.logger.info("Simulated unfollow: {}  ~not valid user".format(simulated_unfollow))
                        unfollow_user(self.browser, self.username, person, self.logger, self.logfolder)
                        continue
                # Do interactions if any
                do_interact = random.randint(0, 100) <= self.user_interact_percentage
                if do_interact==False:
                    self.logger.info("Skipping user '{}' due to the interaction percentage of {}".format(person, self.user_interact_percentage))
                    continue
                else:
                    interacted_all += 1
                    interacted_personal += 1
                    self.logger.info('Interaction [{}/{}]  |  Total Interaction: {}'.format(interacted_personal, len(person_list), interacted_all))
                    interaction_user = [person]
                    self.interact_by_users(interaction_user,
                                             self.user_interact_amount,
                                              self.user_interact_random,
                                                self.user_interact_media)
                    sleep(1)

        self.logger.info(
            "--> Interacted total of {} people\n".format(interacted_all))

        self.not_valid_users += not_valid_users

        return self


    def follow_user_followers(self,
                              usernames,
                              amount=10,
                              randomize=False,
                              interact=False,
                              sleep_delay=600):

        if not isinstance(usernames, list):
            usernames = [usernames]

        followed_all = 0
        followed_new = 0
        not_valid_users = 0
        relax_point = random.randint(7, 14)   # you can use some plain value `10` instead of this quitely randomized score

        for index, user in enumerate(usernames):
            
            self.logger.info("User '{}' [{}/{}]".format((user), index+1, len(usernames)))
            
            try:
                person_list, simulated_list = get_given_user_followers(self.browser,
                                                                        self.username,
                                                                        user,
                                                                        amount,
                                                                        self.dont_include,
                                                                        randomize,
                                                                        self.follow_restrict,
                                                                        self.blacklist,
                                                                        self.follow_times,
                                                                        self.logger,
                                                                        self.logfolder)

            except (TypeError, RuntimeWarning) as err:

                if isinstance(err, RuntimeWarning):
                    self.logger.warning(
                        u'Warning: {} , skipping to next user'.format(err))
                    continue
                
                else:
                    self.logger.error(
                        'Sorry, an error occured: {}'.format(err))
                    self.aborting = True
                    return self
            
            followed_personal = 0
            simulated_unfollow = 0
            
            for person in person_list:
                if person in simulated_list:
                    validation, details = validate_username(self.browser,
                               person,
                               self.username,
                               self.ignore_users,
                               self.blacklist,
                               self.potency_ratio,
                               self.delimit_by_numbers,
                               self.max_followers,
                               self.max_following,
                               self.min_followers,
                               self.min_following,
                               self.logger)
                    if validation != True:
                        self.logger.info(details)
                        not_valid_users += 1
                        simulated_unfollow += 1
                        self.logger.info("Simulated unfollow: {}  ~not valid user".format(simulated_unfollow))
                        unfollow_user(self.browser, self.username, person, self.logger, self.logfolder)
                        continue

                followed = self.follow_by_list(person, self.follow_times, sleep_delay, interact)
                sleep(1)

                if followed > 0:
                    followed_all += 1
                    followed_new += 1
                    followed_personal += 1
                    self.logger.info('Follow [{}/{}]  |  Total Follow: {}'.format(followed_personal, len(person_list), followed_all))
                    # Take a break after a good following
                    if followed_new >= relax_point:
                        delay_random = random.randint(ceil(sleep_delay*0.85), ceil(sleep_delay*1.14))
                        self.logger.info('------=>  Followed {} new users ~sleeping about {}'.format(followed_new,
                                                                    '{} seconds'.format(delay_random) if delay_random < 60 else
                                                                    '{} minutes'.format(float("{0:.2f}".format(delay_random/60)))))
                        sleep(delay_random)
                        relax_point = random.randint(7, 14)
                        followed_new=0
                        pass

        self.logger.info(
            "--> Followed total of {} people\n".format(followed_all))

        self.not_valid_users += not_valid_users

        return self


    def follow_user_following(self,
                              usernames,
                              amount=10,
                              randomize=False,
                              interact=False,
                              sleep_delay=600):

        if not isinstance(usernames, list):
            usernames = [usernames]

        followed_all = 0
        followed_new = 0
        not_valid_users = 0
        relax_point = random.randint(7, 14)   # you can use some plain value `10` instead of this quitely randomized score

        for index, user in enumerate(usernames):

            self.logger.info("User '{}' [{}/{}]".format((user), index+1, len(usernames)))

            try:
                person_list, simulated_list = get_given_user_followers(self.browser,
                                                                        self.username,
                                                                        user,
                                                                        amount,
                                                                        self.dont_include,
                                                                        randomize,
                                                                        self.follow_restrict,
                                                                        self.blacklist,
                                                                        self.follow_times,
                                                                        self.logger,
                                                                        self.logfolder)

            except (TypeError, RuntimeWarning) as err:
                
                if isinstance(err, RuntimeWarning):
                    self.logger.warning(
                        u'Warning: {} , skipping to next user'.format(err))
                    continue
                
                else:
                    self.logger.error(
                        'Sorry, an error occured: {}'.format(err))
                    self.aborting = True
                    return self
                    
            followed_personal = 0
            simulated_unfollow = 0
            
            for person in person_list:
                if person in simulated_list:
                    validation, details = validate_username(self.browser,
                               person,
                               self.username,
                               self.ignore_users,
                               self.blacklist,
                               self.potency_ratio,
                               self.delimit_by_numbers,
                               self.max_followers,
                               self.max_following,
                               self.min_followers,
                               self.min_following,
                               self.logger)
                    if validation != True:
                        self.logger.info(details)
                        not_valid_users += 1
                        simulated_unfollow += 1
                        self.logger.info("Simulated unfollow: {}  ~not valid user".format(simulated_unfollow))
                        unfollow_user(self.browser, self.username, person, self.logger, self.logfolder)
                        continue

                followed = self.follow_by_list(person, self.follow_times, sleep_delay, interact)
                sleep(1)

                if followed > 0:
                    followed_all += 1
                    followed_new += 1
                    followed_personal += 1
                    self.logger.info('Follow [{}/{}]  |  Total Follow: {}'.format(followed_personal, len(person_list), followed_all))
                    # Take a break after a good following
                    if followed_new >= relax_point:
                        delay_random = random.randint(ceil(sleep_delay*0.85), ceil(sleep_delay*1.14))
                        self.logger.info('------=>  Followed {} new users ~sleeping about {}'.format(followed_new,
                                                                    '{} seconds'.format(delay_random) if delay_random < 60 else
                                                                    '{} minutes'.format(float("{0:.2f}".format(delay_random/60)))))
                        sleep(delay_random)
                        relax_point = random.randint(7, 14)
                        followed_new=0
                        pass

        self.logger.info(
                "--> Followed total of {} people\n".format(followed_all))

        self.not_valid_users += not_valid_users

        return self


    def unfollow_users(self,
                       amount=10,
                       onlyInstapyFollowed=False,
                       onlyInstapyMethod='FIFO',
                       sleep_delay=600,
                       onlyNotFollowMe=False,
                       unfollow_after=None):

        if self.aborting:
            return self
        
        """Unfollows (default) 10 users from your following list"""
        self.logger.info(
            "--> unfollow_users, amount: {} ".format(amount))

        if unfollow_after is not None:
            if not python_version().startswith(('2.7', '3')):
                self.logger.warning("`unfollow_after` argument is not available for Python versions below 2.7")
                unfollow_after = None
        
        if onlyInstapyFollowed:
            self.automatedFollowedPool = set_automated_followed_pool(self.username,
                                                                     self.logger,
                                                                     self.logfolder,
                                                                     unfollow_after)

        try:
            unfollowNumber = unfollow(self.browser,
                                      self.username,
                                      amount,
                                      self.dont_include,
                                      onlyInstapyFollowed,
                                      onlyInstapyMethod,
                                      self.automatedFollowedPool,
                                      sleep_delay,
                                      onlyNotFollowMe,
                                      self.logger,
                                      self.logfolder)
            self.logger.info(
                "--> Total people unfollowed : {} ".format(unfollowNumber))
            self.unfollowNumber += unfollowNumber

        except (TypeError, RuntimeWarning) as err:
            if isinstance(err, RuntimeWarning):
                self.logger.error(
                    u'Warning: {} , stopping unfollow_users'.format(err))
                return self
            else:
                self.logger.error('Sorry, an error occured: {}'.format(err))
                self.aborting = True
                return self

        return self

    def like_by_feed(self, **kwargs):
        """Like the users feed"""
        for i in self.like_by_feed_generator(**kwargs):
            pass
        return self

    def like_by_feed_generator(self,
                     amount=50,
                     randomize=False,
                     unfollow=False,
                     interact=False):
        """Like the users feed"""

        if self.aborting:
            return

        liked_img = 0
        already_liked = 0
        inap_img = 0
        commented = 0
        followed = 0
        skipped_img = 0
        num_of_search = 0
        not_valid_users = 0
        history = []

        while liked_img < amount:
            try:
                # Gets another load of links to be tested
                links = get_links_from_feed(self.browser,
                                            amount,
                                            num_of_search,
                                            self.logger)
            except NoSuchElementException:
                self.logger.warning('Too few images, aborting')
                self.aborting = True
                return

            num_of_search += 1

            for i, link in enumerate(links):
                if liked_img == amount:
                    break
                if randomize and random.choice([True, False]):
                    self.logger.warning('Post Randomly Skipped...\n')
                    skipped_img += 1
                    continue
                else:
                    if link in history:
                        self.logger.info('This link has already '
                                         'been visited: {}'
                                         .format(link))
                        continue
                    else:
                        self.logger.info('New link found...')
                        history.append(link)
                        self.logger.info('[{} posts liked /{} amount]'
                                         .format(liked_img, amount))
                        self.logger.info(link)

                        try:
                            inappropriate, user_name, is_video, reason, scope = (
                                check_link(self.browser,
                                           link,
                                           self.dont_like,
                                           self.ignore_if_contains,
                                           self.logger)
                            )

                            if not inappropriate and self.delimit_liking:
                                self.liking_approved = verify_liking(self.browser, self.max_likes, self.min_likes, self.logger)

                            if not inappropriate and self.liking_approved:
                                #validate user
                                validation, details = validate_username(self.browser,
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
                                                               self.logger)
                                if validation != True:
                                    self.logger.info(details)
                                    not_valid_users += 1
                                    continue
                                else:
                                    web_adress_navigator(self.browser, link)

                                #try to like
                                liked = like_image(self.browser,
                                                   user_name,
                                                   self.blacklist,
                                                   self.logger,
                                                   self.logfolder)

                                if liked:
                                    username = (self.browser.
                                                find_element_by_xpath(
                                                    '//article/header/div[2]/'
                                                    'div[1]/div/a'))

                                    username = username.get_attribute("title")
                                    name = []
                                    name.append(username)

                                    if interact:
                                        self.logger.info(
                                            '--> User followed: {}'
                                            .format(name))
                                        self.like_by_users(
                                            name,
                                            self.user_interact_amount,
                                            self.user_interact_random,
                                            self.user_interact_media)

                                    liked_img += 1
                                    checked_img = True
                                    temp_comments = []
                                    commenting = random.randint(
                                        0, 100) <= self.comment_percentage
                                    following = random.randint(
                                        0, 100) <= self.follow_percentage

                                    if (self.use_clarifai and
                                            (following or commenting)):
                                        try:
                                            checked_img, temp_comments = (
                                                check_image(
                                                    self.browser,
                                                    self.clarifai_api_key,
                                                    self.clarifai_img_tags,
                                                    self.clarifai_img_tags_skip,
                                                    self.logger,
                                                    self.clarifai_full_match)
                                            )
                                        except Exception as err:
                                            self.logger.error(
                                                'Image check error:'
                                                ' {}'.format(err))


                                    if (self.do_comment and
                                        user_name not in self.dont_include and
                                            checked_img and
                                            commenting):
                                        if self.delimit_commenting:
                                            self.commenting_approved, disapproval_reason = verify_commenting(self.browser, self.max_comments, self.min_comments, self.logger)

                                        if self.commenting_approved:
                                            if temp_comments:
                                                # use clarifai related
                                                # comments only!
                                                comments = temp_comments
                                            elif is_video:
                                                comments = (
                                                    self.comments +
                                                    self.video_comments)
                                            else:
                                                comments = (
                                                    self.comments +
                                                    self.photo_comments)
                                            commented += comment_image(
                                                            self.browser,
                                                            user_name,
                                                            comments,
                                                            self.blacklist,
                                                            self.logger,
                                                            self.logfolder)
                                        else:
                                            self.logger.info(disapproval_reason)
                                    else:
                                        self.logger.info('--> Not commented')
                                        sleep(1)

                                    if (self.do_follow and
                                        user_name not in self.dont_include and
                                        checked_img and
                                        following and
                                        self.follow_restrict.get(
                                            user_name, 0) < self.follow_times):
                                        followed += follow_user(
                                            self.browser,
                                            self.follow_restrict,
                                            self.username,
                                            user_name,
                                            self.blacklist,
                                            self.logger,
                                            self.logfolder)
                                    else:
                                        self.logger.info('--> Not following')
                                        sleep(1)

                                    yield self
                                else:
                                    already_liked += 1
                            else:
                                self.logger.info(
                                    '--> Image not liked: {}'.format(reason.encode('utf-8')))
                                inap_img += 1
                                if reason == 'Inappropriate' and unfollow:
                                    unfollow_user(self.browser, self.username, user_name, self.logger, self.logfolder)
                        except NoSuchElementException as err:
                            self.logger.error('Invalid Page: {}'.format(err))

        self.logger.info('Liked: {}'.format(liked_img))
        self.logger.info('Already Liked: {}'.format(already_liked))
        self.logger.info('Commented: {}'.format(commented))
        self.logger.info('Followed: {}'.format(followed))
        self.logger.info('Inappropriate: {}'.format(inap_img))
        self.logger.info('Not valid users: {}'.format(not_valid_users))
        self.logger.info('Randomly Skipped: {}\n'.format(skipped_img))

        self.liked_img += liked_img
        self.already_liked += already_liked
        self.commented += commented
        self.followed += followed
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return

    def set_dont_unfollow_active_users(self, enabled=False, posts=4, boundary=500):
        """Prevents unfollow followers who have liked one of
        your latest X posts"""

        # do nothing
        if not enabled:
            return

        # list of users who liked our media
        active_users = get_active_users(self.browser,
                                        self.username,
                                        posts,
                                        boundary,
                                        self.logger)

        for user in active_users:
            # include active user to not unfollow list
            self.dont_include.append(user)

    def set_blacklist(self, enabled, campaign):
        """Enable/disable blacklist. If enabled, adds users to a blacklist after
        interact with and adds users to dont_include list"""

        if enabled is False:
            return

        self.blacklist['enabled'] = True
        self.blacklist['campaign'] = campaign

        try:
            with open('{}blacklist.csv'.format(self.logfolder), 'r') as blacklist:
                reader = csv.DictReader(blacklist)
                for row in reader:
                    if row['campaign'] == campaign:
                        self.dont_include.append(row['username'])
        except:
            self.logger.info('Campaign {} first run'.format(campaign))

    def end(self):
        """Closes the current session"""
        dump_follow_restriction(self.follow_restrict, self.logfolder)

        try:
            self.browser.delete_all_cookies()
            self.browser.quit()
        except WebDriverException as exc:
            self.logger.warning('Could not locate Chrome: {}'.format(exc))

        if self.nogui:
            self.display.stop()

        self.logger.info('Session ended - {}'.format(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.logger.info('-' * 20 + '\n\n')

        with open('{}followed.txt'.format(self.logfolder), 'w') as followFile:
            followFile.write(str(self.followed))

    def follow_by_tags(self,
                     tags=None,
                     amount=50,
                     media=None,
                     skip_top_posts=True,
                     use_smart_hashtags=False):
        if self.aborting:
            return self

        inap_img = 0
        followed = 0
        not_valid_users = 0

        # if smart hashtag is enabled
        if use_smart_hashtags is True and self.smart_hashtags is not []:
            print('Using smart hashtags')
            tags = self.smart_hashtags

        # deletes white spaces in tags
        tags = [tag.strip() for tag in tags]

        tags = tags or []

        for index, tag in enumerate(tags):
            self.logger.info('Tag [{}/{}]'.format(index + 1, len(tags)))
            self.logger.info('--> {}'.format(tag.encode('utf-8')))

            try:
                links = get_links_for_tag(self.browser,
                                          tag,
                                          amount,
                                          self.logger,
                                          media,
                                          skip_top_posts)
            except NoSuchElementException:
                self.logger.info('Too few images, skipping this tag')
                continue

            for i, link in enumerate(links):
                self.logger.info('[{}/{}]'.format(i + 1, len(links)))
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason, scope = (
                        check_link(self.browser,
                                   link,
                                   self.dont_like,
                                   self.ignore_if_contains,
                                   self.logger)
                    )

                    if not inappropriate:
                        #validate user
                        validation, details = validate_username(self.browser,
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
                                                       self.logger)
                        if validation != True:
                            self.logger.info(details)
                            not_valid_users += 1
                            continue
                        else:
                            web_adress_navigator(self.browser, link)

                        #try to follow
                        followed += follow_user(self.browser,
                                                self.follow_restrict,
                                                self.username,
                                                user_name,
                                                self.blacklist,
                                                self.logger,
                                                self.logfolder)
                    else:
                        self.logger.info(
                            '--> User not followed: {}'.format(reason))
                        inap_img += 1
                except NoSuchElementException as err:
                    self.logger.error('Invalid Page: {}'.format(err))

        self.logger.info('Followed: {}'.format(followed))
        self.logger.info('Inappropriate: {}'.format(inap_img))
        self.logger.info('Not valid users: {}\n'.format(not_valid_users))

        self.followed += followed
        self.inap_img += inap_img
        self.not_valid_users += not_valid_users

        return self
