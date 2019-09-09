# flake8: noqa

# __variables__ with double-quoted values will be available in setup.py
__version__ = "0.7.0"

from .instapy2 import InstaPy2
from .util import smart_run
from instapy.common.settings import Settings
from .file_manager import set_workspace
from .file_manager import get_workspace
