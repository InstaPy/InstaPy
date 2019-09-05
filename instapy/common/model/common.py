"""
Common base class for User, Post, Comment

Manipulate common attributes to all classes
"""

class Common(object):

    def __init__(self, driver = None):
        self._driver = driver

    @property
    def driver(self):
        return self._driver

    def go_home(self):
        """
        Abstract function to be defined by the driver
        :return:
        """
        pass

    def go_profile(self):
        """
        Abstract function to be defined by the driver
        :return:
        """
        pass

    def go_user(self):
        """
        Abstract function to be defined by the driver
        :return:
        """
        pass