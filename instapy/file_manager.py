""" A file management utility """

import os
from os.path import expanduser
from os.path import exists as path_exists
from os.path import isfile as file_exists
from os.path import sep as native_slash
from platform import python_version

from .util import highlight_print

from . import conf
from .tools import config
from .tools import osutil

from .exceptions import InstaPyError


def move_workspace(old_path, new_path):
    """ Find data files in old workspace folder and move to new location """
    # write in future
    # TODO: Feature added to migration, review from bitbucket and pull it to github


def update_locations():
    """
    As workspace has changed, locations also should be updated

    If the user already has set a location, do not alter it
    """

    configmanager = config

    # update logs location
    if not conf.log_location:
        conf.log_location = configmanager.instapy['logs_dir']

    # update database location
    if not conf.database_location:
        conf.database_location = os.path.join(configmanager.instapy['db_dir'], 'instapy.db')

    # update chromedriver location
    if not conf.chromedriver_location:
        conf.chromedriver_location = os.path.join(configmanager.instapy['assets_dir'], conf.specific_chromedriver)

        if (not conf.chromedriver_location
                or not path_exists(conf.chromedriver_location)):
            conf.chromedriver_location = os.path.join(configmanager.instapy['assets_dir'], "chromedriver")


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

    update_locations()

    CD = conf.chromedriver_location

    if osutil.OS_ENV == "windows":
        if not CD.endswith(".exe"):
            CD += ".exe"

    if not file_exists(CD):
        msg = ("Oops! Please, put chromedriver executable to the \"{}\" folder"
               " and start again :]"
               .format(CD))
        raise InstaPyError(msg)

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
