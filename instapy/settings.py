"""
Global variables

By design, import no any other local module inside this file.
Vice verse, it'd produce circular dependent imports.

TODO: for global parameters use instapy/conf/__ init__.py
"""

class Storage:
    """ Globally accessible standalone storage """

    # store realtime record activity data
    record_activity = {}


class Selectors:
    """
    Store XPath, CSS, and other element selectors to be used at many places
    """

    likes_dialog_body_xpath = (
        "//h1[text()='Likes']/../../following-sibling::div/div")

    likes_dialog_close_xpath = "//span[contains(@aria-label, 'Close')]"
