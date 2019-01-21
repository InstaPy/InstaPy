# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

"""InstaPy Core Library."""

# Check Python version
import sys
assert sys.version_info > (2, 7), "InstaPy requires Python >= 2.7 to run."


# flake8: noqa
from .settings import Settings  # noqa: E402
from .instapy import InstaPy  # noqa: E402
