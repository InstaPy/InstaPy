"""
class that combines all the exposed methods to simplify
the creation of the WebDriver
common methods are inherited (so visible at the top layer)
specific method are callable by AppiumActions.user.method
etc...
"""

from .appium_common_actions import  AppiumCommonActions
from .appium_user_actions import AppiumUserActions
from .appium_post_actions import AppiumPostActions
from .appium_comment_actions import AppiumCommentActions


class AppiumActions(AppiumCommonActions):
    user = None
    post = None
    comment = None

    def __init__(self):
        self.user = AppiumUserActions()
        self.post = AppiumPostActions()
        self.comment = AppiumCommentActions()

    @classmethod
    def construct_actions(cls):
        if cls.user is None or cls.post is None or cls.comment is None:
            _ = AppiumActions()
