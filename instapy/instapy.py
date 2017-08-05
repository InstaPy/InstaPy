"""OS Modules environ method to get the setup vars from the Environment"""
from datetime import datetime
from os import environ

from random import randint
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.webdriver import FirefoxProfile

from .clarifai_util import check_image
from .comment_util import comment_image
from .like_util import check_link
from .like_util import get_links_for_tag
from .like_util import get_tags
from .like_util import get_links_for_location
from .like_util import like_image
from .login_util import login_user
from .print_log_writer import log_follower_num
from .time_util import sleep
from .unfollow_util import unfollow
from .unfollow_util import follow_user
from .unfollow_util import follow_given_user
from .unfollow_util import load_follow_restriction
from .unfollow_util import dump_follow_restriction
from .unfollow_util import set_automated_followed_pool
from .unfollow_util import follow_follower
from .feed_util import get_like_on_feed


class InstaPy:
    """Class to be instantiated to use the script"""

    def __init__(self, username=None, password=None, nogui=False, selenium_local_session=True, use_firefox=False, page_delay=25):
        if nogui:
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()

        self.browser = None

        self.logFile = open('./logs/logFile.txt', 'a')

        self.username = username or environ.get('INSTA_USER')
        self.password = password or environ.get('INSTA_PW')
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
        self.automatedFollowedPool = []

        self.dont_like = ['sex', 'nsfw']
        self.ignore_if_contains = []
        self.ignore_users = []

        self.use_clarifai = False
        self.clarifai_secret = None
        self.clarifai_id = None
        self.clarifai_img_tags = []
        self.clarifai_full_match = False

        self.like_by_followers_upper_limit = 0
        self.like_by_followers_lower_limit = 0

        self.aborting = False

        if selenium_local_session:
            self.set_selenium_local_session()

    def set_selenium_local_session(self):
        """Starts local session for a selenium server. Default case scenario."""
        if self.aborting:
            return self
        
        if self.use_firefox:
            if self.firefox_profile_path is not None:
                firefox_profile = webdriver.FirefoxProfile(self.firefox_profile_path)
            else:
                firefox_profile = webdriver.FirefoxProfile()

            # permissions.default.image = 2: Disable images load, this setting can improve pageload & save bandwidth
            firefox_profile.set_preference('permissions.default.image', 2)

            self.browser = webdriver.Firefox(firefox_profile=firefox_profile)

        else:
            chromedriver_location = './assets/chromedriver'
            chrome_options = Options()
            chrome_options.add_argument('--dns-prefetch-disable')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--lang=en-US')

            # managed_default_content_settings.images = 2: Disable images load, this setting can improve pageload & save bandwidth
            # default_content_setting_values.notifications = 2: Disable notifications
            # credentials_enable_service & password_manager_enabled = false: Ignore save password prompt from chrome
            chrome_prefs = {
                'intl.accept_languages': 'en-US',
                'profile.managed_default_content_settings.images': 2,
                'profile.default_content_setting_values.notifications' : 2,
                'credentials_enable_service': False,
                'profile': {
                    'password_manager_enabled': False
                }
            }
            chrome_options.add_experimental_option('prefs', chrome_prefs)
            self.browser = webdriver.Chrome(chromedriver_location, chrome_options=chrome_options)
        self.browser.implicitly_wait(self.page_delay)
        self.logFile.write('Session started - %s\n' \
                           % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        return self

    def set_selenium_remote_session(self, selenium_url=''):
        """Starts remote session for a selenium server. Useful for docker setup."""
        if self.aborting:
            return self

        self.browser = webdriver.Remote(command_executor=selenium_url,
                                        desired_capabilities=DesiredCapabilities.CHROME)
        self.browser.maximize_window()
        self.logFile.write('Session started - %s\n' \
                           % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        return self

    def login(self):
        """Used to login the user either with the username and password"""
        if not login_user(self.browser, self.username, self.password, self.switch_language):
            print('Wrong login data!')
            self.logFile.write('Wrong login data!\n')

            self.aborting = True
        else:
            print('Logged in successfully!')
            self.logFile.write('Logged in successfully!\n')

        log_follower_num(self.browser, self.username)

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
            print('Unkown media type! Treating as "any".')
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

    def set_dont_like(self, tags=None):
        """Changes the possible restriction tags, if one of this
         words is in the description, the image won't be liked"""
        if self.aborting:
            return self

        self.dont_like = tags or []

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

    def set_use_clarifai(self, enabled=False, secret=None, proj_id=None, full_match=False):
        """Defines if the clarifai img api should be used
        Which 'project' will be used (only 5000 calls per month)"""
        if self.aborting:
            return self

        self.use_clarifai = enabled

        if secret is None and self.clarifai_secret is None:
            self.clarifai_secret = environ.get('CLARIFAI_SECRET')
        elif secret:
            self.clarifai_secret = secret

        if proj_id is None and self.clarifai_id is None:
            self.clarifai_id = environ.get('CLARIFAI_ID')
        elif proj_id is not None:
            self.clarifai_id = proj_id

        self.clarifai_full_match = full_match

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
            if self.follow_restrict.get(acc_to_follow, 0) < self.follow_times:
                followed += follow_given_user(self.browser, acc_to_follow, self.follow_restrict)
                self.followed += followed
                self.logFile.write('Followed: {}\n'.format(str(followed)))
                followed = 0
            else:
                print('---> {} has already been followed more than {} times'.format(acc_to_follow,
                                                                                    str(self.follow_times)))
                sleep(1)

        return self

    def set_upper_follower_count(self, limit=None):
        """Used to chose if a post is liked by the number of likes"""
        self.like_by_followers_upper_limit = limit or 0
        return self

    def set_lower_follower_count(self, limit=None):
        """Used to chose if a post is liked by the number of likes"""
        self.like_by_followers_lower_limit = limit or 0
        return self

    def like_by_locations(self, locations=None, amount=50, media=None):
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
            print('Location [{}/{}]'.format(index + 1, len(locations)))
            print('--> {}'.format(location.encode('utf-8')))
            self.logFile.write('Location [{}/[]]'.format(index + 1, len(locations)))
            self.logFile.write('--> {}\n'.format(location.encode('utf-8')))

            try:
                links = get_links_for_location(self.browser, location, amount, media)
            except NoSuchElementException:
                print('Too few images, aborting')
                self.logFile.write('Too few images, aborting\n')

                self.aborting = True
                return self

            for i, link in enumerate(links):
                print('[{}/{}]'.format(i + 1, len(links)))
                self.logFile.write('[{}/{}]'.format(i + 1, len(links)))
                self.logFile.write(link)

                try:
                    inappropriate, user_name, is_video, reason = \
                        check_link(self.browser, link, self.dont_like, self.ignore_if_contains, self.ignore_users,
                                   self.username, self.like_by_followers_upper_limit,
                                   self.like_by_followers_lower_limit)

                    if not inappropriate:
                        liked = like_image(self.browser)

                        if liked:
                            liked_img += 1
                            checked_img = True
                            temp_comments = []
                            commenting = randint(0, 100) <= self.comment_percentage
                            following = randint(0, 100) <= self.follow_percentage

                            if self.use_clarifai and (following or commenting):
                                try:
                                    checked_img, temp_comments = \
                                        check_image(self.browser, self.clarifai_id,
                                                    self.clarifai_secret,
                                                    self.clarifai_img_tags,
                                                    self.clarifai_full_match)
                                except Exception as err:
                                    print('Image check error: {}'.format(err))
                                    self.logFile.write('Image check error: {}\n'.format(err))

                            if self.do_comment and user_name not in self.dont_include \
                                    and checked_img and commenting:
                                if temp_comments:
                                    # Use clarifai related comments only!
                                    comments = temp_comments
                                elif is_video:
                                    comments = self.comments + self.video_comments
                                else:
                                    comments = self.comments + self.photo_comments
                                commented += comment_image(self.browser, comments)
                            else:
                                print('--> Not commented')
                                sleep(1)

                            if self.do_follow and user_name not in self.dont_include \
                                    and checked_img and following \
                                    and self.follow_restrict.get(user_name, 0) < self.follow_times:
                                followed += follow_user(self.browser, self.follow_restrict, self.username, user_name)

                            else:
                                print('--> Not following')
                                sleep(1)
                        else:
                            already_liked += 1
                    else:
                        print('--> Image not liked: {}'.format(reason))
                        inap_img += 1
                except NoSuchElementException as err:
                    print('Invalid Page: {}'.format(err))
                    self.logFile.write('Invalid Page: {}\n'.format(err))

                print('')
                self.logFile.write('\n')

        print('Liked: {}'.format(liked_img))
        print('Already Liked: {}'.format(already_liked))
        print('Inappropriate: {}'.format(inap_img))
        print('Commented: {}'.format(commented))
        print('Followed: {}'.format(followed))

        self.logFile.write('Liked: {}\n'.format(liked_img))
        self.logFile.write('Already Liked: {}\n'.format(already_liked))
        self.logFile.write('Inappropriate: {}\n'.format(inap_img))
        self.logFile.write('Commented: {}\n'.format(commented))
        self.logFile.write('Followed: {}\n'.format(followed))

        self.followed += followed

        return self

    def like_by_tags(self, tags=None, amount=50, media=None):

        """Likes (default) 50 images per given tag"""
        if self.aborting:
            return self

        liked_img = 0
        already_liked = 0
        inap_img = 0
        commented = 0
        followed = 0

        tags = tags or []

        for index, tag in enumerate(tags):
            print('Tag [{}/{}]'.format(index + 1, len(tags)))
            print('--> {}'.format(tag.encode('utf-8')))
            self.logFile.write('Tag [{}/[]]'.format(index + 1, len(tags)))
            self.logFile.write('--> {}\n'.format(tag.encode('utf-8')))

            try:
                links = get_links_for_tag(self.browser, tag, amount, media)
            except NoSuchElementException:
                print('Too few images, aborting')
                self.logFile.write('Too few images, aborting\n')

                self.aborting = True
                return self

            for i, link in enumerate(links):
                print('[{}/{}]'.format(i + 1, len(links)))
                self.logFile.write('[{}/{}]'.format(i + 1, len(links)))
                self.logFile.write(link)

                try:
                    inappropriate, user_name, is_video, reason = \
                        check_link(self.browser, link, self.dont_like, self.ignore_if_contains, self.ignore_users,
                                   self.username, self.like_by_followers_upper_limit,
                                   self.like_by_followers_lower_limit)

                    if not inappropriate:
                        liked = like_image(self.browser)

                        if liked:
                            liked_img += 1
                            checked_img = True
                            temp_comments = []
                            commenting = randint(0, 100) <= self.comment_percentage
                            following = randint(0, 100) <= self.follow_percentage

                            if self.use_clarifai and (following or commenting):
                                try:
                                    checked_img, temp_comments = \
                                        check_image(self.browser, self.clarifai_id,
                                                    self.clarifai_secret,
                                                    self.clarifai_img_tags,
                                                    self.clarifai_full_match)
                                except Exception as err:
                                    print('Image check error: {}'.format(err))
                                    self.logFile.write('Image check error: {}\n'.format(err))

                            if self.do_comment and user_name not in self.dont_include \
                                    and checked_img and commenting:
                                if temp_comments:
                                    # Use clarifai related comments only!
                                    comments = temp_comments
                                elif is_video:
                                    comments = self.comments + self.video_comments
                                else:
                                    comments = self.comments + self.photo_comments
                                commented += comment_image(self.browser, comments)
                            else:
                                print('--> Not commented')
                                sleep(1)

                            if self.do_follow and user_name not in self.dont_include \
                                    and checked_img and following \
                                    and self.follow_restrict.get(user_name, 0) < self.follow_times:
                                followed += follow_user(self.browser, self.follow_restrict, self.username, user_name)
                            else:
                                print('--> Not following')
                                sleep(1)
                        else:
                            already_liked += 1
                    else:
                        print('--> Image not liked: {}'.format(reason))
                        inap_img += 1
                except NoSuchElementException as err:
                    print('Invalid Page: {}'.format(err))
                    self.logFile.write('Invalid Page: {}\n'.format(err))

                print('')
                self.logFile.write('\n')

        print('Liked: {}'.format(liked_img))
        print('Already Liked: {}'.format(already_liked))
        print('Inappropriate: {}'.format(inap_img))
        print('Commented: {}'.format(commented))
        print('Followed: {}'.format(followed))

        self.logFile.write('Liked: {}\n'.format(liked_img))
        self.logFile.write('Already Liked: {}\n'.format(already_liked))
        self.logFile.write('Inappropriate: {}\n'.format(inap_img))
        self.logFile.write('Commented: {}\n'.format(commented))
        self.logFile.write('Followed: {}\n'.format(followed))

        self.followed += followed

        return self

    def like_from_image(self, url, amount=50, media=None):
        """Gets the tags from an image and likes 50 images for each tag"""
        if self.aborting:
            return self

        try:
            if not url:
                urls = self.browser.find_elements_by_xpath("//main//article//div//div[1]//div[1]//a[1]")
                url = urls[0].get_attribute("href")
                print("new url ", url)
            tags = get_tags(self.browser, url)
            print(tags)
            self.like_by_tags(tags, amount, media)
        except TypeError as err:
            print('Sorry, an error occured: {}'.format(err))
            self.logFile.write('Sorry, an error occured: {}\n'.format(err))

            self.aborting = True
            return self

        return self

    def unfollow_users(self, amount=10, onlyInstapyFollowed=False):
        """Unfollows (default) 10 users from your following list"""
        self.automatedFollowedPool = set_automated_followed_pool(self.username)

        try:
            unfollowNumber = unfollow(self.browser, self.username, amount, self.dont_include, onlyInstapyFollowed,
                                      self.automatedFollowedPool)
            print("--> Total people unfollowed : {} ".format(unfollowNumber))

        except (TypeError, RuntimeWarning) as err:
            if type(err) == RuntimeWarning:
                print(u'Warning: {} , stopping unfollow_users'.format(err))
                self.logFile.write('Warning: {} , stopping unfollow_users\n'.format(err))

                return self
            else:
                print('Sorry, an error occured: {}'.format(err))
                self.logFile.write('Sorry, an error occured: {}\n'.format(err))
                self.aborting = True

                return self

        return self

    def like_by_feed(self, amount):
        """Like the users feed"""

        if self.aborting:
            return self

        # go to feeds page
        self.browser.get('https://www.instagram.com')

        for button in get_like_on_feed(self.browser, amount):
            try:
                button.click()
                print('---> Image Liked')
                sleep(3)
            except:
                print('Unable to perform Like')

        return self

    def end(self):
        """Closes the current session"""
        dump_follow_restriction(self.follow_restrict)
        self.browser.delete_all_cookies()
        self.browser.close()

        if self.nogui:
            self.display.stop()

        print('')
        print('Session ended')
        print('-------------')

        self.logFile.write(
            '\nSession ended - {}\n'.format(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
        )
        self.logFile.write('-' * 20 + '\n\n')
        self.logFile.close()

        with open('./logs/followed.txt', 'w') as followFile:
            followFile.write(str(self.followed))

    def follow_user_follower(self, users=None, amount=50, interval=40, random=False):
        if self.aborting:
            return self

        followed = 0

        users = users or []

        for index, user in enumerate(users):
            print('User [{}/{}]'.format(index + 1, len(users)))
            print('--> {}'.format(user.encode('utf-8')))
            self.logFile.write('User [{}/[]]'.format(index + 1, len(users)))
            self.logFile.write('--> {}\n'.format(user.encode('utf-8')))

            try:
                followed += follow_follower(self.browser, user, amount, self.dont_include, self.automatedFollowedPool, self.username, interval, self.follow_restrict, random)

            except NoSuchElementException:
                print('Too few followers, aborting')
                self.logFile.write('Too few followers, aborting\n')

                self.aborting = True
                return self
            # followed +=1
            # print('-------------')
            # print('--> Followed from this user: {}'.format(follow))
            print('')

        print('Followed: {}'.format(followed))

        return self