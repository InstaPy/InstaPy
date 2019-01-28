# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

"""
    Example Config File -> configmanager_multi.conf

    Require: schedule library
"""

import time
import schedule
import threading

from instapy import InstaPy
from instapy.exceptions import InstaPyError


def run_threaded(job_func):
    """Manage Thread."""
    job_id = "thId-"+str(job_func.__name__)
    if job_id not in [x.getName() for x in threading.enumerate()]:
        job_thread = threading.Thread(target=job_func, name=job_id)
        job_thread.start()


def InstaPy_Init():
    """Return InstaPy Instance."""
    return InstaPy(config_store=True)


def InstaPy_Commons(session):
    """Clarifai - Same settings for all accounts."""
    session.set_use_clarifai(
        enabled=True, api_key='you-key', proxy=None, check_video=False)


def insta_account1():
    """Actions for Account 1."""
    try:
        account1 = InstaPy_Init()

        account1.init_account("default")

        InstaPy_Commons(account1)

        account1.login()

        account1.set_dont_include(['user1', 'user2'])
        account1.set_dont_like(["pizza", "#store"])
        account1.like_by_tags(["kiss"], amount=10)

        account1.end()
    except InstaPyError:
        pass


def insta_account2():
    """Actions for Account 2."""
    try:
        account2 = InstaPy_Init()

        account2.init_account("defaultnew")

        InstaPy_Commons(account2)

        account2.login()

        account2.set_dont_include(['user34', 'user45'])
        account2.set_dont_like(["house", "#store"])
        account2.like_by_tags(["panorama"], amount=10)

        account2.end()
    except InstaPyError:
        pass


# Schedule for all accounts
schedule.every(1).to(5).minutes.do(run_threaded, insta_account1)
schedule.every(3).to(7).minutes.do(run_threaded, insta_account2)

while True:
    schedule.run_pending()
    time.sleep(1)
