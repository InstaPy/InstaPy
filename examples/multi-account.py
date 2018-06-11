import random 
from instapy import InstaPy
import os
import multiprocessing
import datetime
import time

instaUser = ['username1', 'username2']
instaPass = ['pass1', 'pass2']
followersToFollow = [['acc1RelatedtoUser1', 'acc2RelatedtoUser1'], ['acc1RelatedtoUser2']]
smartTags = [['tag1User1', 'tag2User1'], ['tag1User2']]
followLocation = ['', '224442573/salton-sea/']

def worker(selection):
    
    print("MULTI - Started as",instaUser[selection],"at",datetime.datetime.now().strftime("%H:%M:%S"))
    session = InstaPy(username=instaUser[selection], password=instaPass[selection], headless_browser=True)
    session.login()

    session.set_dont_unfollow_active_users(enabled=True, posts=7)
    session.set_user_interact(amount=2, randomize=True, percentage=20, media='Photo')
    session.set_relationship_bounds(enabled=True,
             potency_ratio=-1.21,
              delimit_by_numbers=True,
               max_followers=4590,
                max_following=5555,
                 min_followers=45,
                  min_following=77)

    session.like_by_feed(amount=random.randint(5,11), randomize=True, unfollow=True, interact=True)
    print("MULTI -",instaUser[selection],"finished liking by feed at",datetime.datetime.now().strftime("%H:%M:%S"))

    if not followLocation[selection] == '':#if no location given for that account, just ignore this step
        session.like_by_locations(followLocation[selection], amount=10)
        print("MULTI -",instaUser[selection],"finished liking by location",datetime.datetime.now().strftime("%H:%M:%S"))

    session.unfollow_users(amount=random.randint(7,10), sleep_delay=(random.randint(44,111)))
    print("MULTI -",instaUser[selection],"finished unfollowing at",datetime.datetime.now().strftime("%H:%M:%S"))

    if followersToFollow[selection]:
        session.follow_user_followers(followersToFollow[selection], amount=random.randint(44,55), randomize=False, interact=True, sleep_delay=111)
        print("MULTI -",instaUser[selection],"finished following followers at",datetime.datetime.now().strftime("%H:%M:%S"))

    if smartTags[selection]:
        session.set_smart_hashtags(smartTags[selection], limit=3, sort='top', log_tags=True)
        session.like_by_tags(amount=random.randint(2,5), use_smart_hashtags=True)
        print("MULTI -",instaUser[selection],"finished smartTags at",datetime.datetime.now().strftime("%H:%M:%S"))

    session.end()
    print("MULTI -",instaUser[selection],"finished run at",datetime.datetime.now().strftime("%H:%M:%S"))

if __name__ == '__main__':        
    print("MULTI -","Starting at",datetime.datetime.now().strftime("%H:%M:%S"))
    jobs = []
    for i in range(len(instaUser)):
        p = multiprocessing.Process(target=worker, args=(i,))
        jobs.append(p)
        p.start()
        time.sleep(66);#no delay cause some instances of chrome to give errors and stop