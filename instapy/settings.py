"""
Global variables

By design, import no any other local module inside this file.
Vice verse, it'd produce circular dependent imports.
"""

from sys import platform
from os import environ as environmental_variables
from os.path import join as join_path


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

    # set a logger cache outside the InstaPy object to avoid
    # re-instantiation issues
    loggers = {}
    logger = None

    # set current profile credentials for DB operations
    profile = {"id": None, "name": None}

    # hold live Quota Supervisor configuration for global usage
    QS_config = {}

    # store user-defined delay time to sleep after doing actions
    action_delays = {}

    # store configuration of text analytics
    meaningcloud_config = {}
    yandex_config = {}

    # store the parameter for global access
    show_logs = None

    # state of instantiation of InstaPy
    InstaPy_is_running = False

    # This is where currently the pods server is hosted
    pods_server_endpoint = 'https://us-central1-instapy-pods.cloudfunctions.net'

class Storage:
    """ Globally accessible standalone storage """

    # store realtime record activity data
    record_activity = {}
