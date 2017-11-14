from instapy import InstaPy
import os
import time
from datetime import datetime
from random import randint
from instapy import time_util, credentials

like100 = ['#outdoors','#explore','#travel','#travelgram','#instatravel','#wanderlust','#viaggiare']
like80 = ['#globetrotter','#backpacker','#wandering','#thegreatoutdoors','#traveling','#travelling','#travelphotography','#traveler','#travelingram']
like60 = ['#zainoinspalla','#esplorare','#explorer','#viaggio','#esploratore','#avventura','#traveller']
like40 = ['#messico','#rivieramaya','#parigi','#coreadelsud','#emiratiarabi','#croazia','#getoutdoors','#liveoutdoors','#greatoutdoors','#scoprire']
like20 = ['#landscape','#ladscapephotography','#landscapes','#wanderer','#stayandwander','#wander','#theglobewanderer','#adventure','#lifeofadventure','#adventures','#adventurer']
like10 = ['#exploretocreate','#exploremore','#exploreeverything','#createexplore','#fitness','#fitnessaddict','#instafitness','#fitnessgirl','#workout','#instapic','#instapicture','#instapict','#instapics','#instagood','#instadaily','#instacool','#adventuretime','#adventureisoutthere']

explore    = ['#explore','#exploretocreate','#exploremore','#exploreeverything','#createexplore','#explorer']    
travel     = ['#travel','#travelgram','#instatravel','#traveling','#travelling','#travelphotography','#traveler','#travelingram','#traveller']    
landscape  = ['#landscape','#ladscapephotography','#landscapes','#wanderlust','#wanderer','#stayandwander','#wander','#theglobewanderer']    
wander     = ['#globetrotter','#backpacker','#wandering','#outdoors','#thegreatoutdoors','#getoutdoors','#liveoutdoors','#greatoutdoors']    
adventure  = ['#adventure','#lifeofadventure','#adventures','#adventuretime','#adventureisoutthere','#adventurer']    
fitness    = ['#fitness','#fitnessaddict','#instafitness','#fitnessgirl','#workout']    
insta      = ['#instapic','#instapicture','#instapict','#instapics','#instagood','#instadaily','#instacool']    
italiani   = ['#viaggiare','#viaggio','#esplorare','#esploratore','#avventura','#zainoinspalla','#scoprire']
mete       = ['#messico','#rivieramaya','#parigi','#coreadelsud','#emiratiarabi','#croazia']       

i_user_followers = ['jannikobenhoff','orcundalarslan','antiguaandbarbuda','saraunderwood','chloe_t','kyrenian','jordhammond','thenomadsoasis','chelseakauai']
i_user_following = ['enrico.onthewine','1mundoxver','darioportamialmare','sometravelago']

user, pwd = credentials.get_credentials()
session = InstaPy(username=user, password=pwd)
session.set_comments(['excellent pic!','bella foto!','bella','nice photo!','bellissima','nice pic!','I really like it','mi piace!','che bella!','ottimo lavoro!','amazing!'], media='Photo')
session.set_unfollow_active_users(enabled=False, posts=5)
session.login()

while(True):
    session.set_do_comment(enabled=True, percentage=20)
    session.set_do_follow(enabled=True, percentage=10)
    
    #session.like_by_tags(like100, amount=50, skip_top_posts=True)
    #session.like_by_tags(like80, amount=40, skip_top_posts=True)
    #session.like_by_tags(like60, amount=30, skip_top_posts=True)
    #session.like_by_tags(like40, amount=25, skip_top_posts=True)
    #session.like_by_tags(like20, amount=20, skip_top_posts=True)
    #session.like_by_tags(like10, amount=10, skip_top_posts=True)
    #session.unfollow_users(amount = 30, onlyInstapyFollowed = False, onlyInstapyMethod = 'FIFO' )
    
    session.like_by_tags(wander, amount=100, skip_top_posts=False)
    
    session.unfollow_users(amount = 50, onlyInstapyFollowed = False, onlyInstapyMethod = 'FIFO' )
    
    session.like_by_tags(landscape, amount=25, skip_top_posts=False)
    session.like_by_tags(adventure, amount=25, skip_top_posts=False)
    session.like_by_tags(mete, amount=30, skip_top_posts=False)
    session.like_by_tags(explore, amount=30, skip_top_posts=False)
    
    session.unfollow_users(amount = 30, onlyInstapyFollowed = False, onlyInstapyMethod = 'FIFO' )
    
    session.set_user_interact(amount=5, random=True, percentage=60)
    session.set_do_follow(enabled=True, percentage=70)
    session.set_do_like(enabled=True, percentage=70)
    session.set_do_comment(enabled=True, percentage=80)
    session.interact_user_followers(i_user_followers[3:6], amount=5, random=True)
    session.interact_user_followers(i_user_followers[6:], amount=5, random=True)
    session.interact_user_followers(i_user_followers[:3], amount=5, random=True)
    
    session.set_user_interact(amount=5, random=True, percentage=60)
    session.set_do_follow(enabled=True, percentage=50)
    session.set_do_like(enabled=True, percentage=70)
    session.set_do_comment(enabled=True, percentage=80)
    session.interact_user_following(i_user_following[:2], amount=5, random=True)
    session.interact_user_following(i_user_following[2:], amount=5, random=True)

    session.like_by_tags(fitness, amount=10, skip_top_posts=False)
    session.like_by_tags(insta, amount=10, skip_top_posts=False)
    session.like_by_tags(italiani, amount=100, skip_top_posts=False)

    session.unfollow_users(amount = 50, onlyInstapyFollowed = False, onlyInstapyMethod = 'FIFO' )
    
    session.like_by_tags(travel, amount=100, skip_top_posts=False)
    
session.end()