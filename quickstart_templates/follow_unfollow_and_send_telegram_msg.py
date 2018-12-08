"""
This template is written by @Mehran

What does this quickstart script aim to do?
- My quickstart is just for follow/unfollow users.

NOTES:
- It uses schedulers to trigger activities in chosen hours and also, sends me
  messages through Telegram API.
"""

# -*- coding: UTF-8 -*-
import time
from datetime import datetime
import schedule
import traceback
import requests

from instapy import InstaPy
from instapy.util import smart_run


insta_username = ''
insta_password = ''


def get_session():
    session = InstaPy(username=insta_username,
                      password=insta_password,
                      headless_browser=True,
                      nogui=True,
                      multi_logs=False)

    return session


def follow():
    # Send notification to my Telegram
    requests.get(
        "https://api.telegram.org/******&text='InstaPy Follower Started @ {}'"
        .format(datetime.now().strftime("%H:%M:%S")))

    # get a session!
    session = get_session()

    # let's go!
    with smart_run(session):
        counter = 0

        while counter < 5:
            counter += 1

            try:
                # settings
                session.set_relationship_bounds(enabled=True, potency_ratio=1.21)

                # activity
                session.follow_by_tags(['tehran','تهران'], amount=5)
                session.follow_user_followers(['donya', 'arat.gym'], amount=5, randomize=False)
                session.follow_by_tags(['کادو','سالن','فروشگاه','زنانه','فشن','میکاپ','پوست','زیبا'], amount=10)
                session.follow_by_tags(['لاغری','خرید_آنلاین','کافی_شاپ','گل'], amount=5)
                session.unfollow_users(amount=25, allFollowing=True, style="LIFO", unfollow_after=3*60*60, sleep_delay=450)

            except Exception:
                print(traceback.format_exc())

    # Send notification to my Telegram
    requests.get("https://api.telegram.org/******&text='InstaPy Follower Stopped @ {}'"
                    .format(datetime.now().strftime("%H:%M:%S")))



def unfollow():
    requests.get("https://api.telegram.org/******/sendMessage?chat_id=*****&text='InstaPy Unfollower Started @ {}'"
                    .format(datetime.now().strftime("%H:%M:%S")))

    # get a session!
    session = get_session()

    # let's go!
    with smart_run(session):
        try:
            # settings
            session.set_relationship_bounds(enabled=False, potency_ratio=1.21)

            # actions
            session.unfollow_users(amount=600, allFollowing=True, style="RANDOM", sleep_delay=450)

        except Exception:
            print(traceback.format_exc())

    requests.get("https://api.telegram.org/******/sendMessage?chat_id=*****&text='InstaPy Unfollower Stopped @ {}'"
                    .format(datetime.now().strftime("%H:%M:%S")))



def xunfollow():
    requests.get("https://api.telegram.org/******/sendMessage?chat_id=*****&text='InstaPy Unfollower WEDNESDAY Started @ {}'"
                    .format(datetime.now().strftime("%H:%M:%S")))

    # get a session!
    session = get_session()

    # let's go!
    with smart_run(session):
        try:
            # settings
            session.set_relationship_bounds(enabled=False, potency_ratio=1.21)

            # actions
            session.unfollow_users(amount=1000, allFollowing=True, style="RANDOM", unfollow_after=3*60*60, sleep_delay=450)

        except Exception:
            print(traceback.format_exc())

    requests.get("https://api.telegram.org/******/sendMessage?chat_id=*****&text='InstaPy Unfollower WEDNESDAY Stopped @ {}'"
                    .format(datetime.now().strftime("%H:%M:%S")))


# schedulers
schedule.every().day.at("09:30").do(follow)
schedule.every().day.at("13:30").do(follow)
schedule.every().day.at("17:30").do(follow)

schedule.every().day.at("00:05").do(unfollow)

schedule.every().wednesday.at("03:00").do(xunfollow)


while True:
    schedule.run_pending()
    time.sleep(1)
