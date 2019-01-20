# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
"""Quickstart script for InstaPy Extension Test."""

from instapy import InstaPy
# imports for test_extesion
from instapy.util import web_address_navigator

# login credentials
insta_username = ''
insta_password = ''


def test_extension(self):
    """Add a custom feature on InstaPy."""
    if self.aborting:
        return

    home_link = 'https://www.instagram.com/'
    web_address_navigator(self.browser, home_link)

    self.logger.info("test_extension() working!!!")

    return


def test_ext_params(self, check=None):
    """Add Another test."""
    if self.aborting:
        return

    self.logger.info("test_ext_params({}) working!!!".format(str(check)))

    return


def get_session():
    """Initialize Instance of InstaPy."""
    instapy_instance = InstaPy(username=insta_username,
                               password=insta_password)

    # Load Custom Extension Function
    instapy_instance.load_extensions(test_extension)
    # WARNING: Only for Testing
    instapy_instance.load_extensions(test_extension)
    # Another Function
    instapy_instance.load_extensions(test_ext_params)
    # Print list extensions
    instapy_instance.get_extensions()

    return instapy_instance


if __name__ == '__main__':
    session = get_session()
    session.login()
    session.test_extension()
    session.test_ext_params("arg-passed")
    session.end()
