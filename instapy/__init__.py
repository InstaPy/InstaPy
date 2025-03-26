# flake8: noqa

# __variables__ with double-quoted values will be available in setup.py
__version__ = "0.6.16"

from .file_manager import get_workspace, set_workspace
from .instapy import InstaPy
from .settings import Settings
from .util import smart_run
