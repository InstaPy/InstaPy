from instapy import InstaPy
from instapy.telegram_util import start_telegram,finish_telegram,pause_telegram
import time


from instapy import InstaPy

insta_username = ''
insta_password = ''

# set headless_browser=True if you want to run InstaPy on a server
try:
    session = InstaPy(username=insta_username,
                      password=insta_password,
                      headless_browser=False)
    session.login()
    #Sends a Telegram message to your Channel ID telling you the bot has started
	start_telegram(insta_username)
    # settings
    session.set_upper_follower_count(limit=2500)
    session.set_do_comment(True, percentage=10)
    session.set_comments(['aMEIzing!', 'So much fun!!', 'Nicey!'])
    session.set_dont_include(['friend1', 'friend2', 'friend3'])
    session.set_dont_like(['pizza', 'girl'])

    # actions
    session.like_by_tags(['f4f'], amount=1)
    #Bot sleeps for 1 hour
    time.sleep(3600)
    #Sends a Telegram message to your Channel ID telling you the bot is going to sleep for 1 hour
    pause_telegram(insta_username)
    session.like_by_tags(['followforfollow'], amount=1)

finally:
    #Sends a Telegram message to your Channel ID telling you the bot has finished
    finish_telegram(insta_username)
    # end the bot session
    session.end()
