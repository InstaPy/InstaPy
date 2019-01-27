# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import importlib
import types
import sys

# post_mortem supported
SUPPORTED_DEBUGGER = {'pdb', 'ipdb', 'wdb', 'pudb'}


def post_mortem(config, info):
    """Start debugger if is enabled in config."""

    if config['dev_mode'] and isinstance(info[2], types.TracebackType):
        debug = next((opt for opt in config['dev_mode'] if opt in SUPPORTED_DEBUGGER), None)

        if debug:
            try:
                # Try to import the xpdb from config (pdb, ipdb, pudb, ...)
                importlib.import_module(debug).post_mortem(info[2])
            except ImportError:
                # TODO: Send to InstaPy Exception
                print('Error while importing %s.' % debug)
                sys.exit(1)
