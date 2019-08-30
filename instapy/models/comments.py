#!/usr/bin/env python3
"""
Comment model for interactions comment attributes and perform action on comments
"""
from .users import User
from ..like_util import like_comment
from ..util import web_address_navigator


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


    def show(self, session):
        web_address_navigator(session.browser, self.link)


    def like(self, session, verify=False):
        print("[+] like comment")

        self.show(session)
        like_comment(session.browser, self.text, session.logger)


    # TODO: implement
    def unlike(self, session, verify=False):
        print("[+] unlike comment")
        print("NOT YET IMPLEMENTED")
        pass


    # TODO: implement
    def reply(self, reply=None, verify=False):
        print("[+] reply to comment")
        print("NOT YET IMPLEMENTED")
        pass


    def get_user(self, session):
        print("[+] get comment user")
        return User(name=self.user)




