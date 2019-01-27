# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

"""Global Configuration variables."""

from ..tools import osutil

log_location = None
database_location = None

specific_chromedriver = "chromedriver_{}".format(osutil.OS_ENV)
chromedriver_location = None

# minimum supported version of chromedriver
chromedriver_min_version = 2.36

# set a logger cache outside the InstaPy object to avoid
# re-instantiation issues
loggers = {}
logger = None

# set current profile credentials for DB operations
profile = {"id": None, "name": None}

# hold live Quota Supervisor configuration for global usage
QS_config = {}

# specify either connected locally or through a proxy
connection_type = None

# store user-defined delay time to sleep after doing actions
action_delays = {}

# store configuration of text analytics
meaningcloud_config = {}
yandex_config = {}

# store the parameter for global access
show_logs = None

# store what browser the user is using, if they are using firefox it is
# true, chrome if false.
use_firefox = None

# state of instantiation of InstaPy
InstaPy_is_running = False

# Paths to search for InstaPy extensions.
extensions_paths = []

# TODO: Move all parameters of settings.py here
