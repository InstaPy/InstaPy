"""
class that combines all the exposed methods to simplify
the creation of the WebDriver
common methods are inherited (so visible at the top layer)
specific method are callable by SeleniumActions.user.method
etc...
"""

from instapy.drivers.selenium_actions import SeleniumCommonActions
from instapy.drivers.selenium_actions import SeleniumUserActions
from instapy.drivers.selenium_actions import SeleniumPostActions
from instapy.drivers.selenium_actions import SeleniumCommentActions


class SeleniumActions(SeleniumCommonActions):
    user = None
    post = None
    comment = None

    def __init__(self):
        self.user = SeleniumUserActions()
        self.post = SeleniumPostActions()
        self.comment = SeleniumCommentActions()

    @classmethod
    def construct_actions(cls):
        if cls.user is None or cls.post is None or cls.comment is None:
            _ = SeleniumActions()
