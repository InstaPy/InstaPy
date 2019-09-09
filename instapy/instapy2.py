"""main class for InstaPy"""

from instapy.drivers import WebDriver
from instapy.engine import LegacyEngine
from instapy.common import Logger
from instapy.setting import Settings

from .file_manager import get_workspace
from .file_manager import get_logfolder
from .database_engine import get_database

from sys import platform
from os import environ as environmental_variables
from os.path import join as join_path

class InstaPy2():
    """Class to be instantiated to use in script"""

    WORKSPACE = {
        "name": "InstaPy",
        "path": environmental_variables.get("INSTAPY_WORKSPACE"),
    }
    OS_ENV = (
        "windows" if platform == "win32" else "osx" if platform == "darwin" else "linux"
    )

    def __init__(
            self,
            username: str = None,
            password: str = None,
            driver_type: str = WebDriver.SELENIUM_DRIVER,
            **kwargs
    ):
        print("InstaPy Version: {}".format(__version__))
        cli_args = parse_cli_args()
        self.settings = Settings()

        # necessary init in the static class to be able to work
        # most of those vars are used only one and should be encapsulated into their own class
        # settings should really only have what needs to be common to all
        # for the moment backward compatibility with legacy code
        self.settings.username = cli_args.username or os.environ.get("INSTA_USER") or username
        self.settings.password = cli_args.password or os.environ.get("INSTA_PW") or password
        self.settings.page_delay = cli_args.page_delay or kwargs.get("page_delay") or 25
        self.settings.headless_browser = cli_args.headless_browser or kwargs.get("headless_browser") or False
        self.settings.proxy_address = cli_args.proxy_address or kwargs.get("proxy_address") or None
        self.settings.proxy_port = cli_args.proxy_port or kwargs.get("proxy_port") or None
        self.setting.proxy_username = cli_args.proxy_username or kwargs.get("proxy_username") or None
        self.setting.proxy_username = cli_args.proxy_password or kwargs.get("proxy_password") or None
        self.settings.disable_image_load = cli_args.disable_image_load or kwargs.get("disable_image_load") or False
        self.settings.split_db = cli_args.split_db or kwargs.get("split_db") or None
        self.settings.browser_profile_path =  kwargs.get("browser_profile_path") or None
        self.settings.geckodriver_path = kwargs.get("geckodriver_path") or None

        self.driver = WebDriver(driver_type)

        # assign logger

        self.logger = Logger(username,
                        get_logfolder(self.username, kwargs.get("multi_logs") or True),
                                      kwargs.get("show_logs") or None, kwargs.get("log_handler") or None)

        self.settings.InstaPy_is_running = True
        # workspace must be ready before anything
        if not get_workspace():
            raise InstaPyError("Oh no! I don't have a workspace to work at :'(")

        # virtual display to hide browser (not supported on Windows)
        self.setting.nogui =  kwargs.get("nogui") or False
        if self.setting.nogui:
            if not platform.startswith("win32"):
                self.display = Display(visible=0, size=(800, 600))
                self.display.start()
            else:
                raise InstaPyError("The 'nogui' parameter isn't supported on Windows.")

        self.settings.bypass_security_challenge_using = kwargs.get("bypass_security_challenge_using") or "email"

        # choose environment over static typed credentials

        self.settings.profile["name"] = self.settings.username

        self.settings.split_db = kwargs.get("split_db") or False
        if self.settings.split_db:
            self.settings.database_location = self._localize_path(
                "db", "instapy_{}.db".format(self.username)
            )

        get_database(make=True)  # IMPORTANT: think twice before relocating

    @staticmethod
    def _localize_path(*args):
        """ Join given locations as an OS path """

        if WORKSPACE["path"]:
            path = join_path(WORKSPACE["path"], *args)
            return path

        else:
            return None