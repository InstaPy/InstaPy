from InstaPy.instapy import Settings
from InstaPy.instapy import InstaPy

from plugins.statistics import write_result
from plugins.mail_support import mail_result

from datetime import datetime

import logging
import json

import argparse

import requests

global followed_this_time
global liked_this_time
global already_liked_this_time
global commented_this_time
global like_inap_this_time
global follow_inap_this_time
global followed_by
global unfollowed
followed_this_time = 0
liked_this_time = 0
already_liked_this_time = 0
commented_this_time = 0
like_inap_this_time = 0
follow_inap_this_time = 0
followed_by = 0
unfollowed = 0

# PARSE USERNAME FROM ARGUMENT #
parser = argparse.ArgumentParser()
parser.add_argument('username', action="store")
parser.add_argument('type', nargs='?')
parse_results = parser.parse_args()

insta_username = parse_results.username
type = parse_results.type

if type != None:
    print('---> Type argument given: ' + str(type))
else:
    print('---> No type argument given')

# LOAD USER-SPECIFIC SETTINGS #
import importlib
libname = 'run_' + insta_username
module = importlib.__import__(libname)

print('MODULE LOADED: ' + str(module))

# SET UP TIME AND LOGGING #
now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
timestart = datetime.now().replace(microsecond=0)
logging.basicConfig(filename='statistics/logs/' + now + '-' + insta_username +  '_instabot.log',level=logging.INFO)

# SET UP INSTAPY #
Settings.database_location = './db/instapy.db'
Settings.chromedriver_location = './browser/chromedriver'
session = InstaPy(username=module.insta_username,
                  password=module.insta_password,
                  headless_browser=True,
                  multi_logs=True
                  )

try:
    session.switch_language=False
    session.login()

    ### LOAD SETTINGS ###
    session.set_comments(comments=module.set_comments['comments'])
    session.set_do_comment(enabled=module.set_do_comment['enabled'], percentage=module.set_do_comment['percentage'])
    session.set_do_follow(enabled=module.set_do_follow['enabled'], percentage=module.set_do_follow['percentage'], times=module.set_do_follow['times'])
    session.set_user_interact(amount=module.set_user_interact['amount'],
                              percentage=module.set_user_interact['percentage'], randomize=module.set_user_interact['randomize'],
                              media=module.set_user_interact['media'])
    session.set_dont_unfollow_active_users(enabled=module.set_dont_unfollow_active_users['enabled'], posts=module.set_dont_unfollow_active_users['posts'])
    session.set_relationship_bounds(enabled=module.set_relationship_bounds['enabled'], potency_ratio=module.set_relationship_bounds['potency_ratio'],
                                    delimit_by_numbers=module.set_relationship_bounds['delimit_by_numbers'],
                                    min_followers=module.set_relationship_bounds['min_followers'],
                                    max_followers=module.set_relationship_bounds['max_followers'],
                                    min_following=module.set_relationship_bounds['min_following'],
                                    max_following=module.set_relationship_bounds['max_following'])
    session.set_delimit_liking(enabled=module.set_delimit_liking['enabled'], min=module.set_delimit_liking['min'], max=module.set_delimit_liking['max'])
    session.set_delimit_commenting(enabled=module.set_delimit_commenting['enabled'], min=module.set_delimit_commenting['min'],
                                   max=module.set_delimit_commenting['max'])
    session.set_dont_like(module.set_dont_like['dontlikelist'])
    session.set_ignore_users(module.set_ignore_users['ignoreuserslist'])
    session.set_ignore_if_contains(module.set_ignore_if_contains['ignoreifcontainslist'])

    if module.set_dont_include['source'] == 'file':
        print('---> Dont include by file')
        friends = json.load(open(module.set_dont_include['dontincludefilename']))
        session.set_dont_include(friends)
        print('---> These friends are not included: ' + str(friends[0:5]) + ' and ' + str(len(friends)-6) + ' more.')
    else:
        print('---> Dont include by list')
        session.set_dont_include(module.set_dont_include['dontincludelist'])
        #print('---> These friends are not included: ' + str(module.set_dont_include['dontincludelist']))
    session.set_simulation(enabled=module.set_simulation['enabled'], percentage=module.set_simulation['percentage'])

    ### LOAD ACTIONS ###
    if module.follow_by_list['enabled'] == True and type != 'only_unfollow':
        print('---> Starting following by list')
        session.follow_by_list(module.follow_by_list['followlist'], times=module.follow_by_list['times'], sleep_delay=module.follow_by_list['sleep_delay'],
                               interact=module.follow_by_list['interact'])
    else:
        print('---> Following by list not enabled')

    if module.follow_user_followers['enabled'] == True and type != 'only_unfollow':
        print('---> Starting following by someone elses followers')
        session.follow_user_followers(module.follow_user_followers['followlist'], amount=module.follow_user_followers['amount'],
                                      randomize=module.follow_user_followers['randomize'], sleep_delay=module.follow_user_followers['sleep_delay'],
                                      interact=module.follow_user_followers['interact'])
    else:
        print('---> Following by user following not enabled')

    if module.follow_user_following['enabled'] == True and type != 'only_unfollow':
        print('---> Starting following by someone elses following')
        session.follow_user_following(module.follow_user_following['followlist'], amount=module.follow_user_following['amount'],
                                      randomize=module.follow_user_following['randomize'], sleep_delay=module.follow_user_following['sleep_delay'],
                                      interact=module.follow_user_following['interact'])
    else:
        print('---> Following by user following not enabled')

    if module.follow_by_tags['enabled'] == True and type != 'only_unfollow':
        print('---> Starting following by tags')
        session.follow_by_tags(tags=module.follow_by_tags['tags'], amount=module.follow_by_tags['amount'],
                                      randomize=module.follow_by_tags['randomize'], skip_top_posts=module.follow_by_tags['skip_top_posts'],
                                      media=module.follow_by_tags['media'])
    else:
        print('---> Following by tags not enabled')

    if module.follow_likers['enabled'] == True and type != 'only_unfollow':
        print('---> Starting following by likers')
        session.follow_likers(module.follow_likers['followlist'], photos_grab_amount=module.follow_likers['photos_grab_amount'],
                              follow_likers_per_photo=module.follow_likers['follow_likers_per_photo'], randomize=module.follow_likers['randomize'],
                              sleep_delay=module.follow_likers['sleep_delay'], interact=module.follow_likers['interact'])
    else:
        print('---> Following by likers not enabled')

    if module.follow_commenters['enabled'] == True and type != 'only_unfollow':
        print('---> Starting following by commenters')
        session.follow_commenters(module.follow_commenters['followlist'], amount=module.follow_commenters['amount'],
                                  daysold=module.follow_commenters['daysold'], max_pic=module.follow_commenters['max_pic'],
                                  sleep_delay=module.follow_commenters['sleep_delay'], interact=module.follow_commenters['interact'])
    else:
        print('---> Following by commenters not enabled')


    #####

    if module.interact_by_users['enabled'] == True and type != 'only_unfollow':
        print('---> Starting interacting by users')
        session.interact_by_users(module.interact_by_users['interactlist'], amount=module.interact_by_users['amount'],
                                  randomize=module.interact_by_users['randomize'], media=module.interact_by_users['media'])
    else:
        print('---> Interacting by users not enabled')

    if module.interact_user_following['enabled'] == True and type != 'only_unfollow':
        print('---> Starting interacting by elses following')
        session.interact_user_following(module.interact_user_following['interactlist'], amount=module.interact_user_following['amount'],
                                  randomize=module.interact_user_following['randomize'])
    else:
        print('---> Interacting by elses following not enabled')

    if module.interact_user_followers['enabled'] == True and type != 'only_unfollow':
        print('---> Starting interacting by elses following')
        session.interact_user_followers(module.interact_user_followers['interactlist'], amount=module.interact_user_followers['amount'],
                                  randomize=module.interact_user_followers['randomize'])
    else:
        print('---> Interacting by elses following not enabled')

    if module.interact_by_URL['enabled'] == True and type != 'only_unfollow':
        print('---> Starting interacting by URL')
        session.interact_by_URL(urls=module.interact_by_URL['urls'], randomize=module.interact_by_URL['randomize'],
                                interact=module.interact_by_URL['interact'])
    else:
        print('---> Interacting by URL not enabled')


    #####

    if module.comment_by_locations['enabled'] == True and type != 'only_unfollow':
        print('---> Starting commenting by locations')
        session.comment_by_locations(locations=module.comment_by_locations['locations'], amount=module.comment_by_locations['amount'],
                                skip_top_posts=module.comment_by_locations['skip_top_posts'], media=module.comment_by_locations['media'])
    else:
        print('---> Commenting by locations not enabled')

    if module.like_by_tags['enabled'] == True and type != 'only_unfollow':
        print('---> Starting liking by tags')
        session.like_by_tags(tags=module.like_by_tags['tags'], amount=module.like_by_tags['amount'], randomize=module.like_by_tags['randomize'],
                             interact=module.like_by_tags['interact'])
    else:
        print('---> Liking by tags not enabled')

    if module.like_by_feed['enabled'] == True and type != 'only_unfollow':
        print('---> Starting liking by feed')
        session.like_by_feed(amount=module.like_by_feed['amount'], unfollow=module.like_by_feed['unfollow'], sleep_delay=module.like_by_feed['sleep_delay'],
                             interact=module.like_by_feed['interact'])
    else:
        print('---> Liking by feed not enabled')

    if module.like_by_locations['enabled'] == True and type != 'only_unfollow':
        print('---> Starting Liking by locations')
        session.like_by_locations(locations=module.like_by_locations['locations'], amount=module.like_by_locations['amount'],
                                skip_top_posts=module.like_by_locations['skip_top_posts'], media=module.like_by_locations['media'])
    else:
        print('---> Liking by locations not enabled')

    ####
    if module.unfollow_users['enabled'] == True and (type == 'unfollow' or type == 'only_unfollow') and module.unfollow_users['method'] == 'instapyfollowed':
        print('---> Starting unfollowing with method: instapyfollowed')
        session.unfollow_users(amount=module.unfollow_users['amount'], sleep_delay=module.unfollow_users['sleep_delay'], style=module.unfollow_users['style'],
                               unfollow_after=module.unfollow_users['unfollow_after'], InstapyFollowed=(True, module.unfollow_users['InstaPyFollowed']))
    else:
        print('---> Unfollowing with method: instapyfollowed not enabled')

    if module.unfollow_users['enabled'] == True and (type == 'unfollow' or type == 'only_unfollow') and module.unfollow_users['method'] == 'all':
        print('---> Starting unfollowing with method: all')
        session.unfollow_users(amount=module.unfollow_users['amount'], sleep_delay=module.unfollow_users['sleep_delay'], style=module.unfollow_users['style'],
                               unfollow_after=module.unfollow_users['unfollow_after'], allFollowing=True)
    else:
        print('---> Unfollowing with method: all not enabled')

finally:

    followed_this_time += session.followed
    print('---> Followed this time: ' + str(followed_this_time))
    print('---> Session followed: ' + str(session.followed))

    liked_this_time += session.liked_img
    print('---> Liked this time: ' + str(liked_this_time))
    print('---> Session liked: ' + str(session.liked_img))

    already_liked_this_time += session.already_liked
    print('---> Already liked this time: ' + str(already_liked_this_time))
    print('---> Session already liked: ' + str(session.already_liked))

    commented_this_time += session.commented
    print('---> Commented this time: ' + str(commented_this_time))
    print('---> Session commented: ' + str(session.commented))

    like_inap_this_time += session.inap_img
    print('---> Like inap this time: ' + str(like_inap_this_time))
    print('---> Session liked inap: ' + str(session.inap_img))

    follow_inap_this_time += session.inap_img
    print('---> Follow inap this time: ' + str(follow_inap_this_time))
    print('---> Session follow inap: ' + str(session.inap_img))

    followed_by = session.followed_by
    print('---> Followed by: ' + str(followed_by))


    # write_result(insta_username=insta_username,
    #              timestart=timestart,
    #              liked_this_time=session.liked_img,
    #              already_liked_this_time=session.already_liked,
    #              like_inap_this_time=session.inap_img,
    #              commented_this_time=session.commented,
    #              followed_this_time=session.followed,
    #              follow_inap_this_time=session.inap_img,
    #              followed_by=session.followed_by)
    #
    # requests.post("https://api.pushover.net/1/messages.json",
    #               data={'token': '<token>',
    #                     'device': module.devices,
    #                     'user': '<user>',
    #                     'title': 'Instagram bot @' + insta_username + ' finished',
    #                     'message': str(session.liked_img) + ' were liked and ' + str(session.followed) + ' followed. I posted ' + str(session.commented) + ' comments. I unfollowed ' + str(session.unfollowed) + ' users. You have ' + str(followed_by) + ' followers!'},
    #               verify=False)

    session.end()
