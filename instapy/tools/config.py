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


def _get_default_datadir():
    # REVIEW: ...
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

    def __init__(self, fname=None):
        """Constructor.

        :param fname: a shortcut allowing to instantiate :class:`configmanager`
                      from Python code without resorting to environment
                      variable

         # username=None,
         # password=None,
         # nogui=False,
         # selenium_local_session=True,
         # use_firefox=False,
         # browser_profile_path=None,
         # page_delay=25,
         # show_logs=True,
         # headless_browser=False,
         # proxy_address=None,
         # proxy_chrome_extension=None,
         # proxy_port=None,
         # disable_image_load=False,
         # bypass_suspicious_attempt=False,
         # bypass_with_mobile=False,
         # multi_logs=True):
        """
        # Section [instapy]
        self.instapy = {
            'root_path': None,
            'data_dir': _get_default_datadir() or os.environ.get('INSTAPY_DATA_DIR'),
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
            'username': None or os.environ.get('INSTA_USER'),
            'password': None or os.environ.get('INSTA_PW'),
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
            'root_path'
        ])

        self.config_file = fname

        # generate default config
        self._parse_config()

    def _parse_config(self, args=None, **kwargs):

        def notice(cond, msg):
            if cond:
                # TODO: send to logger (need fix instapy logger)
                print(msg)
                sys.exit(1)

        # REVIEW: Try use also command line parser for load or save config
        if args is None:
            args = []

        # TODO: Error
        if 'exec_dir' in kwargs:
            exec_dir = kwargs.get("exec_dir")
        else:
            exec_dir = False

        if 'config_file' in kwargs:
            config_file = kwargs.get("config_file")
        else:
            config_file = None or os.environ.get('INSTAPY_CONFIG')

        if 'config_store' in kwargs:
            config_store = kwargs.get("config_store")
        else:
            config_store = None or os.environ.get('INSTAPY_CONFIG_STORE')

        notice(not config_store and config_file and not os.access(config_file, os.R_OK),
            "The config file '%s' doesn't exist or is not readable, "\
            "use config_store=True if you want to generate it."% config_file)

        if os.name == 'nt':
            # Windows - Use exec path
            # TODO: use appdirs
            config_default_path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'instapy.conf')
        else:
            # Mac/Linux - Use home path
            # TODO: use appdirs
            if not exec_dir:
                config_default_path = os.path.expanduser('~/.instapy')
            else:
                config_default_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '.instapy'))

        self.rcfile = os.path.abspath(self.config_file or config_file or config_default_path)

        notice(config_store and os.path.isfile(self.rcfile) and os.access(self.rcfile, os.R_OK),
            "The configuration file exists and is readable; remove the config_store "\
            "parameter to avoid accidentally overwriting it")

        # Try load config file
        self.load()

        # WARNING: root_path is in blacklist - always replace the config option
        self.instapy['root_path'] = os.path.abspath(os.path.expanduser(os.path.expandvars(os.path.join(os.path.dirname(__file__), '..'))))

        if not self.instapy['extensions_path'] or self.instapy['extensions_path']=='None':
            default_extensions = []

            # InstaPy Extensions Path
            base_extensions = os.path.join(self.instapy['root_path'], 'extensions')
            if os.path.exists(base_extensions):
                default_extensions.append(base_extensions)

            # INFO: Default extensions path (Required)
            notice(not os.path.exists(base_extensions), "The directory '%s' "\
                "doesn't exist or is not readable, InstaPy require it."%
                user_extensions)

            # User Extensions Path
            user_extensions_default = os.path.abspath(os.path.join(_get_default_datadir(), '../extensions'))
            if not exec_dir and os.path.exists(user_extensions_default):
                default_extensions.append(user_extensions_default)

            user_extensions_exec = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '../extensions'))
            if exec_dir and os.path.exists(user_extensions_exec):
                default_extensions.append(user_extensions_exec)

            self.instapy['extensions_path'] = ','.join(default_extensions)
        else:
            # TODO: Fix it
            self.instapy['extensions_path'] = ",".join(
                    os.path.abspath(os.path.expanduser(os.path.expandvars(x.strip())))
                      for x in self.instapy['extensions_path'].split(','))

        if exec_dir:
            self.instapy['data_dir'] = os.path.abspath(os.path.dirname(sys.argv[0]))

        self.instapy['data_dir'] = os.path.abspath(os.path.expanduser(os.path.expandvars(self.instapy['data_dir'].strip())))

        # REVIEW: Fix all paths
        self.instapy['assets_dir'] = os.path.join(self.instapy['data_dir'], 'assets')
        self.instapy['db_dir'] = os.path.join(self.instapy['data_dir'], 'db')
        self.instapy['logs_dir'] = os.path.join(self.instapy['data_dir'], 'logs')

        # If doesn't exist try to generate it with default settings only with config_store=True
        if config_store:
            self.save()
            notice(os.path.isfile(self.rcfile) and os.access(self.rcfile, os.R_OK),
                "Configuration file successfully saved in '%s', "\
                "restart the script by removing the config_store parameter."% self.rcfile)

        # REVIEW: Fix it
        conf.extensions_paths = self.instapy['extensions_path'].split(',')

    def parse_config(self, args=None, **kwargs):
        """ Parse the configuration file (if any).

        This method initializes instapy.tools.config and
        - (wind32)    instapy.conf
        - (mac/linux) .instapy

        This method must be called before proper usage of this library can be
        made.

        Typical usage of this method:

            instapy.tools.config.parse_config(
                config_file='instapy.conf', config_store=True)
        """

        self._parse_config(args, **kwargs)
        # REVIEW: Implement init paths, only with direct parse, if used on extension with external config file

    def load(self):
        p = ConfigParser.RawConfigParser()

        try:
            p.read([self.rcfile])

            for (name,value) in p.items('instapy'):
                # OPTIMIZE: int, list, boolean, etc....
                if value=='True' or value=='true':
                    value = True
                if value=='False' or value=='false':
                    value = False
                if value=='None' or value=='none':
                    value = None
                if "ig_" in name and isinstance(ast.literal_eval(value), set):
                    value = sorted(ast.literal_eval(value))

                self.instapy[name] = value

            for (name,value) in p.items('selenium'):
                # OPTIMIZE: int, list, boolean, etc....
                if value=='True' or value=='true':
                    value = True
                if value=='False' or value=='false':
                    value = False
                if value=='None' or value=='none':
                    value = None
                self.selenium[name] = value

            # parse the other sections, as well
            for sec in p.sections():
                if sec == 'instapy' or sec == 'selenium':
                    continue
                # Check user accounts sections
                # TODO: Load to self.ig_default then copy to self.account['ig_account_name']
                if "ig_" in sec:
                    # Load user accounts from dynamic section
                    for ig_user in self.instapy['ig_accounts']:
                        user_sec = "ig_{}".format(ig_user)
                        if p.has_section(user_sec):
                            self.account.setdefault(user_sec, {})
                            for (name, value) in p.items(user_sec):
                                # OPTIMIZE: int, list, boolean, etc....
                                if value=='True' or value=='true':
                                    value = True
                                if value=='False' or value=='false':
                                    value = False
                                if value=='None' or value=='none':
                                    value = None
                                self.account[user_sec][name] = value
                else:
                    continue

                self.misc.setdefault(sec, {})

                for (name, value) in p.items(sec):
                    # OPTIMIZE: int, list, boolean, etc....
                    if value=='True' or value=='true':
                        value = True
                    if value=='False' or value=='false':
                        value = False
                    if value=='None' or value=='none':
                        value = None
                    self.misc[sec][name] = value
        except IOError:
            pass

        except ConfigParser.NoSectionError:
            pass

    def save(self):
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
            for opt in sorted(self.ig_default):
                # TODO: Check blacklist for chromedriver_min_version
                p.set(user_sec, opt, self.ig_default[opt])

        for sec in sorted(self.misc):
            p.add_section(sec)
            for opt in sorted(self.misc[sec]):
                p.set(sec,opt,self.misc[sec][opt])

        # try to create the directories and write the file
        try:
            rc_exists = os.path.exists(self.rcfile)
            if not rc_exists and not os.path.exists(os.path.dirname(self.rcfile)):
                os.makedirs(os.path.dirname(self.rcfile))
            try:
                p.write(open(self.rcfile, 'w'))
                if not rc_exists:
                    os.chmod(self.rcfile, 0o600)
            except IOError:
                sys.stderr.write("ERROR: couldn't write the config file\n")

        except OSError:
            # what to do if impossible?
            sys.stderr.write("ERROR: couldn't create the config directory\n")

    def get(self, key, default=None):
        return self.instapy.get(key, default)

    def pop(self, key, default=None):
        return self.instapy.pop(key, default)

    def get_misc(self, sect, key, default=None):
        return self.misc.get(sect,{}).get(key, default)

    def __setitem__(self, key, value):
        self.instapy[key] = value

    def __getitem__(self, key):
        return self.instapy[key]

# Self Init configmanger
config = configmanager()
