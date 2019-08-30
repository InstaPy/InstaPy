#!/usr/bin/env python3
from instapy import InstaPy
from instapy import smart_run
import schedule
import random
import time
import sys
import os

from instapy.like_util import get_links_for_tag
from instapy.like_util import get_links_from_feed
from instapy.models import User, Post, Comment

# login credentials
username = os.environ["INSTAGRAM_USERNAME"]
password = os.environ["INSTAGRAM_PASSWORD"]

# Target users
target_hashtags = ["love", "instagood", "me", "cute", "tbt", "photooftheday", "instamood", "iphonesia", "tweegram", "picoftheday", "igers", "girl", "beautiful", "instadaily", "summer", "instagramhub", "iphoneonly", "follow", "igdaily", "bestoftheday", "happy", "picstitch", "tagblender", "jj", "sky", "nofilter", "fashion", "followme", "fun", "sun"]

# photo comments
photo_comments = [  u':thumbsup: Epic @{}!',
                    u'Keep it up!'
                 ]

session = InstaPy(
    username=username,
    password=password,
    headless_browser=False,
    show_logs=True
)

TAG_COUNT = 2
POST_COUNT = 3
COMMENT_COUNT = 5

POST_LIKE_PERCENTAGE = 50
POST_FOLLOW_PERCENTAGE = 80
POST_COMMENT_PERCENTAGE = 30

INTERACT_COMMENTERS_PERCENTAGE = 30
FOLLOW_COMMENTER_PERCENTAGE = 80

print("[+] starting session new session with:")
print(" - TAG_COUNT: {0}".format(TAG_COUNT))
print(" - POST_COUNT: {0}".format(POST_COUNT))
print(" - COMMENT_COUNT: {0}".format(COMMENT_COUNT))
print(" - POST_LIKE_PERCENTAGE: {0}".format(POST_LIKE_PERCENTAGE))
print(" - POST_FOLLOW_PERCENTAGE: {0}".format(POST_FOLLOW_PERCENTAGE))
print(" - POST_COMMENT_PERCENTAGE: {0}".format(POST_COMMENT_PERCENTAGE))
print(" - INTERACT_COMMENTERS_PERCENTAGE: {0}".format(INTERACT_COMMENTERS_PERCENTAGE))
print(" - FOLLOW_COMMENTER_PERCENTAGE: {0}".format(FOLLOW_COMMENTER_PERCENTAGE))

print("[+] This will result in approximate:")
print(" - {0} LIKES".format(TAG_COUNT * POST_COUNT * POST_LIKE_PERCENTAGE / 100))
print(" - {0} POST FOLLOWS".format(TAG_COUNT * POST_COUNT * POST_FOLLOW_PERCENTAGE / 100))
print(" - {0} COMMENTS".format(TAG_COUNT * POST_COUNT * POST_COMMENT_PERCENTAGE / 100))
print(" - {0} COMMENT FOLLOWS".format(TAG_COUNT * POST_COUNT * INTERACT_COMMENTERS_PERCENTAGE / 100 * COMMENT_COUNT * FOLLOW_COMMENTER_PERCENTAGE / 100))

with smart_run(session):
    random.shuffle(target_hashtags)

    for tag in target_hashtags[:TAG_COUNT]:
        print("[+] investigating tag: {0}".format(tag))

        links = get_links_for_tag(
                        session.browser,
                        tag,
                        POST_COUNT,
                        True,
                        False,
                        None,
                        session.logger,
                    )

        posts = set()
        for link in links:
            post = Post(link=link)
            posts.add(post)
            print(" - post: {0}".format(post))

            # like post
            if random.randint(0, 100) <= POST_LIKE_PERCENTAGE:
                print(" - liking post: {0}".format(post))
                post.like(session)

            # Follow poster
            if random.randint(0, 100) <= POST_FOLLOW_PERCENTAGE:
                print(" - following post user")
                # post.follow(session)
                user = post.get_user(session)
                user.follow(session)

            # Comment on post
            if random.randint(0, 100) <= POST_COMMENT_PERCENTAGE:
                random.shuffle(photo_comments)
                print(" - commenting post: {0}".format(photo_comments[0]))
                post.comment(session, comment=photo_comments[0])

            # Interact with commenters
            if random.randint(0, 100) <= INTERACT_COMMENTERS_PERCENTAGE:
                print(" - interacting with maximal {0} commenters".format(COMMENT_COUNT))

                comments = post.get_comments(session, offset=0, limit=COMMENT_COUNT)
                for comment in comments:
                    commenter = comment.get_user(session)
                    print("   - comment by: {0}".format(comment.user))

                    # Follow commenter
                    if random.randint(0, 100) <= FOLLOW_COMMENTER_PERCENTAGE:
                        print("     - following commenter: {0}".format(commenter.name))
                        commenter.follow(session)

    print("[+] all done")

