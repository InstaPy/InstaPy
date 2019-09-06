"""
User model for interactions user attributes and perform action on users
"""

class User():

    def __init__(self,username: str, post_count=None, follower_count=None, following_count=None, full_name=None, bio=None ):
        """
        init
        """
        self.username = username
        self._post_count = post_count
        self._follower_count = follower_count
        self._following_count = following_count
        self._full_name = full_name
        self._bio = bio


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
            hash(self), self.username, self.post_count, self.follower_count, self.following_count, self.full_name, self.bio
        )

    def __str__(self):
        return repr(self)

    @property
    def post_count(self):
        """
        Getter for post_count (self.post_count will call this function automatically)
        :return:
        """

        if self._post_count is None:
            self.get_post_count()

        return self._post_count

    @property
    def follower_count(self):
        """
        Getter for follower_count (self.follower_count will call this function automatically)
        :return:
        """

        if self._follower is None:
            self.get_follower()

        return self._follower

    @property
    def following_count(self):
        """
        Getter for following_count (self.following_count will call this function automatically)
        :return:
        """

        if self._following is None:
            self.get_following_count()

        return self._following

    @property
    def bio(self):
        """
        Getter for the bio
        :return:
        """

        if self._bio is None:
            self.get_bio()

        return self._bio

    @property
    def full_name(self):
        """
        Getter for the header description
        :return:
        """

        if self._full_name is None:
            self.get_full_name()

        return self._full_name

    def populate(self,post_count=0,following_count=0,follower_count=0,full_name="",bio=""):
        """
         load the data into the User object
         """

        self._post_count = post_count
        self._follower_count = follower_count
        self._following_count = following_count
        self._full_name = full_name
        self._bio = bio

    def get_post_count(self):
        """
        Abstract, to be implemented by the driver
        :return:
        """
        pass

    def get_follower_count(self):
        """
        Abstract to be implemented by the driver
        :return:
        """
        pass

    def get_following_count(self):
        """
        Abstract to be implemented by the driver
        :return:
        """
        pass

    def get_bio(self):
        """
        Abstract to be implemented by the driver
        :return:
        """
        pass

    def get_full_name(self):
        """
        Abstract to be implemented by the driver
        :return:
        """
        pass
