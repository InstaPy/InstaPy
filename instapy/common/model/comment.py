#!/usr/bin/env python3
"""
Comment model for interactions comment attributes and perform action on comments
"""

class Comment():
    def __init__(self, user=None, text=None, timestamp=None, like_count=None, reply_count=None):


        self._user = user
        self._text = text
        self._timestamp = timestamp

        self._like_count = like_count
        self._reply_count = reply_count

    # Used for working with sets
    def __hash__(self):
        return hash( self.user + self.text + self.timestamp)

    # Used for working with sets
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return hash(self) == hash(other)
        else:
            return False

    def __repr__(self):
        return "Comment({0}, {1}, {2}, {3}, {4}, {5})".format(
            hash(self),
            self.user,
            self.text,
            self.timestamp,
            self.like_count,
            self.reply_count,
        )

    def __str__(self):
        return repr(self)

    @property
    def user(self):
        """
        getter for User object representing the User who made the comment
        :return: User
        """
        if _user is None:
            _user = self.get_user()

        return _user

    @property
    def text(self):
        """
        getter for comment text
        :return:
        """
        if self._text is None:
            self._text = self.get_text()

        return self._text

    @property
    def timestamp(self):
        """
        getter for timestamp of comment
        :return:
        """

        if _timestamp is None:
            self._timestamp = self.get_timestamp()

        return self._timestamp

    @property
    def like_count(self):
        """
        getter for the amount of likes on the comment
        :return:
        """

        if _like_count is None:
            self._like_count = self.get_like_count()

        return self._like_count

    @property
    def reply_count(self):
        """
        getter for the amount of replies on the comment
        :return:
        """

        if _reply_count is None:
            self._reply_count = self.get_reply_count()

        return self._reply_count

    def like(self):
        """
        Abstract function to be defined by the driver
        """
        pass

    # TODO: implement
    def unlike(self):
        """
        Abstract function to be defined by the driver
        """
        pass

    # TODO: implement
    def reply(self, reply=None):
        """
        Abstract function to be defined by the driver
        """
        pass

    def get_user(self):
        """
        Abstract function to be defined by the driver
        """
        pass

    def get_text(self):
        """
        Abstract function to be defined by the driver
        """
        pass

    def get_timestamp(self):
        """
        Abstract function to be defined by the driver
        """
        pass

    def get_like_count(self):
        """
        Abstract function to be defined by the driver
        """
        pass

    def get_comment_count(self):
        """
        Abstract function to be defined by the driver
        """
        pass

    def get_reply_count(self):
        """
        Abstract function to be defined by the driver
        """
        pass
