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

