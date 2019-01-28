# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser


import os
import sys
import ast

import errno
# import logging

from .. import release, conf
from . import appdirs

# TODO: integrate highlight_print
# from ..util import highlight_print
# message = "Given workspace path is identical as current :/"
# highlight_print(conf.profile["name"],
#                 message,
#                 "workspace",
#                 "info",
#                 conf.logger)


def _get_default_datadir():
    # REVIEW: Use product_name like directory for default path
    home = os.path.expanduser('~')

    if os.path.isdir(home):
        func = appdirs.user_data_dir
    else:
        if sys.platform in ['win32', 'darwin']:
            func = appdirs.site_data_dir
        else:
            func = lambda **kwarg: "/var/lib/%s" % kwarg['appname'].lower()

    return func(appname=release.product_name, appauthor=release.author)


class configmanager(object):
    """Config Manager Class."""

    def __init__(self, fname=None):
        """Constructor.

        :param fname: a shortcut allowing to instantiate :class:`configmanager`
                      from Python code without resorting to environment
                      variable
        """
        # Section [instapy]
        self.instapy = {
            'root_path': None,
            'dev_mode': "pdb",
            'data_dir': _get_default_datadir() or os.environ.get(
                                                'INSTAPY_DATA_DIR'),
            'assets_dir': None,
            'db_dir': None,
            'logs_dir': None,
            'extensions_path': None,
            'log_level': None,
            # show_logs=True
            'console_logs': True,
            'nogui': False,
            'ig_accounts': set(["default"])
        }
        # Section [selenium]
        self.selenium = {
            # TODO: next add chromedriver_min_version
            'selenium_local_session': True,
            'browser_profile_path': None,
            'use_firefox': False,
            'proxy_chrome_extension': None,
            'headless_browser': False,
            'disable_image_load': False
        }
        # Section [ig_default, ig_yourusername]
        # TODO: Load first here any user sections then copy to self.account
        self.ig_default = {
            # REVIEW: next update allow custom user data dir for logs, etc.. or
            #         sqlite3 database
            # TODO: change env name INSTA_ to INSTAPY_
            'username': "insta_username" or os.environ.get('INSTA_USER'),
            'password': "insta_password" or os.environ.get('INSTA_PW'),
            # multi_logs=True
            'save_logs': True,
            'bypass_suspicious_attempt': False,
            'bypass_with_mobile': False,
            'page_delay': 25,
            'proxy_address': None,
            'proxy_port': 0
        }
        # Section IG_Accounts
        self.account = {}

        # Section - Any others
        self.misc = {}

        # Not exposed in the configuration file.
        self.blacklist_for_save = set([
            # TODO: next add chromedriver_min_version
            'root_path', 'dev_mode'
        ])

        self.config_file = fname

        # generate default config
        self._parse_config()

    def _parse_config(self, args=None, **kwargs):
        """
        Parse Config (Internal use).
        """

        def notice(cond, msg):
            if cond:
                # TODO: send to logger (need fix instapy logger)
                print(msg)
                sys.exit(1)

        # REVIEW: Try use also command line parser for load or save config
        if args is None:
            args = []

        # TODO: Error
        if 'script_dir' in kwargs:
            script_dir = kwargs.get("script_dir")
        else:
            script_dir = False

        if 'config_file' in kwargs:
            config_file = kwargs.get("config_file")
        else:
            config_file = None or os.environ.get('INSTAPY_CONFIG')

        if 'config_store' in kwargs:
            config_store = kwargs.get("config_store")
        else:
            config_store = None or os.environ.get('INSTAPY_CONFIG_STORE')

        notice(not config_store and config_file and
            not os.access(config_file, os.R_OK),
            "The config file '%s' doesn't exist or is not readable, "\
            "use config_store=True if you want to generate it."% config_file)

        if os.name == 'nt':
            # Windows - Use exec path
            # TODO: use appdirs
            config_default_path = os.path.join(
                os.path.abspath(os.path.dirname(sys.argv[0])), 'instapy.conf')
        else:
            # Mac/Linux - Use home path
            # TODO: use appdirs
            if not script_dir:
                config_default_path = os.path.expanduser('~/.instapy')
            else:
                config_default_path = os.path.abspath(
                    os.path.join(os.path.dirname(sys.argv[0]), '.instapy'))

        self.rcfile = os.path.abspath(
            self.config_file or config_file or config_default_path)

        # Try load config file
        self.load()

        # WARNING: root_path is in blacklist - always replace the config option
        self.instapy['root_path'] = os.path.abspath(
            os.path.expanduser(os.path.expandvars(
                os.path.join(os.path.dirname(__file__), '..'))))

        if not self.instapy['extensions_path'] or \
                self.instapy['extensions_path'] == 'None':

            default_extensions = []

            # InstaPy Extensions Path
            base_extensions = os.path.join(
                self.instapy['root_path'], 'extensions')
            if os.path.exists(base_extensions):
                default_extensions.append(base_extensions)

            # INFO: Default extensions path (Required)
            notice(not os.path.exists(base_extensions), "The directory '%s' "\
                "doesn't exist or is not readable, InstaPy require it."%
                base_extensions)

            # User Extensions Path
            user_extensions_default = os.path.abspath(
                os.path.join(_get_default_datadir(), '../extensions'))
            if not script_dir and os.path.exists(user_extensions_default):
                default_extensions.append(user_extensions_default)

            user_extensions_exec = os.path.abspath(
                os.path.join(os.path.dirname(sys.argv[0]), '../extensions'))
            if script_dir and os.path.exists(user_extensions_exec):
                default_extensions.append(user_extensions_exec)

            self.instapy['extensions_path'] = ','.join(default_extensions)
        else:
            # TODO: Fix it
            self.instapy['extensions_path'] = ",".join(
                    os.path.abspath(os.path.expanduser(
                        os.path.expandvars(
                            x.strip()))
                        ) for x in self.instapy['extensions_path'].split(','))

        if script_dir:
            self.instapy['data_dir'] = os.path.abspath(
                os.path.dirname(sys.argv[0]))

        self.instapy['data_dir'] = os.path.abspath(
            os.path.expanduser(os.path.expandvars(
                self.instapy['data_dir'].strip())))

        # REVIEW: Fix all paths
        self.instapy['assets_dir'] = os.path.join(
            self.instapy['data_dir'], 'assets')
        self.instapy['db_dir'] = os.path.join(
            self.instapy['data_dir'], 'db')
        self.instapy['logs_dir'] = os.path.join(
            self.instapy['data_dir'], 'logs')

        # If doesn't exist try to generate it with default settings
        if config_store:
            self.save()

        # Used for load default user account
        if not os.path.isfile(self.rcfile) and len(self.account) == 0:
            self.account.setdefault("ig_default", self.ig_default)

        # Update all conf variables
        conf.extensions_paths = self.instapy['extensions_path'].split(',')
        conf.log_location = self.instapy['logs_dir']
        conf.database_location = os.path.join(
            self.instapy['db_dir'], 'instapy.db')
        # Chromelocation is fixed from PR #3829 leave at None

    def parse_config(self, args=None, **kwargs):
        """ Parse the configuration file (if any).

        This method initializes instapy.tools.config and
        - (win32)    instapy.conf
        - (mac/linux) .instapy

        This method must be called before proper usage of this library can be
        made.

        Typical usage of this method:

            instapy.tools.config.parse_config(
                config_file='instapy.conf', config_store=True)
        """

        self._parse_config(args, **kwargs)

        # TODO: Implement init paths, only with direct parse,
        #         if used on extension with external config file

    def load(self):
        """Load Config File."""

        p = ConfigParser.RawConfigParser()

        try:
            p.read([self.rcfile])

            for (name, value) in p.items('instapy'):
                # OPTIMIZE: int, list, boolean, etc....
                if value == 'True' or value == 'true':
                    value = True
                if value == 'False' or value == 'false':
                    value = False
                if value == 'None' or value == 'none':
                    value = None
                if "ig_" in name and isinstance(
                            set(sorted(ast.literal_eval(value))), set):
                    value = set(sorted(ast.literal_eval(value)))

                self.instapy[name] = value

            for (name, value) in p.items('selenium'):
                # OPTIMIZE: int, list, boolean, etc....
                if value == 'True' or value == 'true':
                    value = True
                if value == 'False' or value == 'false':
                    value = False
                if value == 'None' or value == 'none':
                    value = None
                self.selenium[name] = value

            # parse the other sections, as well
            for sec in p.sections():
                if sec == 'instapy' or sec == 'selenium':
                    continue
                # Check user accounts sections
                # TODO: Load to self.ig_default then copy to
                #       self.account['ig_account_name']
                if "ig_" in sec:
                    # Load user accounts from dynamic section
                    for ig_user in self.instapy['ig_accounts']:
                        user_sec = "ig_{}".format(ig_user)
                        if p.has_section(user_sec):
                            self.account.setdefault(user_sec, {})
                            for (name, value) in p.items(user_sec):
                                # OPTIMIZE: int, list, boolean, etc....
                                if value == 'True' or value == 'true':
                                    value = True
                                if value == 'False' or value == 'false':
                                    value = False
                                if value == 'None' or value == 'none':
                                    value = None
                                self.account[user_sec][name] = value
                else:
                    # Load others sections
                    self.misc.setdefault(sec, {})

                    for (name, value) in p.items(sec):
                        # OPTIMIZE: int, list, boolean, etc....
                        if value == 'True' or value == 'true':
                            value = True
                        if value == 'False' or value == 'false':
                            value = False
                        if value == 'None' or value == 'none':
                            value = None
                        self.misc[sec][name] = value

        except IOError:
            """TODO: Add Debugger tools/debugger."""
            pass

        except ConfigParser.NoSectionError:
            """TODO: Add Debugger tools/debugger."""
            pass

    def save(self):
        """Save Config File."""

        p = ConfigParser.RawConfigParser()

        p.add_section('instapy')
        for opt in sorted(self.instapy):
            if opt in self.blacklist_for_save:
                continue
            else:
                p.set('instapy', opt, self.instapy[opt])

        p.add_section('selenium')
        for opt in sorted(self.selenium):
            p.set('selenium', opt, self.selenium[opt])

        # Save user default account with default settings
        for ig_user in self.instapy['ig_accounts']:
            user_sec = "ig_{}".format(ig_user)
            p.add_section(user_sec)
            if len(self.account) == 0:
                # Save default values
                for opt in sorted(self.ig_default):
                    # TODO: Check blacklist for chromedriver_min_version
                    p.set(user_sec, opt, self.ig_default[opt])
            else:
                # Save account values
                for opt in sorted(self.account[user_sec]):
                    # TODO: Check blacklist for chromedriver_min_version
                    p.set(user_sec, opt, self.account[user_sec][opt])

        for sec in sorted(self.misc):
            p.add_section(sec)
            for opt in sorted(self.misc[sec]):
                p.set(sec, opt, self.misc[sec][opt])

        # try to create the directories and write the file
        try:
            rc_exists = os.path.exists(self.rcfile)
            if not rc_exists and not os.path.exists(
                    os.path.dirname(self.rcfile)):
                os.makedirs(os.path.dirname(self.rcfile))
            try:
                p.write(open(self.rcfile, 'w'))
                if not rc_exists:
                    os.chmod(self.rcfile, 0o600)

            except IOError:
                sys.stderr.write("ERROR: couldn't write the config file\n")
                """TODO: Add Debugger tools/debugger."""

        except OSError:
            # what to do if impossible?
            sys.stderr.write("ERROR: couldn't create the config directory\n")
            """TODO: Add Debugger tools/debugger."""

    def get(self, key, default=None):
        return self.instapy.get(key, default)

    def pop(self, key, default=None):
        return self.instapy.pop(key, default)

    def get_misc(self, sect, key, default=None):
        return self.misc.get(sect, {}).get(key, default)

    def __setitem__(self, key, value):
        self.instapy[key] = value

    def __getitem__(self, key):
        return self.instapy[key]

    def verify_account(self, account_name):
        enabled_account = self.instapy['ig_accounts']
        stored_account = self.account["ig_{}".format(account_name)]

        if not stored_account:
            return False
        if account_name not in enabled_account:
            return False

        return True

    def validate_path(self, path):
        pass

    def get_chromedriver_location(self):
        pass


# Self Init configmanger
config = configmanager()
