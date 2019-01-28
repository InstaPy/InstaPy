# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
# flake8: noqa

"""InstaPy Core Library."""

# TODO: See instapy/release.py
# __variables__ with double-quoted values will be available in setup.py
__version__ = "0.1.1"

# ----------------------------------------------------------
# namespace package for instapy.extensions
# https://packaging.python.org/guides/packaging-namespace-packages/
# ----------------------------------------------------------
__path__ = __import__('pkgutil').extend_path(__path__, __name__)

# ----------------------------------------------------------
# Imports
# ----------------------------------------------------------
from . import conf  # noqa
from . import tools  # noqa

from .instapy import InstaPy  # noqa
from .util import smart_run  # noqa

# ----------------------------------------------------------
# Model classes, fields, decorators
# ----------------------------------------------------------
