from instapy import InstaPy
from random import shuffle
from instapy.unfollow_util import dump_follow_restriction
import pickle
import sys

with open('./logs/user.txt', 'r') as file:
    insta_username = file.readline()
    print(insta_username)
with open('./logs/password.txt', 'r') as file:
    insta_password = file.readline()
with open('./logs/all_following.pkl', 'rb') as input:
    original_all_following = pickle.load(input)
print ("original_all_following users to ignore", len(original_all_following))
print("1")

import schedule
import time

def job():
    try:
        #create instance
        session = InstaPy(username=insta_username, password=insta_password, passwordinput = sys.argv[0])
        session.login()
        #limits
        session.set_dont_include(original_all_following)
        # start the process
        #session.set_dont_unfollow_active_users(enabled=True, posts=2)
        session.unfollow_users(amount=100, onlyInstapyFollowed=True, onlyInstapyMethod='FIFO', sleep_delay=240 )
        # end the bot session
        session.end()
    except KeyboardInterrupt:
        session.end()
    except:
        import traceback
        print(traceback.format_exc())

schedule.every().day.at("06:22").do(job)
schedule.every().day.at("07:20").do(job)
schedule.every().day.at("08:05").do(job)
schedule.every().day.at("10:23").do(job)
schedule.every().day.at("12:08").do(job)
schedule.every().day.at("13:02").do(job)
schedule.every().day.at("14:13").do(job)
schedule.every().day.at("15:13").do(job)
schedule.every().day.at("16:14").do(job)
schedule.every().day.at("17:23").do(job)
schedule.every().day.at("18:13").do(job)
schedule.every().day.at("19:00").do(job)
schedule.every().day.at("20:25").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)