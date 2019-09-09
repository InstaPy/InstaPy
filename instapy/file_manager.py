""" file management helper functions """

# class import
from instapy.common import Settings
from .exceptions import InstaPyError

# libraries import
import os
from os.path import expanduser
from os.path import exists as path_exists
from os.path import sep as native_slash
from platform import python_version


def move_workspace(old_path, new_path):
    """ Find data files in old workspace folder and move to new location """
    # write in future


def get_home_path():
    """ Get user's home directory """

    if python_version() >= "3.5":
        from pathlib import Path

        home_dir = str(Path.home())  # this method returns slash as dir sep*
    else:
        home_dir = expanduser("~")

    home_dir = slashen(home_dir)
    home_dir = remove_last_slash(home_dir)

    return home_dir


def slashen(path, direction="forward"):
    """ Replace backslashes in paths with forward slashes """

    if direction == "forward":
        path = path.replace("\\", "/")

    elif direction == "backwards":
        path = path.replace("/", "\\")

    elif direction == "native":
        path = path.replace("/", str(native_slash))
        path = path.replace("\\", str(native_slash))

    return path


def remove_last_slash(path):
    """ Remove the last slash in the given path [if any] """

    if path.endswith("/"):
        path = path[:-1]

    return path


def differ_paths(old, new):
    """ Compare old and new paths """

    if old and old.endswith(("\\", "/")):
        old = old[:-1]
        old = old.replace("\\", "/")

    if new and new.endswith(("\\", "/")):
        new = new[:-1]
        new = new.replace("\\", "/")

    return new != old


def validate_path(path):
    """ Make sure the given path exists """

    if not path_exists(path):
        try:
            os.makedirs(path)

        except OSError as exc:
            exc_name = type(exc).__name__
            msg = '{} occured while making "{}" path!' "\n\t{}".format(
                exc_name, path, str(exc).encode("utf-8")
            )
            raise InstaPyError(msg)


def get_logfolder(username, multi_logs):
    if multi_logs:
        logfolder = "{0}{1}{2}{1}".format(Settings.log_location, native_slash, username)
    else:
        logfolder = Settings.log_location + native_slash

    validate_path(logfolder)
    return logfolder
