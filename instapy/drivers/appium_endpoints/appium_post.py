"""
Class to define the specific actions for the AppiumPost class to work with Appium
"""

from instapy.common.model.post import Post
from instapy.common.model.comment import Comment
from instapy.common.model.user import User
from .common import Common

class AppiumPost(Post, Common):

    def __init__(self):
        """

        """
        super().__init__()

    def do_like(self):
        """"
        to implement the action of liking a post
        """

        # TODO: implement


    def do_unlike(self):
        """
        to implement the action of unliking a post
        """
        # TODO: implement

    def do_comment(self, comment=None):
        """
        to implement the action of commenting on a post
        """
        # TODO: implement


    def get_user(self):
        """
        function that click on the username of the post and return a User
        :returns User()
        """
        #TODO: implement


        # return User()


    def get_comments(self):
        """
        function that return the list of comments on the post
        :returns Array/List of Comment
        """
        # TODO: implement
        # return comments


    def get_likers(self):
        """"
        function that return a list of Users that liked the post
        :returns Array/List of User
        """
        # TODO: implement

        # return users

