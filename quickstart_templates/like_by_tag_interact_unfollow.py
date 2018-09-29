"""This script is automatically executed every 6h on my server via cron"""

# additional imports random amount of likes and unfollows
import json
import random

from instapy import InstaPy
from instapy.util import smart_run


####
def getUsername():
    with open('../../../../Manutenzione_PC_Portable/InstaPy-master/logs/file.txt', 'r') as input:
        d = json.load(input)
    return d['username']


def getPassword():
    with open('../../../../Manutenzione_PC_Portable/InstaPy-master/logs/file.txt', 'r') as input:
        d = json.load(input)
    return d['psw']


# login credentials
insta_username = getUsername()
insta_password = getPassword()
####

insta_username = ""
insta_password = ""

dont_likes = ['sex', 'nude', 'naked', 'beef', 'pork', 'seafood',
              'egg', 'chicken', 'cheese', 'sausage', 'lobster',
              'fisch', 'schwein', 'lamm', 'rind', 'kuh', 'meeresfrüchte',
              'schaf', 'ziege', 'hummer', 'yoghurt', 'joghurt', 'dairy',
              'meal', 'food', 'eat', 'pancake', 'cake', 'dessert',
              'protein', 'essen', 'mahl', 'breakfast', 'lunch',
              'dinner', 'turkey', 'truthahn', 'plate', 'bacon',
              'sushi', 'burger', 'salmon', 'shrimp', 'steak',
              'schnitzel', 'goat', 'oxtail', 'mayo', 'fur', 'leather',
              'cream', 'hunt', 'gun', 'shoot', 'slaughter', 'pussy',
              'breakfast', 'dinner', 'lunch']

friends = ['list of friends I do not want to interact with']

like_tag_list = ['vegan', 'veganfoodshare', 'veganfood', 'whatveganseat', 'veganfoodie', 'veganism', 'govegan',
                 'veganism', 'vegansofig', 'veganfoodshare', 'veganfit', 'veggies']

# prevent posts that contain some plantbased meat from being skipped
ignore_list = ['vegan', 'veggie', 'plantbased']

accounts = ['accounts with similar content']

"""session = InstaPy(username=insta_username,
                      password=insta_password,
                        headless_browser=True)"""
session = InstaPy(username=insta_username,
                      password=insta_password)

with smart_run(session):
    session.login()

    # settings
    session.set_relationship_bounds(enabled=True,
                                    max_followers=15000, min_posts=5, max_posts=100)

    #session.set_dont_include(friends)
    #session.set_dont_like(dont_likes)
    #session.set_ignore_if_contains(ignore_list)

    #session.set_user_interact(amount=2, randomize=True, percentage=60)
    #session.set_do_follow(enabled=True, percentage=40)
    session.set_do_like(enabled=True, percentage=80)
    session.like_by_users(['frasca2', 'drusianialberto', 'instaosso_', 'natgeo'], amount=1)

    # actions
    #session.like_by_tags(random.sample(like_tag_list, 3), amount=random.randint(50, 100), interact=True)

    #session.unfollow_users(amount=random.randint(75, 150), InstapyFollowed=(True, "all"), style="FIFO",
    #                      unfollow_after=90 * 60 * 60, sleep_delay=501)
