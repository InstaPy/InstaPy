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
with open('./logs/following/'+insta_username, 'rb') as input:
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
        #taglist = ['10monthsold', '8monthsold', 'babygram', 'kidstagram', 'babybump', '6months', 'proudmommy', 'toddlerfashion','girlmom','bows','momofgirls', 'babygirl', 'mommylife', 'momanddaughter', 'baby', 'mybabygirl', 'babygirl']
        taglist = ['10monthsold', '8monthsold', 'babygram', 'kidstagram', 'babybump', '6months', 'childhoodunplugged', 'candidchildhood', 'cameramama']
        shuffle(taglist)
        taglist = taglist[:5]
        print(taglist)

        #create instance
        session = InstaPy(username=insta_username, password=insta_password, proxy_address='149.202.180.55', proxy_port=3128)
        session.login()

        # limits
        session.set_dont_like(['boy', 'boys', 'store', 'shop in bio', 'shipping', 'worldwide', 'shop'])
        #limits
        session.set_blacklist(enabled=True, campaign='General')
        session.set_upper_follower_count(limit=25500)
        session.set_dont_include(original_all_following)
        session.set_dont_include_language(['fa', 'ar', 'id', 'tr', 'ab', 'af', 'as', 'az', 'ba', 'zh', 'cv', 'th', 'sq'])
        session.set_user_interact(amount=2, randomize=False, percentage=100, media='Photo', listUsersFromDirectory=True)
        #configurations
        session.set_do_like(True, percentage=95)
        session.set_do_comment(True, percentage=20)
        session.set_do_follow(True, percentage=30, times=1)

        session.set_feed_comments(['beautiful', u':heart_eyes:', u':heart_eyes::heart_eyes:',
                                    u':heart_eyes::heart_eyes::heart_eyes:',
                                    u':heart_eyes: + :heart_eyes:', u':heart_eyes: :heart_eyes:',
                                    u':leaves: + :leaves:', u':leaves: :leaves:',u':purple_heart:',
                                    u':pray:', u':heart: :heart:', u'heart :heart:',
                                    u':sunny:', u':cloud::sunny::cloud:',u':sunny: :cloud:',u':sunny::sunny:',
                                    u':tulip:', u':tulip:::sunflower:::tulip:', u':tulip: :tulip:',
                                    u':sunflower::sunflower:'])

        session.set_comments({"en":[
            'beautiful', u':heart_eyes:', u':heart_eyes::heart_eyes:',
            u':heart_eyes::heart_eyes::heart_eyes:',
            u':heart_eyes: + :heart_eyes:', u':heart_eyes: :heart_eyes:',
            u':leaves: + :leaves:', u':leaves: :leaves:', u':purple_heart:',
            u':pray:', u':heart: :heart:', u'heart :heart:',
            u':sunny:', u':cloud::sunny::cloud:', u':sunny: :cloud:', u':sunny::sunny:',
            u':tulip:', u':tulip:::sunflower:::tulip:', u':tulip: :tulip:',
            u':sunflower::sunflower:',
            'Delightful photography...', 'describe ur works!',
            'Nice-nice.', 'Way rad!', 'hi {} Pretty cool!',
            'hi {} Its fascinating...',
            'hi {} Nice photo', 'Just love it', 'Lovely pictures',
            'It has sence and character... I love it...',
            'Winning, love it!', 'Magnetic power!', 'Paradise', 'Fantastic',
            'looks good', 'Elegant and stylish!', 'Amazing Love Life',
            'Great pictures! Just love it!', 'Hello {} I really enjoy your account..',
            'Harmony and peaceful atmoshere...', 'BINGO!!! Beauty&Style in one piece!', 'Wow, thats amazing pic',
            'Amazing', 'Wonderful', 'Awesome...)', 'Awesome...():)', 'Love ur profile', 'Love your profile :)', 'Just love it',
            'Fresh and bright!', 'Like all your photoes', 'Extremely good one!'
        ],
        "he":['beautiful', u':heart_eyes:', u':heart_eyes::heart_eyes:',
              u':heart_eyes::heart_eyes::heart_eyes:',
              u':heart_eyes: + :heart_eyes:', u':heart_eyes: :heart_eyes:',
              u':leaves: + :leaves:', u':leaves: :leaves:',u':purple_heart:',
              u':pray:', u':heart: :heart:', u'heart :heart:',
              u':sunny:', u':cloud::sunny::cloud:',u':sunny: :cloud:',u':sunny::sunny:',
              u':tulip:', u':tulip:::sunflower:::tulip:', u':tulip: :tulip:',
              u':sunflower::sunflower:',
              'מקסים',
              'יפה',
              'יפה:)',
              'יפה!',
              'אחלה',
              'אחלה!',
              'אחלה :)',
              'מקסים!!',
              'מקסים!!!',
              'מקסים=!',
              'מרגש!',
              'מרגש@!!',
              'מרגש!!',
              'זה נחמד ככה :)',
              'זה נחמד, ככה :) !',
              'מעניין@',
              'מעניין!!',
              'ליבי'
              ]})
		
        session.set_sleep_reduce(70)
        session.set_following_limit(True, limit=715, unfollowImmediate=True)

        # start the process
        print("do the actual liking by tag")
        session.like_by_tags(taglist, amount=100)

        # unfollow
        #session.unfollow_users(amount=20, onlyInstapyFollowed=True, onlyInstapyMethod='FIFO', sleep_delay=250)

        print("do the actual liking by feed")
        session.like_by_feed(amount=80)

        # unfollow
        session.unfollow_users(amount=30, onlyInstapyFollowed=True, onlyInstapyMethod='FIFO', sleep_delay=250)


    except KeyboardInterrupt:
        session.end()
        quit()
    finally:
        import traceback
        print(traceback.format_exc())
        try:
            session.end()
        except:
            pass


schedule.every(10).to(20).minutes.do(job)
# run immed
try:
    job()
except:
    pass

while True:
    schedule.run_pending()
    #print("--- wait for next job ---")
    time.sleep(55)