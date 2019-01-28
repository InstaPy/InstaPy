# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import os
from sys import platform

from os.path import exists as path_exists

from ..exceptions import InstaPyError

OS_ENV = ("windows" if platform == "win32"
          else "osx" if platform == "darwin"
          else "linux")


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
