#!/usr/bin/env python3
"""
Post model for interactions posts attributes and perform action on posts
"""
from enum import Enum

class Post():
    class Types(Enum):
        PHOTO = 0
        CAROUSEL = 1
        VIDEO = 2

    def __init__(self, like_count = None, comment_count = None):

        self._like_count = like_count
        self._comment_count = comment_count

    def __hash__(self):
        return hash(self.link)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return hash(self) == hash(other)
        else:
            return False

    def __repr__(self):
        return "Post({0}, {1})".format(hash(self), self.type)

    def __str__(self):
        return repr(self)

    # def show(self, session):
    #     web_address_navigator(session.browser, self.link)

    @property
    def like_count(self):
        """
        getter for like_count
        :return:
        """
        if self._like_count is None:
            self._like_count = self.get_like_count()

        return self._like_count

    def comment_count(self):
        """
        getter for comment_count
        :return:
        """
        if self._comment_count is None:
            self._comment_count = self.get_comment_count()

        return self._comment_count

    def get_like_count(self):
        """
        Abstract function to be defined by the driver
        :return:
        """
        pass

    def get_comment_count(self):
        """
        Abstract function to be defined by the driver
        :return:
        """

    # def populate(self, session):
    #     print("[+] populating post values")
    #     self.show(session)
    #     self.count_likes(session, refresh=False)
    #     self.count_comments(session, refresh=False)
    #
    # def refresh(self, session):
    #     print("[+] refreshing post values")
    #     self.show(session)
    #     self.count_likes(session, refresh=True)
    #     self.count_comments(session, refresh=True)
