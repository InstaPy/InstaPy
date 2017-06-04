# -*- coding: utf-8 -*-

from re import findall
from sys import version_info

from instapy.utils.browser_util import reduce_wait
from instapy.utils.comments import Comments
from instapy.utils.views_mixin import BaseMixin

from .user import user


if version_info.major == 3:
    unicode = str


class Image(BaseMixin):
    """Handler for image pages."""

    def __init__(self, *args, **kwargs):
        """Start page with some defaults."""
        super(Image, self).__init__(*args, **kwargs)
        self.set_object_url('/p/')
        self.media = None
        self.graphql = None
        self.is_video = None

        self.user = None
        self.ignore_users = []
        self.lower_limit = 0
        self.upper_limit = 0

        self.like_anyway = []
        self.dont_like = []

        self.comments = Comments()

    def get_page(self, obj):
        """Get page for a given object.

        Returns Page media if success else None
        """
        self.browser_check()
        self.set_current_obj(obj)
        success = self.get_object_url()
        if not success:
            return None

        # Get post page
        page = self.browser.execute_script("""
            return window._sharedData.entry_data.PostPage
        """)

        self.graphql = None
        if page:
            # Is it using graphQL?
            self.graphql = 'graphql' in page[0]
            # Get post media attribute
            self.media = page[0]['graphql']['shortcode_media'] \
                if self.graphql \
                else page[0]['media']

        return self.media

    def get_is_video(self):
        """Get is_video property."""
        self.page_check()
        return self.media['is_video']

    def get_username(self):
        """Get username from current page."""
        self.page_check()
        return self.media['owner']['username']

    def get_image_text(self):
        """Get image_text from current page."""
        self.page_check()
        if self.graphql:
            image_text = self.media['edge_media_to_caption']['edges']
            image_text = image_text[0]['node']['text'] if image_text else None
        else:
            image_text = self.media['caption']

        # Get owner comments and append them to image_text
        owner_comments = self.get_comments(mode='owner', join='\n')
        if image_text is None:
            image_text = owner_comments
        elif owner_comments is not None:
            image_text += '\n'
            image_text += owner_comments

        # If we still don't have a valid text, get the first comment
        if image_text is None:
            image_text = self.get_comments(mode='first')

        return image_text

    def get_comments(self, mode=None, join=None):
        """Get comments from current page.

        if mode == 'first': get first comment only;
        if mode == 'owner': get all available owner comments;

        if join, join the available comments using this as separator.
        """
        self.page_check()
        username = self.get_username()
        self.is_video = self.get_is_video()
        if self.graphql:
            comments = self.media['edge_media_to_comment']['edges']
            if mode == 'first':
                comments = comments[0]['node']['text'] \
                    if comments \
                    else None
            if mode == 'owner':
                comments = [
                    comment['node']['text']
                    for comment in comments
                    if comment['node']['owner']['username'] == username
                ]
        else:
            comments = self.media['comments']['nodes']
            if mode == 'first':
                comments = comments[0]['text'] \
                    if comments \
                    else None
            if mode == 'owner':
                comments = [
                    comment['text']
                    for comment in comments
                    if comment['user']['username'] == username
                ]

        if isinstance(join, (str, unicode)) and (comments is not None):
            comments = join.join(comments)

        return comments

    def get_image_link(self):
        """Get link for the image in the current page."""
        self.page_check()
        return self.get_attribute_by_xpath('//img[@class = "_icyx7"]',
                                           'src')

    def get_followers(self):
        """Get number of followers from page owner."""
        # Get user page.
        user.get_page(self.get_username())
        followers = user.get_followers()

        # And get back to this image page.
        self.get_object_url()
        return followers

    def follow(self, unfollow=False):
        """Follow owner of current page.

        if unfollow: unfollows the owner.
        """
        self.page_check()
        follow_xpath = "//article/header/span/button"
        follow_text = 'Following' if unfollow else 'Follow'
        follow = self.get_text_by_xpath(follow_xpath) == follow_text
        if follow:
            self.click_by_xpath(follow_xpath)

        return follow

    def unfollow(self):
        """Unfollow owner of current page."""
        return self.follow(unfollow=True)

    def check_ignore_user(self):
        """Check if this page should be ignored based on its owner."""
        username = self.get_username()
        followers = None
        if username == self.user:
            return False, "It's not cool to like your own image.", followers
        if username in self.ignore_users:
            return False, 'User is blacklisted.', followers

        if self.lower_limit or self.upper_limit:
            followers = self.get_followers()
            if self.lower_limit and (followers < self.lower_limit):
                return (False, 'Not enough followers to be a cool kid.',
                        followers)

            if self.upper_limit and (followers > self.upper_limit):
                return False, 'Too many followers.', followers

        return True, None, followers

    def check_like_anyway(self, text):
        """Check if this page shouldn't be ignored based on some text."""
        text = text.lower() if text else ''
        return any((word.lower() in text for word in self.like_anyway)), None

    def check_dont_like(self, text):
        """Check if this page should be ignored based on some text."""
        text = text.lower() if text else ''
        good = not any((word.lower() in text for word in self.dont_like))
        reason = None if good else 'Inappropriate description.'
        return good, reason

    def check_everything(self):
        """Check if this page should be ignored based on several factors."""
        good, reason, followers = self.check_ignore_user()
        if not good:
            return good, reason, followers

        image_text = self.get_image_text()
        good, reason = self.check_like_anyway(image_text)
        if good:
            return good, reason, followers

        good, reason = self.check_dont_like(image_text)
        if not good:
            return good, reason, followers

        return good, reason, followers

    def like_image(self):
        """Like the image in the current page."""
        liked = None
        with reduce_wait(self.browser):
            liked = self.click_by_xpath(
                "//a[@role = 'button']/span[text()='Like']")
        if liked is None:
            unliked = self.find_by_xpath(
                "//a[@role = 'button']/span[text()='Unlike']")
            liked = False if unliked else None
            return liked

        return True

    def comment_image(self):
        """Make a comment on the current page."""
        media = 'Video' if self.is_video else 'Photo'
        rand_comment = self.comments.get_random_comment(media)
        self.submit_form_by_xpath(
            '//input[@placeholder = "Add a comment…"]',
            [rand_comment]
        )

        return rand_comment

    def get_tags(self):
        """Get all tags from current image_text."""
        image_text = self.get_image_text()
        tags = findall(r'#\w*', image_text)
        return tags

image = Image()
image.set_target('instagram')
