"""
Global variables

By design, import no any other local module inside this file.
Vice verse, it'd produce circular dependent imports.
"""

# objects import
from instapy.common import Logger
from instapy.drivers import WebDriver

# libraries import
import os
import json
import random
import requests
from math import radians
from math import degrees as rad2deg
from math import cos


class Settings:
    """ Globally accessible settings throughout whole project """

    # locations
    log_location = None
    database_location = None

    # set current profile credentials for DB operations
    profile = {"id": None, "name": None}

    # hold live Quota Supervisor configuration for global usage
    QS_config = {}

    # store user-defined delay time to sleep after doing actions
    action_delays = {}

    # store configuration of text analytics
    meaningcloud_config = {}
    yandex_config = {}

    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    )

    # state of instantiation of InstaPy
    InstaPy_is_running = False

    # This is where currently the pods server is hosted
    pods_server_endpoint = "https://us-central1-instapy-pods.cloudfunctions.net"
    pods_fashion_server_endpoint = (
        "https://us-central1-instapy-pods-fashion.cloudfunctions.net"
    )
    pods_food_server_endpoint = (
        "https://us-central1-instapy-pods-food.cloudfunctions.net"
    )
    pods_travel_server_endpoint = (
        "https://us-central1-instapy-pods-travel.cloudfunctions.net"
    )
    pods_sports_server_endpoint = (
        "https://us-central1-instapy-pods-sports.cloudfunctions.net"
    )
    pods_entertainment_server_endpoint = (
        "https://us-central1-instapy-pods-entertainment.cloudfunctions.net"
    )

    @classmethod
    def set_action_delays(
        cls,
        enabled: bool = False,
        like: int = None,
        comment: int = None,
        follow: int = None,
        unfollow: int = None,
        story: int = None,
        randomize: bool = False,
        random_range_from: int = None,
        random_range_to: int = None,
        safety_match: bool = True,
    ):
        """ Set custom sleep delay after actions """
        cls.action_delays["enabled"] = enabled
        cls.action_delays["like"] = like
        cls.action_delays["comment"] = comment
        cls.action_delays["follow"] = follow
        cls.action_delays["unfollow"] = unfollow
        cls.action_delays["story"] = story
        cls.action_delays["randomize"] = randomize
        cls.action_delays["random_range_from"] = random_range_from
        cls.action_delays["random_range_to"] = random_range_to
        cls.action_delays["safety_match"] = safety_match

    @classmethod
    def set_do_comment(cls, enabled: bool = False, percentage: int = 0):
        """
        Defines if images should be commented or not.
        E.g. percentage=25 means every ~4th picture will be commented.
        """

        cls.do_comment = enabled
        cls.comment_percentage = percentage

    @classmethod
    def set_comments(cls, comments: list = [], media: str = None):
        """
        Sets the possible posted comments.
        'What an amazing shot :heart_eyes: !' is an example for using emojis.
        """

        if media not in [None, "Photo", "Video"]:
            Logger.warning('Unkown media type! Treating as "any".')
            media = None

        cls.comments = comments

        if media is None:
            cls.comments = comments
        else:
            attr = "{}_comments".format(media.lower())
            setattr(cls, attr, comments)

    @classmethod
    def set_do_follow(cls, enabled: bool = False, percentage: int = 0, times: int = 1):
        """Defines if the user of the liked image should be followed"""

        cls.follow_times = times
        cls.do_follow = enabled
        cls.follow_percentage = percentage

    @classmethod
    def set_do_like(cls, enabled: bool = False, percentage: int = 0):

        cls.do_like = enabled
        cls.like_percentage = min(percentage, 100)

    @classmethod
    def set_do_story(
        cls, enabled: bool = False, percentage: int = 0, simulate: bool = False
    ):
        """
            configure stories
            enabled: to add story to interact
            percentage: how much to watch
            simulate: if True, we will simulate watching (faster),
                      but nothing will be seen on the browser window
        """
        cls.do_story = enabled
        cls.story_percentage = min(percentage, 100)
        cls.story_simulate = simulate

    @classmethod
    def set_dont_like(cls, tags: list = []):
        """Changes the possible restriction tags, if one of this
         words is in the description, the image won't be liked but user
         still might be unfollowed"""

        if not isinstance(tags, list):
            Logger.warning("Unable to use your set_dont_like " "configuration!")
        else:
            cls.dont_like = tags

    @classmethod
    def set_mandatory_words(cls, tags: list = []):
        """Changes the possible restriction tags, if all of this
         hashtags is in the description, the image will be liked"""

        if not isinstance(tags, list):
            Logger.warning("Unable to use your set_mandatory_words " "configuration!")
        else:
            cls.mandatory_words = tags

    @classmethod
    def set_user_interact(
        cls,
        amount: int = 10,
        percentage: int = 100,
        randomize: bool = False,
        media: str = None,
    ):
        """Define if posts of given user should be interacted"""

        cls.user_interact_amount = amount
        cls.user_interact_random = randomize
        cls.user_interact_percentage = percentage
        cls.user_interact_media = media

    @classmethod
    def set_ignore_users(cls, users: list = []):
        """Changes the possible restriction to users, if a user who posts
        is one of these, the image won't be liked"""

        cls.ignore_users = users

    @classmethod
    def set_ignore_if_contains(cls, words: list = []):
        """Ignores the don't likes if the description contains
        one of the given words"""

        cls.ignore_if_contains = words

    @classmethod
    def set_dont_include(cls, friends: list = None):
        """Defines which accounts should not be unfollowed"""

        cls.dont_include = set(friends) or set()
        cls.white_list = set(friends) or set()

    @classmethod
    def set_switch_language(cls, option: bool = True):
        cls.switch_language = option

    @classmethod
    def set_use_clarifai(
        cls,
        enabled: bool = False,
        api_key: str = None,
        models: list = ["general"],
        workflow: list = [],
        probability: float = 0.50,
        full_match: bool = False,
        check_video: bool = False,
        proxy: str = None,
    ):
        """
        Defines if the clarifai img api should be used
        Which 'project' will be used (only 5000 calls per month)

        Raises:
            InstaPyError if os is windows
        """

        # if os.name == 'nt':
        #    raise InstaPyError('Clarifai is not supported on Windows')

        cls.use_clarifai = enabled

        if api_key is None and cls.clarifai_api_key is None:
            cls.clarifai_api_key = os.environ.get("CLARIFAI_API_KEY")
        elif api_key is not None:
            cls.clarifai_api_key = api_key

        cls.clarifai_models = models
        cls.clarifai_workflow = workflow
        cls.clarifai_probability = probability
        cls.clarifai_full_match = full_match
        cls.clarifai_check_video = check_video

        if proxy is not None:
            cls.clarifai_proxy = "https://" + proxy

    @classmethod
    def set_smart_hashtags(
        cls, tags: list = None, limit: int = 3, sort: str = "top", log_tags: bool = True
    ):
        """Generate smart hashtags based on https://displaypurposes.com/"""
        """ranking, banned and spammy tags are filtered out."""

        if tags is None:
            print("set_smart_hashtags is misconfigured")
            return

        for tag in tags:
            req = requests.get(
                "https://d212rkvo8t62el.cloudfront.net/tag/{}".format(tag)
            )
            data = json.loads(req.text)

            if data["tagExists"] is True:
                if sort == "top":
                    # sort by ranking
                    ordered_tags_by_rank = sorted(
                        data["results"], key=lambda d: d["rank"], reverse=True
                    )
                    ranked_tags = ordered_tags_by_rank[:limit]
                    for item in ranked_tags:
                        # add smart hashtag to like list
                        cls.smart_hashtags.append(item["tag"])

                elif sort == "random":
                    if len(data["results"]) < limit:
                        random_tags = random.sample(
                            data["results"], len(data["results"])
                        )
                    else:
                        random_tags = random.sample(data["results"], limit)
                    for item in random_tags:
                        cls.smart_hashtags.append(item["tag"])

                if log_tags is True:
                    for item in cls.smart_hashtags:
                        print("[smart hashtag generated: {}]".format(item))
            else:
                print("Too few results for #{} tag".format(tag))

        # delete duplicated tags
        cls.smart_hashtags = list(set(cls.smart_hashtags))

    @classmethod
    def set_smart_location_hashtags(
        cls, locations: list, radius: int = 10, limit: int = 3, log_tags: bool = True
    ):
        """Generate smart hashtags based on https://displaypurposes.com/map"""
        if locations is None:
            Logger.error("set_smart_location_hashtags is misconfigured")

        for location in locations:
            lat, lon = WebDriver.actions.search(location)

            bbox = cls._get_bounding_box(lat, lon, half_side_in_miles=radius)
            bbox_url = "{},{},{},{}&zoom={}".format(
                bbox["lon_min"],
                bbox["lat_min"],
                bbox["lon_max"],
                bbox["lat_max"],
                radius,
            )
            url = "https://query.displaypurposes.com/local/?bbox={}".format(bbox_url)

            req = requests.get(url)
            data = json.loads(req.text)
            if int(data["count"]) == 0:
                Logger.warning("Too few results for {} location".format(location))
                continue

            count = limit if limit < data["count"] else data["count"]
            i = 0
            tags = []
            while i < count:
                cls.smart_location_hashtags.append(data["tags"][i]["tag"])
                i += 1

        cls.smart_location_hashtags = list(set(cls.smart_location_hashtags))

        if log_tags is True:
            Logger.info(
                "[smart location hashtag generated: {}]\n".format(
                    cls.smart_location_hashtags
                )
            )

    @staticmethod
    def _get_bounding_box(
        latitude_in_degrees, longitude_in_degrees, half_side_in_miles
    ):
        if half_side_in_miles == 0:
            Logger.error("Check your Radius its lower then 0")
            return {}
        if latitude_in_degrees < -90.0 or latitude_in_degrees > 90.0:
            Logger.error("Check your latitude should be between -90/90")
            return {}
        if longitude_in_degrees < -180.0 or longitude_in_degrees > 180.0:
            Logger.error("Check your longtitude should be between -180/180")
            return {}
        half_side_in_km = half_side_in_miles * 1.609344
        lat = radians(latitude_in_degrees)
        lon = radians(longitude_in_degrees)

        radius = 6371
        # Radius of the parallel at given latitude
        parallel_radius = radius * cos(lat)

        lat_min = lat - half_side_in_km / radius
        lat_max = lat + half_side_in_km / radius
        lon_min = lon - half_side_in_km / parallel_radius
        lon_max = lon + half_side_in_km / parallel_radius

        lat_min = rad2deg(lat_min)
        lon_min = rad2deg(lon_min)
        lat_max = rad2deg(lat_max)
        lon_max = rad2deg(lon_max)

        bbox = {
            "lat_min": lat_min,
            "lat_max": lat_max,
            "lon_min": lon_min,
            "lon_max": lon_max,
        }

        return bbox

    @classmethod
    def set_mandatory_language(
        cls, enabled: bool = False, character_set: list = ["LATIN"]
    ):
        """Restrict the description of the image to a character set"""

        char_set = []

        if not isinstance(character_set, list):
            character_set = [character_set]

        for chr_set in character_set:
            if chr_set not in [
                "LATIN",
                "GREEK",
                "CYRILLIC",
                "ARABIC",
                "HEBREW",
                "CJK",
                "HANGUL",
                "HIRAGANA",
                "KATAKANA",
                "THAI",
                "MATHEMATICAL",
            ]:
                Logger.warning('Unkown character set! Treating as "LATIN".')
                ch_set_name = "LATIN"
            else:
                ch_set_name = chr_set

            if ch_set_name not in char_set:
                char_set.append(ch_set_name)

        cls.mandatory_language = enabled
        cls.mandatory_character = char_set


class Storage:
    """ Globally accessible standalone storage """

    # store realtime record activity data
    record_activity = {}
