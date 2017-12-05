"""OS Modules environ method to get the setup vars from the Environment"""
import csv
import json
import logging
from math import ceil
import os
from datetime import datetime
from sys import maxsize
import random

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import DesiredCapabilities
import requests

from .clarifai_util import check_image
from .comment_util import comment_image
from .like_util import check_link
from .like_util import get_links_for_tag
from .like_util import get_links_from_feed
from .like_util import get_tags
from .like_util import get_links_for_location
from .like_util import like_image
from .like_util import get_links_for_username
from .login_util import login_user
from .print_log_writer import log_follower_num
from .time_util import sleep
from .time_util import set_sleep_percentage
from .util import get_active_users
from .util import getFollowerList
from .util import validate_username
from .unfollow_util import get_given_user_followers
from .unfollow_util import get_given_user_following
from .unfollow_util import unfollow
from .unfollow_util import unfollow_user
from .unfollow_util import follow_given_user_followers
from .unfollow_util import follow_given_user_following
from .unfollow_util import follow_user
from .unfollow_util import follow_given_user
from .unfollow_util import load_follow_restriction
from .unfollow_util import dump_follow_restriction
from .unfollow_util import set_automated_followed_pool


class InstaPy:
    """Class to be instantiated to use the script"""

    def __init__(self,
                 username=None,
                 password=None,
                 nogui=False,
                 selenium_local_session=True,
                 use_firefox=False,
                 page_delay=25,
                 show_logs=True,
                 headless_browser=False):

        if nogui:
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()

        self.browser = None
        self.headless_browser = headless_browser

        self.username = username or os.environ.get('INSTA_USER')
        self.password = password or os.environ.get('INSTA_PW')
        self.nogui = nogui

        self.page_delay = page_delay
        self.switch_language = True
        self.use_firefox = use_firefox
        self.firefox_profile_path = None

        self.do_comment = False
        self.comment_percentage = 0
        self.comments = ['Cool!', 'Nice!', 'Looks good!']
        self.photo_comments = []
        self.video_comments = []

        self.followed = 0
        self.follow_restrict = load_follow_restriction()
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
        self.clarifai_full_match = False

        self.like_by_followers_upper_limit = 0
        self.like_by_followers_lower_limit = 0

        self.aborting = False

        # initialize and setup logging system
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('./logs/general.log')
        file_handler.setLevel(logging.DEBUG)
        logger_formatter = logging.Formatter('%(levelname)s - %(message)s')
        file_handler.setFormatter(logger_formatter)
        if (self.logger.hasHandlers()):
            self.logger.handlers.clear()
        self.logger.addHandler(file_handler)

        if show_logs is True:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(logger_formatter)
            self.logger.addHandler(console_handler)

        if selenium_local_session:
            self.set_selenium_local_session()

        if os.name == 'nt':
            error_msg = ('Sorry, Record Activity is not working on Windows. '
                         'We\'re working to fix this soon!')
            self.logger.critical(error_msg)

    def set_selenium_local_session(self):
        """Starts local session for a selenium server.
        Default case scenario."""
        if self.aborting:
            return self

        if self.use_firefox:
            if self.firefox_profile_path is not None:
                firefox_profile = webdriver.FirefoxProfile(
                    self.firefox_profile_path)
            else:
                firefox_profile = webdriver.FirefoxProfile()

            # permissions.default.image = 2: Disable images load,
            # this setting can improve pageload & save bandwidth
            firefox_profile.set_preference('permissions.default.image', 2)

            self.browser = webdriver.Firefox(firefox_profile=firefox_profile)

        else:
            chromedriver_location = './assets/chromedriver'
            chrome_options = Options()
            chrome_options.add_argument('--dns-prefetch-disable')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--lang=en-US')
            chrome_options.add_argument('--disable-setuid-sandbox')
            
            ## This option implements Chrome Headless, a new (late 2017) GUI-less browser
            ## Must be Chromedriver 2.9 and above.
            if self.headless_browser:
                chrome_options.add_argument('--headless')
                user_agent = "Chrome" # Replaces browser User Agent from "HeadlessChrome".
                chrome_options.add_argument('user-agent={user_agent}'.format(user_agent=user_agent))

            # managed_default_content_settings.images = 2: Disable images load,
            # this setting can improve pageload & save bandwidth
            # default_content_setting_values.notifications = 2:
            # Disable notifications
            # credentials_enable_service & password_manager_enabled = false:
            # Ignore save password prompt from chrome
            # 'profile.managed_default_content_settings.images': 2,
            # 'profile.default_content_setting_values.notifications' : 2,
            # 'credentials_enable_service': False,
            # 'profile': {
            #   'password_manager_enabled': False
            # }

            chrome_prefs = {
                'intl.accept_languages': 'en-US'
            }
            chrome_options.add_experimental_option('prefs', chrome_prefs)
            self.browser = webdriver.Chrome(chromedriver_location,
                                            chrome_options=chrome_options)
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
                          self.switch_language):
            self.logger.critical('Wrong login data!')

            self.aborting = True
        else:
            self.logger.info('Logged in successfully!')

        log_follower_num(self.browser, self.username)

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
        """Changes the possible restriction to users, if user who postes
        is one of this, the image won't be liked"""
        if self.aborting:
            return self

        self.ignore_users = users or []

        return self

    def set_ignore_if_contains(self, words=None):
        """ignores the don't likes if the description contains
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
        """Defines if the clarifai img api should be used
        Which 'project' will be used (only 5000 calls per month)"""
        if self.aborting:
            return self

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
                'https://d212rkvo8t62el.cloudfront.net/tag/{}'.format(tag))
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
                        print('[smart hashtag generated: {}]'.format(item))
            else:
                print('Too few results for #{} tag'.format(tag))

        # delete duplicated tags
        self.smart_hashtags = list(set(self.smart_hashtags))
        return self

    def clarifai_check_img_for(self, tags=None, comment=False, comments=None):
        """Defines the tags, the images should be checked for"""
        if self.aborting:
            return self

        if tags is None and not self.clarifai_img_tags:
            self.use_clarifai = False
        elif tags:
            self.clarifai_img_tags.append((tags, comment, comments))

        return self

    def follow_by_list(self, followlist, times=1):
        """Allows to follow by any scrapped list"""
        self.follow_times = times or 0
        if self.aborting:
            return self

        followed = 0

        for acc_to_follow in followlist:
            if acc_to_follow in self.dont_include:
                continue

            if self.follow_restrict.get(acc_to_follow, 0) < self.follow_times:
                followed += follow_given_user(self.browser,
                                              acc_to_follow,
                                              self.follow_restrict,
                                              self.blacklist,
                                              self.logger)
                self.followed += followed
                self.logger.info('Followed: {}'.format(str(followed)))
                followed = 0
            else:
                self.logger.info('---> {} has already been followed more than '
                                 '{} times'.format(
                                    acc_to_follow, str(self.follow_times)))
                sleep(1)

        return self

    def set_upper_follower_count(self, limit=None):
        """Used to chose if a post is liked by the number of likes"""
        self.like_by_followers_upper_limit = limit or maxsize
        return self

    def set_lower_follower_count(self, limit=None):
        """Used to chose if a post is liked by the number of likes"""
        self.like_by_followers_lower_limit = limit or 0
        return self

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
                    inappropriate, user_name, is_video, reason = (
                        check_link(self.browser,
                                   link,
                                   self.dont_like,
                                   self.ignore_if_contains,
                                   self.ignore_users,
                                   self.username,
                                   self.like_by_followers_upper_limit,
                                   self.like_by_followers_lower_limit,
                                   self.logger)
                    )

                    if not inappropriate:
                        liked = like_image(self.browser,
                                           user_name,
                                           self.blacklist,
                                           self.logger)

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
                                                           self.logger)
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
                                                        self.logger)

                            else:
                                self.logger.info('--> Not following')
                                sleep(1)
                        else:
                            already_liked += 1
                    else:
                        self.logger.info(
                            '--> Image not liked: {}'.format(reason))
                        inap_img += 1
                except NoSuchElementException as err:
                    self.logger.error('Invalid Page: {}'.format(err))

        self.logger.info('Liked: {}'.format(liked_img))
        self.logger.info('Already Liked: {}'.format(already_liked))
        self.logger.info('Inappropriate: {}'.format(inap_img))
        self.logger.info('Commented: {}'.format(commented))
        self.logger.info('Followed: {}'.format(followed))

        self.followed += followed

        return self

    def like_by_tags(self,
                     tags=None,
                     amount=50,
                     media=None,
                     skip_top_posts=True,
                     use_smart_hashtags=False):
        """Likes (default) 50 images per given tag"""
        if self.aborting:
            return self

        liked_img = 0
        already_liked = 0
        inap_img = 0
        commented = 0
        followed = 0

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
                self.logger.error('Too few images, skipping this tag')
                continue

            for i, link in enumerate(links):
                self.logger.info('[{}/{}]'.format(i + 1, len(links)))
                self.logger.info(link)

                try:
                    inappropriate, user_name, is_video, reason = (
                        check_link(self.browser,
                                   link,
                                   self.dont_like,
                                   self.ignore_if_contains,
                                   self.ignore_users,
                                   self.username,
                                   self.like_by_followers_upper_limit,
                                   self.like_by_followers_lower_limit,
                                   self.logger)
                    )

                    if not inappropriate:
                        liked = like_image(self.browser,
                                           user_name,
                                           self.blacklist,
                                           self.logger)

                        if liked:
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
                                                           self.logger)
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
                                                        self.logger)
                            else:
                                self.logger.info('--> Not following')
                                sleep(1)
                        else:
                            already_liked += 1
                    else:
                        self.logger.info(
                            '--> Image not liked: {}'.format(reason))
                        inap_img += 1
                except NoSuchElementException as err:
                    self.logger.error('Invalid Page: {}'.format(err))

        self.logger.info('Liked: {}'.format(liked_img))
        self.logger.info('Already Liked: {}'.format(already_liked))
        self.logger.info('Inappropriate: {}'.format(inap_img))
        self.logger.info('Commented: {}'.format(commented))
        self.logger.info('Followed: {}'.format(followed))

        self.followed += followed

        return self

    def like_by_users(self, usernames, amount=10, randomize=False, media=None):
        """Likes some amounts of images for each usernames"""
        if self.aborting:
            return self

        total_liked_img = 0
        already_liked = 0
        inap_img = 0
        commented = 0
        followed = 0
        usernames = usernames or []

        for index, username in enumerate(usernames):
            self.logger.info(
                'Username [{}/{}]'.format(index + 1, len(usernames)))
            self.logger.info('--> {}'.format(username.encode('utf-8')))
            following = random.randint(0, 100) <= self.follow_percentage

            valid_user = validate_username(self.browser,
                                           username,
                                           self.ignore_users,
                                           self.blacklist,
                                           self.like_by_followers_upper_limit,
                                           self.like_by_followers_lower_limit)
            if valid_user is not True:
                self.logger.info(valid_user)
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
                                        self.logger)
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
                    inappropriate, user_name, is_video, reason = (
                        check_link(self.browser,
                                   link,
                                   self.dont_like,
                                   self.ignore_if_contains,
                                   self.ignore_users,
                                   self.username,
                                   self.like_by_followers_upper_limit,
                                   self.like_by_followers_lower_limit,
                                   self.logger)
                    )

                    if not inappropriate:
                        liked = like_image(self.browser,
                                           user_name,
                                           self.blacklist,
                                           self.logger)

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
                                                           self.logger)
                            else:
                                self.logger.info('--> Not commented')
                                sleep(1)

                        else:
                            already_liked += 1

                    else:
                        self.logger.info(
                            '--> Image not liked: {}'.format(reason))
                        inap_img += 1
                except NoSuchElementException as err:
                    self.logger.error('Invalid Page: {}'.format(err))

            if liked_img < amount:
                self.logger.info('-------------')
                self.logger.info("--> Given amount not fullfilled, "
                                 "image pool reached its end\n")

        self.logger.info('Liked: {}'.format(total_liked_img))
        self.logger.info('Already Liked: {}'.format(already_liked))
        self.logger.info('Inappropriate: {}'.format(inap_img))
        self.logger.info('Commented: {}'.format(commented))

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

        usernames = usernames or []

        for index, username in enumerate(usernames):
            self.logger.info(
                'Username [{}/{}]'.format(index + 1, len(usernames)))
            self.logger.info('--> {}'.format(username.encode('utf-8')))

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
                    inappropriate, user_name, is_video, reason = (
                        check_link(self.browser,
                                   link,
                                   self.dont_like,
                                   self.ignore_if_contains,
                                   self.ignore_users,
                                   self.username,
                                   self.like_by_followers_upper_limit,
                                   self.like_by_followers_lower_limit,
                                   self.logger)
                    )

                    if not inappropriate:

                        following = (
                            random.randint(0, 100) <= self.follow_percentage)
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
                                self.logger)
                        else:
                            self.logger.info('--> Not following')
                            sleep(1)

                        liking = random.randint(0, 100) <= self.like_percentage
                        if self.do_like and liking:
                            liked = like_image(self.browser,
                                               user_name,
                                               self.blacklist,
                                               self.logger)
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
                                                           self.logger)
                            else:
                                self.logger.info('--> Not commented')
                                sleep(1)
                        else:
                            already_liked += 1

                    else:
                        self.logger.info(
                            '--> Image not liked: {}'.format(reason))
                        inap_img += 1
                except NoSuchElementException as err:
                    self.logger.info('Invalid Page: {}'.format(err))

            if liked_img < amount:
                self.logger.info('-------------')
                self.logger.info("--> Given amount not fullfilled, image pool "
                                 "reached its end\n")

        self.logger.info('Liked: {}'.format(total_liked_img))
        self.logger.info('Already Liked: {}'.format(already_liked))
        self.logger.info('Inappropriate: {}'.format(inap_img))
        self.logger.info('Commented: {}'.format(commented))

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

        if self.aborting:
            return self

        userToInteract = []
        if not isinstance(usernames, list):
            usernames = [usernames]
        try:
            for user in usernames:

                user = get_given_user_followers(self.browser,
                                                user,
                                                amount,
                                                self.dont_include,
                                                self.username,
                                                self.follow_restrict,
                                                randomize,
                                                self.logger)
                if isinstance(user, list):
                    userToInteract += user
        except (TypeError, RuntimeWarning) as err:
            if isinstance(err, RuntimeWarning):
                self.logger.warning(
                    u'Warning: {} , stopping follow_users'.format(err))
                return self
            else:
                self.logger.error('Sorry, an error occured: {}'.format(err))
                self.aborting = True
                return self

        self.logger.info('--> Users: {} \n'.format(len(userToInteract)))
        userToInteract = random.sample(
            userToInteract,
            int(ceil(self.user_interact_percentage * len(userToInteract) / 100)))

        self.like_by_users(userToInteract,
                           self.user_interact_amount,
                           self.user_interact_random,
                           self.user_interact_media)

        return self

    def interact_user_following(self, usernames, amount=10, randomize=False):

        userToInteract = []
        if not isinstance(usernames, list):
            usernames = [usernames]
        try:
            for user in usernames:
                userToInteract += get_given_user_following(
                    self.browser,
                    user,
                    amount,
                    self.dont_include,
                    self.username,
                    self.follow_restrict,
                    randomize,
                    self.logger)
        except (TypeError, RuntimeWarning) as err:
            if isinstance(err, RuntimeWarning):
                self.logger.warning(
                    u'Warning: {} , stopping follow_users'.format(err))
                return self
            else:
                self.logger.error('Sorry, an error occured: {}'.format(err))
                self.aborting = True
                return self

        self.logger.info('--> Users: {}'.format(len(userToInteract)))

        userToInteract = random.sample(userToInteract, int(ceil(
            self.user_interact_percentage * len(userToInteract) / 100)))

        self.like_by_users(userToInteract,
                           self.user_interact_amount,
                           self.user_interact_random,
                           self.user_interact_media)

        return self

    def follow_user_followers(self,
                              usernames,
                              amount=10,
                              randomize=False,
                              interact=False,
                              sleep_delay=600):

        userFollowed = []
        if not isinstance(usernames, list):
            usernames = [usernames]
        for user in usernames:

            try:
                userFollowed += follow_given_user_followers(self.browser,
                                                            user,
                                                            amount,
                                                            self.dont_include,
                                                            self.username,
                                                            self.follow_restrict,
                                                            randomize,
                                                            sleep_delay,
                                                            self.blacklist,
                                                            self.logger)

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
        self.logger.info(
            "--> Total people followed : {} ".format(len(userFollowed)))

        if interact:
            self.logger.info('--> User followed: {}'.format(userFollowed))
            userFollowed = random.sample(userFollowed, int(ceil(
                self.user_interact_percentage * len(userFollowed) / 100)))
            self.like_by_users(userFollowed,
                               self.user_interact_amount,
                               self.user_interact_random,
                               self.user_interact_media)

        return self

    def follow_user_following(self,
                              usernames,
                              amount=10,
                              randomize=False,
                              interact=False,
                              sleep_delay=600):
        userFollowed = []
        if not isinstance(usernames, list):
            usernames = [usernames]

        for user in usernames:
            try:
                userFollowed += follow_given_user_following(self.browser,
                                                            user,
                                                            amount,
                                                            self.dont_include,
                                                            self.username,
                                                            self.follow_restrict,
                                                            randomize,
                                                            sleep_delay,
                                                            self.blacklist,
                                                            self.logger)

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
        self.logger.info("--> Total people followed : {} ".format(len(userFollowed)))

        if interact:
            self.logger.info('--> User followed: {}'.format(userFollowed))
            userFollowed = random.sample(userFollowed, int(ceil(
                self.user_interact_percentage * len(userFollowed) / 100)))
            self.like_by_users(userFollowed,
                               self.user_interact_amount,
                               self.user_interact_random,
                               self.user_interact_media)

        return self

    def unfollow_users(self,
                       amount=10,
                       onlyInstapyFollowed=False,
                       onlyInstapyMethod='FIFO',
                       sleep_delay=600,
                       onlyNotFollowMe=False):

        if self.aborting:
            return self
        
        """Unfollows (default) 10 users from your following list"""
        self.automatedFollowedPool = set_automated_followed_pool(self.username,
                                                                 self.logger)

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
                                      self.logger)
            self.logger.info(
                "--> Total people unfollowed : {} ".format(unfollowNumber))

        except (TypeError, RuntimeWarning) as err:
            if isinstance(err, RuntimeWarning):
                self.logger.warning(
                    u'Warning: {} , stopping unfollow_users'.format(err))
                return self
            else:
                self.logger.info('Sorry, an error occured: {}'.format(err))
                self.aborting = True
                return self

        return self

    def like_by_feed(self,
                     amount=50,
                     randomize=False,
                     unfollow=False,
                     interact=False):
        """Like the users feed"""

        if self.aborting:
            return self

        liked_img = 0
        already_liked = 0
        inap_img = 0
        commented = 0
        followed = 0
        skipped_img = 0
        num_of_search = 0
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
                return self

            num_of_search += 1

            for i, link in enumerate(links):
                if liked_img == amount:
                    break
                if randomize and random.choice([True, False]):
                    self.logger.warning('Post Randomly Skipped...\n')
                    skipped_img += 1
                else:
                    if link in history:
                        self.logger.info('This link has already '
                                         'been visited:\n', link, '\n')
                    else:
                        self.logger.info('New link found...')
                        history.append(link)
                        self.logger.info('[{} posts liked /{} amount]'
                                         .format(liked_img, amount))
                        self.logger.info(link)

                        try:
                            inappropriate, user_name, is_video, reason = (
                                check_link(self.browser,
                                           link,
                                           self.dont_like,
                                           self.ignore_if_contains,
                                           self.ignore_users,
                                           self.username,
                                           self.like_by_followers_upper_limit,
                                           self.like_by_followers_lower_limit,
                                           self.logger)
                            )

                            if not inappropriate:
                                liked = like_image(self.browser,
                                                   user_name,
                                                   self.blacklist,
                                                   self.logger)

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
                                                    self.logger,
                                                    self.clarifai_full_match)
                                            )
                                        except Exception as err:
                                            self.logger.error(
                                                'Image check error:'
                                                ' {}'.format(err))

                                    if (self.do_comment and
                                        user_name not in self.dont_include and
                                            checked_img and commenting):
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
                                                        self.logger)
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
                                            self.logger)
                                    else:
                                        self.logger.info('--> Not following')
                                        sleep(1)
                                else:
                                    already_liked += 1
                            else:
                                self.logger.info(
                                    '--> Image not liked: {}'.format(reason))
                                inap_img += 1
                                if reason == 'Inappropriate':
                                    unfollow_user(self.browser, self.logger)
                        except NoSuchElementException as err:
                            self.logger.error('Invalid Page: {}'.format(err))

        self.logger.info('Liked: {}'.format(liked_img))
        self.logger.info('Already Liked: {}'.format(already_liked))
        self.logger.info('Inappropriate: {}'.format(inap_img))
        self.logger.info('Commented: {}'.format(commented))
        self.logger.info('Followed: {}'.format(followed))
        self.logger.info('Randomly Skipped: {}'.format(skipped_img))

        self.followed += followed

    def getFollowerList_user(self, following=True, followers=False):
        unfollowNumber = getFollowerList(self.browser,
                                         self.username,
                                         self.logger,
                                         following,
                                         followers)
        return self

    def set_dont_unfollow_active_users(self, enabled=False, posts=4):
        """Prevents unfollow followers who have liked one of
        your latest X posts"""

        # do nothing
        if not enabled:
            return

        # list of users who liked our media
        active_users = get_active_users(self.browser,
                                        self.username,
                                        posts,
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
            with open('./logs/blacklist.csv', 'r') as blacklist:
                reader = csv.DictReader(blacklist)
                for row in reader:
                    if row['campaign'] == campaign:
                        self.dont_include.append(row['username'])
        except:
            self.logger.info('Campaign {} first run'.format(campaign))

    def end(self):
        """Closes the current session"""
        # If stopped in the middle than abort all other tasks
        self.aborting = True
        # Copy all followed by restriction to a json
        dump_follow_restriction(self.follow_restrict)
        self.browser.delete_all_cookies()
        self.browser.close()

        if self.nogui:
            self.display.stop()

        self.logger.info('Session ended - {}'.format(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.logger.info('-' * 20 + '\n\n')

        with open('./logs/followed.txt', 'w') as followFile:
            followFile.write(str(self.followed))
