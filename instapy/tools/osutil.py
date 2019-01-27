# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from sys import platform

OS_ENV = ("windows" if platform == "win32"
          else "osx" if platform == "darwin"
          else "linux")
