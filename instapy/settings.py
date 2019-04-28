"""
Global variables

By design, import no any other local module inside this file.
Vice verse, it'd produce circular dependent imports.
"""

from sys import platform
from os import environ as environmental_variables
from os.path import join as join_path
from os.path import exists as path_exists

from .xpath import read_xpath


WORKSPACE = {"name": "InstaPy",
             "path": environmental_variables.get("INSTAPY_WORKSPACE")}
OS_ENV = ("windows" if platform == "win32"
          else "osx" if platform == "darwin"
          else "linux")


def localize_path(*args):
    """ Join given locations as an OS path """

    if WORKSPACE["path"]:
        path = join_path(WORKSPACE["path"], *args)
        return path

    else:
        return None


class Settings:
    """ Globally accessible settings throughout whole project """

    # locations
    log_location = localize_path("logs")
    database_location = localize_path("db", "instapy.db")
    specific_chromedriver = "chromedriver_{}".format(OS_ENV)
    chromedriver_location = localize_path("assets", specific_chromedriver)
    if (not chromedriver_location
            or not path_exists(chromedriver_location)):
        chromedriver_location = localize_path("assets", "chromedriver")

    # minimum supported version of chromedriver
    chromedriver_min_version = 2.36

    # set a logger cache outside the InstaPy object to avoid
    # re-instantiation issues
    loggers = {}
    logger = None

    # set current profile credentials for DB operations
    profile = {"id": None, "name": None}

    # hold live Quota Supervisor configuration for global usage
    QS_config = {}

    # specify either connected locally or through a proxy
    connection_type = None

    # store user-defined delay time to sleep after doing actions
    action_delays = {}

    # store configuration of text analytics
    meaningcloud_config = {}
    yandex_config = {}

    # store the parameter for global access
    show_logs = None

    # store what browser the user is using, if they are using firefox it is
    # true, chrome if false.
    use_firefox = None

    # state of instantiation of InstaPy
    InstaPy_is_running = False

    # This is where currently the pods server is hosted
    pods_server_endpoint = 'https://us-central1-instapy-pods.cloudfunctions.net'

class Storage:
    """ Globally accessible standalone storage """

    # store realtime record activity data
    record_activity = {}


class Selectors:
    """
    Store XPath, CSS, and other element selectors to be used at many places
    """

    likes_dialog_body_xpath = (
        read_xpath("class_selectors","likes_dialog_body_xpath"))

    likes_dialog_close_xpath = read_xpath("class_selectors","likes_dialog_close_xpath")
