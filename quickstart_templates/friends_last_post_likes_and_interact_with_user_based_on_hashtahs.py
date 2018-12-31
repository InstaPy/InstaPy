"""
Based in @jeremycjang and @boldestfortune
This config is ment to run with docker-compose inside a folder call z_{user}
(Added to gitignore)
Folder content:
  - data.yaml
  - docker-compose.yaml
  - start.py (Containing this script)

Content files examples (comments between parenthesis)

::data.yaml::
username: user              # (instagram user)
password: password          # (instagram password)
friends_interaction: True   # (if True will like friendlist posts,
False will avoid create friends session)
do_comments: True           # (if True will comment on user interaction)
do_follow: True             # (if True will follow on user interaction)
user_interact: True         # (if True will interact with user posts)
do_unfollow: True           # (if True will execution unfollow)
friendlist: ['friend1', 'friend2', 'friend3', 'friend4']
hashtags: ['interest1', 'interest2', 'interest3', 'interest4']


::docker-compose.yaml::
version: '3'
services:
  web:
    command: ["./wait-for-selenium.sh", "http://selenium:4444/wd/hub", "--",
    "python", "start.py"]
    environment:
      - PYTHONUNBUFFERED=0
    build:
      context: ../
      dockerfile: docker_conf/python/Dockerfile
    depends_on:
      - selenium
    volumes:
      - ./start.py:/code/start.py
      - ./data.yaml:/code/data.yaml
      - ./logs:/code/logs
  selenium:
    image: selenium/standalone-chrome
    shm_size: 128M

::HOW TO RUN::
Inside z_{user} directory:
  run in background:
    docker-compose down && docker-compose up -d --build
  run with log in terminal:
    docker-compose down && docker-compose up -d --build && docker-compose
    logs -f
"""

import yaml
import os
import random
from instapy import InstaPy
from instapy.util import smart_run

"""
Loading data
"""
current_path = os.path.abspath(os.path.dirname(__file__))
data = yaml.safe_load(open("%s/data.yaml" % (current_path)))

insta_username = data['username']
insta_password = data['password']
friendlist = data['friendlist']
hashtags = data['hashtags']

"""
Generating 5 comments built with random selection and amount of emojis from 
characters
"""
comments = []
characters = [u'😮', u'🌱', u'🍕', u'🚀', u'💬', u'💅', u'🦑', u'🌻', u'⚡️',
              u'🌈', u'🎉', u'😻']
for comment in range(5):
    comment = ''.join(random.sample(characters, random.randint(3, 6)))
    comments.append(comment)

"""
Like last two posts from friendlists
"""
if data['friends_interaction']:
    friends = InstaPy(username=insta_username, password=insta_password,
                      selenium_local_session=False,
                      disable_image_load=True, multi_logs=False)
    friends.set_selenium_remote_session(
        selenium_url='http://selenium:4444/wd/hub')
    with smart_run(friends):
        print(u'💞 Showing friends some love 💖')
        friends.set_relationship_bounds(enabled=False)
        friends.set_skip_users(skip_private=False)
        friends.set_do_like(True, percentage=100)
        friends.interact_by_users(friendlist, amount=2, randomize=False)

"""
Collecting followers
"""
bot = InstaPy(username=insta_username, password=insta_password,
              selenium_local_session=False, disable_image_load=True,
              multi_logs=False)
bot.set_selenium_remote_session(selenium_url='http://selenium:4444/wd/hub')
with smart_run(bot):
    """
    Setting quota supervisor
    """
    bot.set_quota_supervisor(enabled=True, sleep_after=["server_calls_h"],
                             sleepyhead=True, stochastic_flow=True,
                             notify_me=True,
                             peak_likes=(57, 585), peak_follows=(48, None),
                             peak_unfollows=(35, 402),
                             peak_server_calls=(500, None))
    """
    Setting smooth behavior
    """
    bot.set_simulation(enabled=True, percentage=66)
    bot.set_action_delays(enabled=True, like=3, comment=5, follow=4.17,
                          unfollow=28)
    """
    Setting user bounderies
    """
    bot.set_dont_include(friendlist)
    bot.set_blacklist(enabled=True, campaign='blacklist')
    bot.set_relationship_bounds(enabled=True, potency_ratio=-1.21,
                                delimit_by_numbers=True,
                                max_followers=99999999,
                                max_following=5000, min_followers=2000,
                                min_following=10)
    """
    Filters
    """
    bot.set_dont_like(
        ['dick', 'squirt', 'gay', 'homo', '#fit', '#fitfam', '#fittips',
         '#abs', '#kids', '#children', '#child',
         '[nazi', 'promoter'
                  'jew', 'judaism', '[muslim', '[islam', 'bangladesh',
         '[hijab', '[niqab', '[farright', '[rightwing',
         '#conservative', 'death', 'racist'])

    """
    Interaction settings
    """
    bot.set_do_like(enabled=True, percentage=100)
    bot.set_delimit_liking(enabled=True, min=40)
    if data['do_comments']:
        bot.set_comments(comments)
        bot.set_do_comment(enabled=True, percentage=80)
    if data['do_follow']:
        bot.set_do_follow(enabled=True, percentage=60)
    if data['user_interact']:
        bot.set_user_interact(amount=1, randomize=False, percentage=30)

    """
    Interact
    """
    print(u'⛰ ⛏')
    bot.like_by_tags(hashtags, amount=10, interact=True)

    """
    Unfollow non-followers after 3 days and all followed by InstaPy from a 
    week ago.
    """
    if data['do_unfollow']:
        bot.set_blacklist(enabled=False, campaign='blacklist')
        bot.unfollow_users(amount=random.randint(75, 100),
                           InstapyFollowed=(True, "nonfollowers"),
                           style="FIFO",
                           unfollow_after=72 * 60 * 60, sleep_delay=600)
        bot.unfollow_users(amount=1000, InstapyFollowed=(True, "all"),
                           style="FIFO", unfollow_after=168 * 60 * 60,
                           sleep_delay=600)
