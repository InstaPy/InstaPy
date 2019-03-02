# importing instapy
# https://github.com/timgrossmann/InstaPy
# ------------------------------------->
from instapy import InstaPy
from instapy import smart_run
from instapy import set_workspace

# import other stuff
import random
import json

# set workspace folder at desired location (default is at your home folder)
# set_workspace(path=None)

# implement to avoid UnicodeEncodeError for e.g chinese hashtags
# -------------->
# https://github.com/timgrossmann/InstaPy/issues/3321
# https://github.com/timgrossmann/InstaPy/issues/838
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# importing all settings from settings.json
# ----------------------->
with open('settings.json') as settings_file:
    settings = json.load(settings_file)

# get an InstaPy session!
# set headless_browser=True to run InstaPy in the background
# ------------------------------------->
session = InstaPy(username=str(settings['credentials']['username']), password=str(settings['credentials']['password']), headless_browser=False)

# Fire up Session!
# ------------------->
with smart_run(session):

    # Set Up Relationship Bounds
    # ------------------------------------->
    # This is used to check the number of followers and/or following a user has and if these numbers
    # either exceed the number set OR does not pass the number set OR if their ratio does not reach
    # desired potency ratio then no further interaction happens
    # ------------------------------------->
    session.set_relationship_bounds(
        enabled=True,
        # potency_ratio=1,
        delimit_by_numbers=True,
        max_followers=8500,
        max_following=4000,
        min_followers=100,
        min_following=100,
        min_posts=10,
        max_posts=1000
    )
    # Mandatory Language
    # https://github.com/timgrossmann/InstaPy#mandatory-language
    # ------------------------------------>
    # set_mandatory_language restrict the interactions, liking and following if
    # any character of the description is outside of the character set selected
    # (the location is not included and non-alphabetic characters are ignored).
    # For example if you choose LATIN, any character in Cyrillic will flag the post as inappropriate.
    # ------------------------------------>
    # Available character sets: LATIN, GREEK, CYRILLIC, ARABIC, HEBREW, CJK, HANGUL, HIRAGANA, KATAKANA and THAI
    session.set_mandatory_language(enabled=True, character_set='LATIN')

    # will prevent commenting on and unfollowing your good friends
    # the images will still be liked
    # ------------------->
    friends = [
        # 'usernamme',
        # 'username',
    ]

    session.set_dont_include(friends)

    # https://github.com/timgrossmann/InstaPy#interact-by-comments
    # session.set_do_reply_to_comments(enabled=True, percentage=20)

    # Do the liking
    # ------------------->
    session.set_do_like(True, percentage=100)

    # https://github.com/timgrossmann/InstaPy#following
    session.set_do_follow(enabled=True, percentage=50)

    # Commenting + CLARIFAI
    # ---------------------------->
    # default enabled=False, ~ every 4th image will be commented on
    # https://github.com/timgrossmann/InstaPy#commenting
    comments = [] # ensure to not add default comments
    session.set_comments(comments)

    # default enabled=False, ~ every 10th image will be commented on
    # Todo: Try to only let Clarify comment! Images
    session.set_do_comment(True, percentage=100) # <-- Must be activated for clarifai to work!!

    # Use Clarifai AI to analyse Pictures and make Comments
    # ------------------------------------->
    # Enabling Imagechecking
    # default enabled=False , enables the checking with the clarifai api (image
    # tagging) if secret and proj_id are not set, it will get the environment
    session.set_use_clarifai(enabled=True, api_key=settings['clarifai']['api_key'], probability=0.97, models=['general'], full_match=True)

    # uses the clarifai api to check if the image contains nsfw content
    # -> won't comment if image is nsfw
    # ------------------------------------->
    session.clarifai_check_img_for(['nsfw', 'child'])

    # checks the image for keywords food and lunch, if both are found,
    # comments with the given comments. If full_match is False (default), it only requires a single tag to match Clarifai results.

    # Import smart comments general function
    # Import all wanted comments schemes
    # ------------------->
    from custom_functions.smart_comments import *
    from custom_functions.comments_animals import *
    from custom_functions.comments_art import *
    from custom_functions.comments_motor_sports import *
    from custom_functions.comments_nature import *
    from custom_functions.comments_surfing import *

    # Keep in mind ->
    # Adjust Comments sequence depending on smart hashtags
    smarthashtags = [
        'animals',
        'beach',
        'illustration',
        'ride',
        'beach',
        'surfing',
        'motors',
        'outdoor',
        'mountain',
        'nature',
        'trip',
        'camping',
    ]

    comments_general = [
        comments_surfing(),
        comments_animals(),
        comments_art(),
        comments_motor_sports(),
        comments_nature(),
    ]

    # ------------------------------------------>
    # This is where the commenting magic happens
    # ------------------------------------------>
    for comments in comments_general:
        # random.shuffle(comments)
        # print(comments);

        for comment in comments:

            # check if keys are defined in comment object
            if not comment.get('synonyms'):
                comment['synonyms'] = ['photo', 'picture']

            if not comment.get('synonyms_before'):
                comment['synonyms_before'] = ['']

            if not comment.get('synonyms_after'):
                comment['synonyms_after'] = ['']

            if not comment.get('emojis'):
                comment['emojis'] = ['']

            # Fire the Clarifai Image Check Based on the defnied comments in
            # Custom Comments
            # ----------------------------------->
            session.clarifai_check_img_for(
                comment['concept'],
                comment=True,
                comments=smart_comments(
                    synonyms=comment['synonyms'],
                    synonyms_before=comment['synonyms_before'],
                    synonyms_after=comment['synonyms_after'],
                    emojis=comment['emojis'],
                )
            )

    # Smart Hashtags + Interact with User + Liking by Tags
    # ------------------------------------->
    # Generate smart hashtags based on https://displaypurposes.com ranking,
    # banned and spammy tags are filtered out.
    # (limit) defines amount limit of generated hashtags by hashtag
    # (sort) sort generated hashtag list 'top' and 'random' are available
    # (log_tags) shows generated hashtags before use it
    # (use_smart_hashtags) activates like_by_tag to use smart hashtags
    # ------------------------------------->
    session.set_smart_hashtags(smarthashtags, limit=5, sort='top', log_tags=True)

    #  Not User Interact for now -> Bad Image Results
    session.set_user_interact(amount=1, randomize=True, percentage=70, media='Photo')
    #
    #  https://github.com/timgrossmann/InstaPy#like-by-tags
    session.like_by_tags(amount=10, use_smart_hashtags=True, media='Photo', interact=True)

    # Interact with users that someone else is following
    # ---------------------------------->
    # user_following = [
    #     'test',
    #     'test',
    #     'test'
    # ]

    # session.interact_user_following(user_following, amount=100, randomize=True)

    # Interact with someone else's followers
    # ---------------------------------->
    # user_followers = [
    #     'test',
    #     'test',
    #     'test'
    # ]

    # Interact with the people that a given user is followed by
    # set_do_comment, set_do_follow and set_do_like are applicable
    # session.interact_user_followers(user_followers, amount=100, randomize=True)

    # Set Normal Hashtags again
    # Be Sure you can also use smart hashtags
    # import random
    # random.shuffle(hashtags)
    #
    # hashtags = [
    #     'hbkbraunschweig',
    #     'openstudios',
    #     'kuenstler',
    #     'study',
    #     'painting',
    #     'fotoshoot',
    #     'contemporaryart',
    #     'photography',
    #     'kunstwerk',
    #     'artlovers',
    #     'exhibition',
    #     'dailyart',
    #     'obststudios',
    # ]

    # Use normal Tags for liking
    # session.like_by_tags(hashtags, amount=10, media='Photo', interact=True)

    # https://github.com/timgrossmann/InstaPy#unfollowing
    # session.unfollow_users(amount=60, InstapyFollowed=(True, "nonfollowers"), style="FIFO", unfollow_after=90*60*60, sleep_delay=500)

    # Like by Locations
    # ------------------------------------->
    # You can find locations for the like_by_locations function by:
    # Browsing https://www.instagram.com/explore/locations/
    # Regular instagram search.
    # Search 'Salton Sea' and select the result with a location icon
    # The url is for example: https://www.instagram.com/explore/locations/224442573/salton-sea/
    # Use everything after 'locations/' or just the number
    # ------------------------------------->
    locations = [
        '272608620/masunte-oaxaca-mexico/',
        '213131048/berlin-germany/',
        '213270076/mexico-city-mexico/'
    ]

    session.like_by_locations(locations, amount=5, media='Photo')

    # This is used to perform likes on your own feeds
    # ------------------------------------->
    # amount=100  specifies how many total likes you want to perform
    # randomize=True randomly skips posts to be liked on your feed
    # unfollow=True unfollows the author of a post which was considered
    # inappropriate interact=True visits the author's profile page of a
    # certain post and likes a given number of his pictures, then returns to feed
    # ------------------------------------->
    session.like_by_feed(amount=200, randomize=True, unfollow=False, interact=True)

    # UNFOLLOW
    # ---------------------------------------->
    # Don't unfollow active users
    # Prevents unfollow followers who have liked one of your latest 5 posts
    session.set_dont_unfollow_active_users(enabled=True, posts=5)

    # https://github.com/timgrossmann/InstaPy#unfollowing
    # if you like to unfollow only the users followed by InstaPy WHO do not follow you back, use the track- "nonfollowers";
    # session.unfollow_users(amount=300, InstapyFollowed=(True, "nonfollowers"), style="FIFO", unfollow_after=unfollow_after, sleep_delay=400)

    # Unfollow the users WHO do not follow you back:
    unfollow_after = 2*24*60*60 # two Days
    session.unfollow_users(amount=400, nonFollowers=True, style="RANDOM", unfollow_after=unfollow_after, sleep_delay=400)

    # Quota Supervisor
    # Take full control of the actions with the most sophisticated approaches
    # enabled: put True to activate or False to deactivate supervising any time
    # peak_likes: the first value indicates the hourly and the second indicates the daily peak value
    # TODO: Not working! Try to get that!
    # ------------------------------------->
    # session.set_quota_supervisor(
    #     enabled=True,
    #     sleep_after=["likes", "comments_d", "follows", "unfollows", "server_calls_h"],
    #     sleepyhead=True,
    #     stochastic_flow=True,
    #     notify_me=True,
    #     peak_likes=(57, 585),
    #     peak_comments=(21, 182),
    #     peak_follows=(48, None),
    #     peak_unfollows=(35, 402),
    #     peak_server_calls=(None, 4700)
    # )
