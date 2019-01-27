# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from instapy import InstaPy
from instapy import smart_run

# Run InstaPy in current directory and save/update local config
session = InstaPy(script_dir=True, config_store=True)
# Initialize settings for single account
session.init_account("default")
# After init account you can add others options

with smart_run(session):
    """ Activity flow """
    # general settings
    session.set_relationship_bounds(enabled=True,
                                    delimit_by_numbers=True,
                                    max_followers=4590,
                                    min_followers=45,
                                    min_following=77)

    session.set_dont_include(["friend1", "friend2", "friend3"])
    session.set_dont_like(["pizza", "#store"])

    # activity
    session.like_by_tags(["natgeo"], amount=10)
