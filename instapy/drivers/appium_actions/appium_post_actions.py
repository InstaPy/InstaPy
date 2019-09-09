"""
Class to define the specific actions for the AppiumPost class to work with Appium
"""

class AppiumPostActions():

    @classmethod
    def do_like(self):
        """"
        to implement the action of liking a post
        """

        # TODO: implement

    @classmethod
    def do_unlike(self):
        """
        to implement the action of unliking a post
        """
        # TODO: implement

    @classmethod
    def do_comment(self, comment=None):
        """
        to implement the action of commenting on a post
        """
        # TODO: implement

    @classmethod
    def get_user(self):
        """
        function that click on the username of the post and return a User
        :returns User()
        """
        #TODO: implement


        # return User()

    @classmethod
    def get_comments(self):
        """
        function that return the list of comments on the post
        :returns Array/List of Comment
        """
        # TODO: implement
        # return comments

    @classmethod
    def get_likers(self, amount):
        """"
        function that return a list of Users that liked the post
        :param amount Amount of User to get and return
        :returns Array/List of User
        """
        # TODO: implement
        # ideally we should have the criterias for the user that
        # are interesting to us, and return only the users that fits.
        # further integration with Setting needed to do this...

        # return users
