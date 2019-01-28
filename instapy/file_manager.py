""" A file management utility """

import pkg_resources

from os.path import isfile as file_exists
from os.path import sep as native_slash

from instapy_chromedriver import binary_path

from .util import highlight_print

from . import conf
from .tools import osutil

from .exceptions import InstaPyError


def move_workspace(old_path, new_path):
    """ Find data files in old workspace folder and move to new location """
    # write in future
    # TODO: Feature added to migration, review from bitbucket and pull it to github


def get_chromedriver_location():
    """ Solve chromedriver access issues """

    # TODO: Move to configmanager

    CD = conf.chromedriver_location

    if osutil.OS_ENV == "windows":
        if not CD.endswith(".exe"):
            CD += ".exe"

    if not CD or not file_exists(CD):
        CD = binary_path
        chrome_version = pkg_resources.get_distribution(
                                    "instapy_chromedriver").version
        message = "Using built in instapy-chromedriver"\
                  " executable (version {})".format(chrome_version)
        highlight_print(conf.profile["name"],
                        message,
                        "workspace",
                        "info",
                        conf.logger)

    # save updated path into settings
    conf.chromedriver_location = CD
    return CD


def get_logfolder(username, multi_logs):

    if multi_logs:
        logfolder = "{0}{1}{2}{1}".format(conf.log_location,
                                          native_slash,
                                          username)
    else:
        logfolder = (conf.log_location + native_slash)

    osutil.validate_path(logfolder)
    return logfolder
