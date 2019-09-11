"""main class for InstaPy"""

# class import
from instapy.drivers import WebDriver
from instapy.common import Logger
from instapy.common import Settings
from instapy.common import DatabaseEngine
from instapy.common import Stats

# helper import
from .file_manager import get_logfolder
from .file_manager import get_home_path
from .file_manager import slashen
from .file_manager import validate_path
from .file_manager import remove_last_slash

from .exceptions import InstaPyError
from . import __version__

# libraries import
from sys import platform
import os
from os import environ as environmental_variables
from os.path import join as join_path
from os.path import sep as native_slash
from argparse import ArgumentParser

from platform import python_version
from pyvirtualdisplay import Display


class InstaPy2:
    """Class to be instantiated to use in script
        has 3 subclasses that are instantiated
        .settings contains all the set_ parameters and functions
        .stats contains all the current numbers for current session
        .driver the correct instantiated webdriver in use for that session
        .logger the Logger instance
    """

    def __init__(self, driver_type: str = WebDriver.SELENIUM_DRIVER, **kwargs):
        print("InstaPy Version: {}".format(__version__))

        self.WORKSPACE = {
            "name": "InstaPy",
            "path": environmental_variables.get("INSTAPY_WORKSPACE"),
        }
        self.OS_ENV = (
            "windows"
            if platform == "win32"
            else "osx"
            if platform == "darwin"
            else "linux"
        )

        cli_args = self._parse_cli_args()
        self.settings = Settings()

        # necessary init in the static class to be able to work
        # most of those vars are used only one and should be encapsulated into their own class
        # settings should really only have what needs to be common to all
        # for the moment backward compatibility with legacy code
        self.settings.username = (
            cli_args.username or os.environ.get("INSTA_USER") or kwargs.get("username")
        )
        self.settings.password = (
            cli_args.password or os.environ.get("INSTA_PW") or kwargs.get("password")
        )
        self.settings.page_delay = cli_args.page_delay or kwargs.get("page_delay") or 25
        self.settings.headless_browser = (
            cli_args.headless_browser or kwargs.get("headless_browser") or False
        )
        self.settings.proxy_address = (
            cli_args.proxy_address or kwargs.get("proxy_address") or None
        )
        self.settings.proxy_port = (
            cli_args.proxy_port or kwargs.get("proxy_port") or None
        )
        self.settings.proxy_username = (
            cli_args.proxy_username or kwargs.get("proxy_username") or None
        )
        self.settings.proxy_username = (
            cli_args.proxy_password or kwargs.get("proxy_password") or None
        )
        self.settings.disable_image_load = (
            cli_args.disable_image_load or kwargs.get("disable_image_load") or False
        )
        self.settings.split_db = cli_args.split_db or kwargs.get("split_db") or None
        self.settings.browser_profile_path = kwargs.get("browser_profile_path") or None
        self.settings.geckodriver_path = kwargs.get("geckodriver_path") or None

        self.settings.devicename = kwargs.get("devicename") or 'emulator-5554'
        self.settings.devicetimeout = kwargs.get("devicetimeout") or 600
        self.settings.client_host = kwargs.get("client_host") or '127.0.0.1'
        self.settings.client_port = kwargs.get("client_port") or 5037


        self.driver = WebDriver(driver_type)

        # assign logger

        self.logger = Logger(
            self.settings.username,
            get_logfolder(self.username, kwargs.get("multi_logs") or True),
            kwargs.get("show_logs") or None,
            kwargs.get("log_handler") or None,
        )

        self.settings.InstaPy_is_running = True
        # workspace must be ready before anything
        if not self._get_workspace():
            raise InstaPyError("Oh no! I don't have a workspace to work at :'(")

        # virtual display to hide browser (not supported on Windows)
        self.setting.nogui = kwargs.get("nogui") or False
        if self.setting.nogui:
            if not platform.startswith("win32"):
                self.display = Display(visible=0, size=(800, 600))
                self.display.start()
            else:
                raise InstaPyError("The 'nogui' parameter isn't supported on Windows.")

        self.settings.bypass_security_challenge_using = (
            kwargs.get("bypass_security_challenge_using") or "email"
        )

        # choose environment over static typed credentials

        self.settings.profile["name"] = self.settings.username

        self.settings.split_db = kwargs.get("split_db") or False
        if self.settings.split_db:
            self.settings.database_location = self._localize_path(
                "db", "instapy_{}.db".format(self.username)
            )

        DatabaseEngine.get_database(make=True)  # IMPORTANT: think twice before relocating

        #stats
        self.stats = Stats()



    def use_assets(self):
        """Get asset folder"""
        assets_path = "{}{}assets".format(self._use_workspace(), native_slash)
        validate_path(assets_path)
        return assets_path

    def _localize_path(self, *args):
        """ Join given locations as an OS path """

        if self.WORKSPACE["path"]:
            path = join_path(self.WORKSPACE["path"], *args)
            return path

        else:
            return None

    def _use_workspace(self):
        """Get workspace folder"""
        workspace_path = slashen(self.WORKSPACE["path"], "native")
        validate_path(workspace_path)
        return workspace_path

    def _get_workspace(self):
        """ Make a workspace ready for user """

        if self.WORKSPACE["path"]:
            workspace = self._verify_workspace_name(self.WORKSPACE["path"])

        else:
            home_dir = get_home_path()
            workspace = "{}/{}".format(home_dir, self.WORKSPACE["name"])

        message = 'Workspace in use: "{}"'.format(workspace)
        Logger.highlight_print(Settings.profile["name"], message, "workspace", "info")
        self._update_workspace(workspace)
        self.update_locations()
        return self.WORKSPACE

    def _update_workspace(self, latest_path):
        """ Update the workspace constant with its latest path """

        latest_path = slashen(latest_path, "native")
        validate_path(latest_path)
        self.WORKSPACE.update(path=latest_path)

    def update_locations(self):
        """
        As workspace has changed, locations also should be updated

        If the user already has set a location, do not alter it
        """

        # update logs location
        if not Settings.log_location:
            Settings.log_location = self._localize_path("logs")

        # update database location
        if not Settings.database_location:
            Settings.database_location = self._localize_path("db", "instapy.db")

    def _verify_workspace_name(self, path):
        """ Make sure chosen workspace name is InstaPy friendly """

        path = slashen(path)
        path = remove_last_slash(path)
        custom_workspace_name = path.split("/")[-1]
        default_workspace_name = self.WORKSPACE["name"]

        if default_workspace_name not in custom_workspace_name:
            if default_workspace_name.lower() not in custom_workspace_name.lower():
                path += "/{}".format(default_workspace_name)
            else:
                nicer_name = custom_workspace_name.lower().replace(
                    default_workspace_name.lower(), default_workspace_name
                )
                path = path.replace(custom_workspace_name, nicer_name)

        return path

    class CustomizedArgumentParser(ArgumentParser):
        """
         Subclass ArgumentParser in order to turn off
        the abbreviation matching on older pythons.

        `allow_abbrev` parameter was added by Python 3.5 to do it.
        Thanks to @paul.j3 - https://bugs.python.org/msg204678 for this solution.
        """

        def _get_option_tuples(self, option_string):
            """
             Default of this method searches through all possible prefixes
            of the option string and all actions in the parser for possible
            interpretations.

            To view the original source of this method, running,
            ```
            import inspect; import argparse; inspect.getsourcefile(argparse)
            ```
            will give the location of the 'argparse.py' file that have this method.
            """
            return []

    @staticmethod
    def _parse_cli_args():
        """ Parse arguments passed by command line interface """

        AP_kwargs = dict(
            prog="InstaPy",
            description="Parse InstaPy constructor's arguments",
            epilog="And that's how you'd pass arguments by CLI..",
            conflict_handler="resolve",
        )
        if python_version() < "3.5":
            parser = InstaPy2.CustomizedArgumentParser(**AP_kwargs)
        else:
            AP_kwargs.update(allow_abbrev=False)
            parser = ArgumentParser(**AP_kwargs)

        """ Flags that REQUIRE a value once added
        ```python quickstart.py --username abc```
        """
        parser.add_argument("-u", "--username", help="Username", type=str, metavar="abc")
        parser.add_argument("-p", "--password", help="Password", type=str, metavar="123")
        parser.add_argument(
            "-pd", "--page-delay", help="Implicit wait", type=int, metavar=25
        )
        parser.add_argument(
            "-pa", "--proxy-address", help="Proxy address", type=str, metavar="192.168.1.1"
        )
        parser.add_argument(
            "-pp", "--proxy-port", help="Proxy port", type=int, metavar=8080
        )

        """ Auto-booleans: adding these flags ENABLE themselves automatically
        ```python quickstart.py --use-firefox```
        """
        parser.add_argument(
            "-uf", "--use-firefox", help="Use Firefox", action="store_true", default=None
        )
        parser.add_argument(
            "-hb",
            "--headless-browser",
            help="Headless browser",
            action="store_true",
            default=None,
        )
        parser.add_argument(
            "-dil",
            "--disable-image-load",
            help="Disable image load",
            action="store_true",
            default=None,
        )
        parser.add_argument(
            "-bsa",
            "--bypass-suspicious-attempt",
            help="Bypass suspicious attempt",
            action="store_true",
            default=None,
        )
        parser.add_argument(
            "-bwm",
            "--bypass-with-mobile",
            help="Bypass with mobile phone",
            action="store_true",
            default=None,
        )
        parser.add_argument(
            "-sdb",
            "--split-db",
            help="Split sqlite-db as instapy_{username}.db",
            action="store_true",
            default=None,
        )
        parser.add_argument(
            "-pu",
            "--proxy-username",
            help="Proxy username",
            action="store_true",
            default=None
        )
        parser.add_argument(
            "-ppw",
            "--proxy-password",
            help="Proxy password",
            action="store_true",
            default=None
        )

        """ Style below can convert strings into booleans:
        ```parser.add_argument("--is-debug",
                               default=False,
                               type=lambda x: (str(x).capitalize() == "True"))```

        So that, you can pass bool values explicitly from CLI,
        ```python quickstart.py --is-debug True```

        NOTE: This style is the easiest of it and currently not being used.
        """

        args, _ = parser.parse_known_args()
        # Once added custom arguments if you use a reserved name of core flags
        # and don't parse it, e.g.,
        # `-ufa` will misbehave cos it has `-uf` reserved flag in it.
        # But if you parse it, it's okay.

        return args
