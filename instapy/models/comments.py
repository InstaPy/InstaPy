#!/usr/bin/env python3
"""
Comment model for interactions comment attributes and perform action on comments
"""


class Comment(object):

    def __init__(self, link=None, user=None, text=None, timestamp=None, like_count=None, reply_count=None):
        self.link = link

        self.user = user
        self.text = text
        self.timestamp = timestamp

        self.like_count = like_count
        self.reply_count = reply_count

    # Used for working with sets
    def __hash__(self):
        return hash(self.link + self.user + self.text)

    # Used for working with sets
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return hash(self) == hash(other)
        else:
            return False

    def __repr__(self):
        return "Comment({0}, {1}, {2}, {3}, {4}, {5})".format(hash(self), self.link, self.user, self.text, self.like_count, self.reply_count)

    def __str__(self):
        return repr(self)