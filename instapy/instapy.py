from datetime import datetime
from os import environ
from random import randint

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .utils.logger import default_logger
from .views.image import image
from .views.landing import landing
from .views.tag import tag
from .views.user import user


class InstaPy:
    """Class to be instantiated to use the script."""

    def __init__(self, username=None, password=None, nogui=False):
        """Start InstaPy with some defaults.

        set virtual = True to enable VirtualDisplay in servers.
        """
        self.logger = default_logger

        self.logger.info(
            "Session started - {}".format(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
        )

        self.username = username or environ.get('INSTA_USER')
        self.password = password or environ.get('INSTA_PW')

        # Check if we should use a virtual display or not
        self.nogui = nogui
        if nogui:
            self.logger.debug("Starting virtual display")
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()

        # Fire up the browser
        self._init_webdriver_browser()

        self.followed = 0

        # Load page classes
        self.landing = landing.set_browser(self.browser)
        self.image = image.set_browser(self.browser)
        self.user = user.set_browser(self.browser)
        self.tag = tag.set_browser(self.browser)

        # Start up all the settings
        self.aborting = False

        self.set_ignore_users()
        self.set_follower_limit()
        self.set_follow_rate()
        self.set_comment_rate()
        self.set_comments()
        self.set_dont_comment_users()
        self.set_dont_like()
        self.set_like_anyway()
        self.set_like_tags()
        self.set_like_media()

        # Ensure that .login() is the first call
        self.aborting = True

    # Logical flux
    def login(self):
        """Log user in."""
        self.logger.info(
            "Logging in with credentials for: {}".format(self.username)
        )
        success = self.landing.login(self.username, self.password)
        if success:
            self.aborting = False
            self.image.username = self.username
            self.logger.info("  Successfully logged in!")
        else:
            self.aborting = True
            self.logger.warning("  Failed to log in!"
                                " Please check your credentials")

        return self

    def like_images(self, amount=50):
        """Start process of liking images."""
        if self.aborting:
            return self

        liked_img = 0
        already_liked = 0
        unavailable = 0
        inap_img = 0
        commented = 0
        followed = 0

        # Cicle through tags
        for index, tag_name in enumerate(self.like_tags):
            self.logger.info(u'\n\nTag [{}/{}]'.format(index + 1,
                                                       len(self.like_tags)))
            self.logger.info(u'--> {}'.format(tag_name))
            self.tag.get_page(tag_name)
            links = self.tag.get_links(amount)

            # Cicle through image links
            for i, link in enumerate(links):
                self.logger.info(u'\n\n[{}/{}]'.format(i + 1, len(links)))

                # Get image page, continue if not available
                if self.image.get_page(link) is None:
                    self.logger.warning("Unavailable page")
                    self.logger.warning(u"  {}".format(link))
                    unavailable += 1
                    continue

                # Check if image is good and output its details
                good, reason, followers = self.image.check_everything()
                username = self.image.get_username()
                image_text = self.image.get_image_text()
                self.logger.info("Image from: {}".format(username))
                if followers is not None:
                    self.logger.info("  {} followers".format(followers))
                self.logger.info(u'Link: {}'.format(link))
                self.logger.info(u'Description: {}'.format(image_text.encode('utf-8')))

                # If image isn't good, go to the next one
                if not good:
                    self.logger.info(
                        "--> Image not liked: {}".format(reason)
                    )
                    inap_img += 1
                    continue

                # Like image
                liked = self.image.like_image()
                if liked is None:
                    self.logger.warning("--> Invalid like button")
                elif liked:
                    liked_img += 1
                    self.logger.info("--> Image liked")
                else:
                    already_liked += 1
                    self.logger.info("--> Already liked")

                # Decide wether or not to comment
                commenting = (self.comment_percentage and
                              randint(0, 100) <= self.comment_percentage and
                              username not in self.dont_comment_users)
                if commenting:
                    commented += 1
                    comment = self.image.comment_image()
                    self.logger.info(u"--> Commented: {}".format(comment))
                else:
                    self.logger.info("--> Not commented")

                # Decide wether or not to follow
                following = (self.follow_percentage and
                             randint(0, 100) <= self.follow_percentage)
                if following:
                    follow = self.image.follow()
                    if follow:
                        followed += 1
                        self.logger.info(
                            "--> Now following: {}".format(username)
                        )
                    else:
                        self.logger.info("--> Already following")
                else:
                    self.logger.info("--> Not following")

                # End cicle through links
            # End cicle through tags

        self.logger.info("")
        self.logger.info("Liked: {}".format(liked_img))
        self.logger.info("Already liked: {}".format(already_liked))
        self.logger.info("Unavailable: {}".format(unavailable))
        self.logger.info("Inappropriate: {}".format(inap_img))
        self.logger.info("Commented: {}".format(commented))
        self.logger.info("Followed: {}".format(followed))

        self.followed += followed

        return self

    def end(self):
        """Shut the system down."""
        self.logger.debug("Ending process")
        self.logger.debug("  Deleting cookies")
        self.browser.delete_all_cookies()
        self.logger.debug("  Closing Chrome webdriver")
        self.browser.close()
        if self.nogui:
            self.logger.debug("  Closing virtual display")
            self.display.stop()

        self.logger.info("")
        self.logger.info(
            "Session ended - {}".format(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
        )
        self.logger.info("-" * 20)

        # Make sure any further calls will be rendered useless
        self.aborting = True

    # Settings
    # Full settings
    def set_ignore_users(self, users=[]):
        """Blacklist users so we don't interact with them."""
        if self.aborting:
            return self

        self.image.ignore_users = users
        return self

    # Follow settings
    def set_follower_limit(self, lower=0, upper=0):
        """Set limits for following a user.

        if user has less followers than lower
            or more followers than upper,
            user won't be followed.
        """
        if self.aborting:
            return self

        self.logger.debug("Setting lower and upper limit for followers")
        self.image.lower_limit = lower
        self.image.upper_limit = upper
        return self

    def set_follow_rate(self, percentage=0, times=1):
        """Define follow rate for users."""
        if self.aborting:
            return self

        self.follow_percentage = percentage
        self.follow_times = times
        return self

    # Comment settings
    def set_comment_rate(self, percentage=0):
        """Define comment rate for images.

        percentage = 25
            makes about one in every 4 pictures to be commented.
        """
        if self.aborting:
            return self

        self.logger.debug("Setting comment rate")
        self.comment_percentage = percentage
        return self

    def set_comments(self, comments=[], media=None):
        """Set possible comments."""
        if self.aborting:
            return self

        self.logger.debug("Setting comments")
        self.image.comments.set_comment(comments, media)
        return self

    def set_dont_comment_users(self, users=[]):
        """Set users that we don't want to comment on."""
        if self.aborting:
            return self

        self.dont_comment_users = users
        return self

    # Like settings
    def set_dont_like(self, tags=[]):
        """Set tags that we shouldn't like.

        if one of this words is in the description,
            the image won't be liked.
        """
        if self.aborting:
            return self

        self.logger.debug("Setting dont_like tags")
        self.image.dont_like = tags
        return self

    def set_like_anyway(self, tags=[]):
        """Set tags that we should be liked anyway.

        if one of this words is in the description,
            the image will be liked even if dont_like tags are present.
        """
        if self.aborting:
            return self

        self.logger.debug("Setting like_anyway tags")
        self.image.like_anyway = tags
        return self

    def set_like_tags(self, tags=[]):
        """Set the tags that should be liked."""
        if self.aborting:
            return self

        self.logger.debug("Setting like_tags")
        self.like_tags = tags
        return self

    def set_like_tags_from_image(self, image_id):
        """Get tags from an image and set them to be liked."""
        if self.aborting:
            return self

        self.logger.debug("Getting tags form image")
        self.logger.debug(u"  image_id = {}".format(image_id))
        self.image.get_page(image_id)
        tags = self.image.get_tags()

        self.set_like_tags(tags)
        return self

    def set_like_media(self, media=None):
        """Set the medias that should be liked."""
        if self.aborting:
            return self

        self.tag.set_media(media)
        return self

    # Helpers
    def _init_webdriver_browser(self):
        chromedriver = environ.get('INSTA_DRIVE') or './assets/chromedriver'

        chrome_options = Options()
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--lang=en-US')
        chrome_options.add_experimental_option(
            'prefs',
            {'intl.accept_languages': 'en-US'}
        )
        self.logger.debug("Starting Chrome webdriver")
        self.browser = webdriver.Chrome(chromedriver,
                                        chrome_options=chrome_options)
        self.browser.implicitly_wait(25)
