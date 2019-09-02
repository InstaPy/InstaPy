"""
User model for interactions user attributes and perform action on users
"""


class User(object):
    def __init__(self, link=None, name=None, session=None):
        # text=None, post_count=None, follower_count=None, following_count=None):
        self.link = link
        self.name = name
        self.session = session

        self._posts = None
        self._following = None
        self._followers = None

    # Used for working with sets
    def __hash__(self):
        return hash(self.link)

    # Used for working with sets
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return hash(self) == hash(other)
        else:
            return False

    def __repr__(self):
        return "User({0}, {1}, {2}, {3}, {4}, {5})".format(
            hash(self), self.link, self.name, self.posts, self.followers, self.following
        )

    def __str__(self):
        return repr(self)

    @property
    def posts(self):
        """
        Getter for post_count (self.post_count will call this function automatically)
        :return:
        """

        return self._posts

    @property
    def followers(self):
        """
        Getter for follower_count (self.follower_count will call this function automatically)
        :return:
        """

        return self._followers

    @property
    def following(self):
        """
        Getter for following_count (self.following_count will call this function automatically)
        :return:
        """

        return self._following

    def populate(self):
        """
         load the data into the User object
         :param session:
         :return:
         """
