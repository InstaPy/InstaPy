"""
User model for interactions user attributes and perform action on users
"""


class User(object):
    def __init__(self, username=None):
        # text=None, post_count=None, follower_count=None, following_count=None):
        self.username = username

        self._posts = None
        self._following = None
        self._followers = None
        self._full_name_header = None
        self._description = None

    # Used for working with sets
    def __hash__(self):
        return hash(self.username)

    # Used for working with sets
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return hash(self) == hash(other)
        else:
            return False

    def __repr__(self):
        return "User({}, {}, {}, {}, {},{},{})".format(
            hash(self), self.username, self._posts, self._followers, self._following, self._description,self._full_name_header
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

    def populate(self,posts,following,followers,header,desc):
        """
         load the data into the User object
         :param session:
         :return:
         """
         self._posts = posts
         self._followers = followers
         self._following = following
         self._full_name_header = header
         self._description = desc
