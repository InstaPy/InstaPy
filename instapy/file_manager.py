""" A file management utility """

import os
import pkg_resources
from os.path import expanduser
from os.path import exists as path_exists
from os.path import isfile as file_exists
from os.path import sep as native_slash
from platform import python_version

from instapy_chromedriver import binary_path

from .util import highlight_print

from . import conf
from .tools import config
from .tools import osutil

from .exceptions import InstaPyError


def move_workspace(old_path, new_path):
    """ Find data files in old workspace folder and move to new location """
    # write in future
    # TODO: Feature added to migration, review from bitbucket and pull it to github


def validate_path(path):
    """ Make sure the given path exists """

    # TODO: Move to tools/osutil.py

    if not path_exists(path):
        try:
            os.makedirs(path)

        except OSError as exc:
            exc_name = type(exc).__name__
            msg = ("{} occured while making \"{}\" path!"
                   "\n\t{}".format(exc_name,
                                   path,
                                   str(exc).encode("utf-8")))
            raise InstaPyError(msg)


def get_chromedriver_location():
    """ Solve chromedriver access issues """

    # TODO: Move to configmanager

    CD = conf.chromedriver_location

    if osutil.OS_ENV == "windows":
        if not CD.endswith(".exe"):
            CD += ".exe"

    if not file_exists(CD):
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

    validate_path(logfolder)
    return logfolder
