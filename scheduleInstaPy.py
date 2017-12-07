from instapy import InstaPy
from random import shuffle
from instapy.statistics import InstaPyStorage
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
        # check time restrictions
        is_not_hour_to_run = InstaPyStorage()
        if is_not_hour_to_run.check_limit() is True:
            print("Not an Hour to run")
            return 0
        taglist = ['babygram', 'kidstagram', 'babybump', 'babyroom', '6months', 'proudmommy', 'toddlerfashion','girlmom','bows','momofgirls', 'babygirl', 'mommylife', 'momanddaughter', 'baby', 'mybabygirl', 'babygirl']
        userFollowlist = ["petekdesign", "soul.soulandpaper", "dror_sade", "orly555", "sivan_ih", "loveandlibby", "matan_sensel", "einadesign", "tweelingendesign", "nkahalon", "yaelyaniv", "pulkepanama" ,"lihihod", "galisjewerly", "shooka.stores", "ms_sweet_dreams", "danielyona", "ronitshler", "peterandwolf.kids", "anattal03", "michaelbercu", "limortiroche", "danaungerfashion", "hilarahav", "kerenshpilsher", "petitedorisofficial", "jem_sharonbenzaray", "kerenbargil", "sivansternbach", "maria_rodsant", "misskyreeloves", "zucoulisses", "petit.os", "foxsheartbeat", "nyani_kids", "littleops_", "kidsinteriors_com", "mytrendtroom", "natalydadon", "adikastyle"]
        shuffle(taglist)
        shuffle(userFollowlist)
        userFollowlist = userFollowlist[:5]
        taglist = taglist[:5]
        print(taglist)
        print(userFollowlist)
        #create instance
        session = InstaPy(username=insta_username, password=insta_password)
        session.login()
        # use smart hashtags
        #session.set_smart_hashtags(taglist, limit=3, sort='top', log_tags=True)
        session.set_dont_like(['boy', 'boys', 'store', 'shop in bio', 'shipping', 'worldwide', 'shop'])
        #limits
        session.set_blacklist(enabled=True, campaign='General')
        session.set_upper_follower_count(limit=1500)
        session.set_dont_include(original_all_following)
        session.set_user_interact(amount=2, randomize=False, percentage=90, media='Photo')
        #configurations
        session.set_do_comment(True, percentage=5)
        session.set_do_follow(True, percentage=50, times=1)
        session.set_comments(['beautiful', u'\u2665', u'\u2665 \u2665 \u2665', u'\u2665 \u2665', u'\u2764', u'\u263A'])

        # start the process
        print("do the actual liking by tag")
        session.like_by_tags(taglist, amount=200)

        # unfollow
        session.unfollow_users(amount=40, onlyInstapyFollowed=True, onlyInstapyMethod='FIFO', sleep_delay=600)

        print("do the actual liking by feed")
        session.like_by_feed(amount=80)

		# unfollow
        session.unfollow_users(amount=40, onlyInstapyFollowed=True, onlyInstapyMethod='FIFO', sleep_delay=600)
		
        print("do the actual liking by user list")
        session.interact_user_followers(userFollowlist, amount=700, randomize=False)

        # unfollow
        session.unfollow_users(amount=40, onlyInstapyFollowed=True, onlyInstapyMethod='FIFO', sleep_delay=600)

        # end the bot session
        session.end()
    except KeyboardInterrupt:
        session.end()
    except:
        import traceback
        print(traceback.format_exc())

job()
schedule.every().day.at("06:22").do(job)
schedule.every().day.at("08:01").do(job)
schedule.every().day.at("09:10").do(job)
schedule.every().day.at("10:23").do(job)
schedule.every().day.at("11:18").do(job)
schedule.every().day.at("12:25").do(job)
schedule.every().day.at("14:25").do(job)
schedule.every().day.at("15:28").do(job)
schedule.every().day.at("16:25").do(job)
schedule.every().day.at("17:25").do(job)
schedule.every().day.at("19:00").do(job)
schedule.every().day.at("20:44").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)