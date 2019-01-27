# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

"""InstaPy Core Library."""

# ----------------------------------------------------------
# Imports
# ----------------------------------------------------------
from . import conf
from . import tools

# flake8: noqa
from .instapy import InstaPy
from .util import smart_run
from .settings import Settings

# TODO: No never need if use ConfigManager
from .file_manager import set_workspace
from .file_manager import get_workspace

# TODO: See instapy/release.py
# __variables__ with double-quoted values will be available in setup.py
__version__ = "0.1.1"

# ----------------------------------------------------------
# Model classes, fields, decorators
# ----------------------------------------------------------
