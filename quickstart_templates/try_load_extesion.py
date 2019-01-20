# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

""" Quickstart script for InstaPy usage """

from instapy import InstaPy
# imports for test_extesion
from instapy.util import web_address_navigator

# login credentials
insta_username = ''
insta_password = ''


def test_extesion(self):
    """Add a custom feature on InstaPy."""
    if self.aborting:
        return

    home_link = 'https://www.instagram.com/'
    web_address_navigator(self.browser, home_link)

    return


def get_session():
    """Initialize Instance of InstaPy."""
    instapy_instance = InstaPy(username=insta_username,
                               password=insta_password,
                               selenium_local_session=True)

    instapy_instance.load_extensions(test_extesion)

    return instapy_instance


if __name__ == '__main__':
    session = get_session()
    session.login()
    session.test_extesion()
    session.end()
