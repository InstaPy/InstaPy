""" Module that handles the like features """
import random
import re
from re import findall

from .constants import MEDIA_PHOTO, MEDIA_CAROUSEL, MEDIA_ALL_TYPES
from .time_util import sleep
from .util import format_number
from .util import add_user_to_blacklist
from .util import click_element
from .util import is_private_profile
from .util import is_page_available
from .util import update_activity
from .util import web_address_navigator
from .util import get_number_of_posts
from .util import get_action_delay
from .util import explicit_wait
from .util import extract_text_from_element
from .util import evaluate_mandatory_words
from .quota_supervisor import quota_supervisor
from .unfollow_util import get_following_status
from .event import Event

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from .xpath import read_xpath


def get_links_from_feed(browser, amount, num_of_search, logger):
    """Fetches random number of links from feed and returns a list of links"""

    feeds_link = "https://www.instagram.com/"

    # Check URL of the webpage, if it already is in Feeds page, then do not
    # navigate to it again
    web_address_navigator(browser, feeds_link)

    for i in range(num_of_search + 1):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        update_activity(browser, state=None)
        sleep(2)

    # get links
    link_elems = browser.find_elements_by_xpath(
        read_xpath(get_links_from_feed.__name__, "get_links")
    )

    total_links = len(link_elems)
    logger.info("Total of links feched for analysis: {}".format(total_links))
    links = []
    try:
        if link_elems:
            links = [link_elem.get_attribute("href") for link_elem in link_elems]
            logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            for i, link in enumerate(links):
                print(i, link)
            logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    except BaseException as e:
        logger.error("link_elems error {}".format(str(e)))

    return links


def get_main_element(browser, link_elems, skip_top_posts):
    main_elem = None

    if not link_elems:
        main_elem = browser.find_element_by_xpath(
            read_xpath(get_links_for_location.__name__, "top_elements")
        )
    else:
        if skip_top_posts:
            main_elem = browser.find_element_by_xpath(
                read_xpath(get_links_for_location.__name__, "main_elem")
            )
        else:
            main_elem = browser.find_element_by_tag_name("main")

    return main_elem


def get_links_for_location(
    browser, location, amount, logger, media=None, skip_top_posts=True
):
    """
    Fetches the number of links specified by amount and returns a list of links
    """

    if media is None:
        # All known media types
        media = MEDIA_ALL_TYPES
    elif media == MEDIA_PHOTO:
        # Include posts with multiple images in it
        media = [MEDIA_PHOTO, MEDIA_CAROUSEL]
    else:
        # Make it an array to use it in the following part
        media = [media]

    location_link = "https://www.instagram.com/explore/locations/{}".format(location)
    web_address_navigator(browser, location_link)

    top_elements = browser.find_element_by_xpath(
        read_xpath(get_links_for_location.__name__, "top_elements")
    )
    top_posts = top_elements.find_elements_by_tag_name("a")
    sleep(1)

    if skip_top_posts:
        main_elem = browser.find_element_by_xpath(
            read_xpath(get_links_for_location.__name__, "main_elem")
        )
    else:
        main_elem = browser.find_element_by_tag_name("main")

    link_elems = main_elem.find_elements_by_tag_name("a")
    sleep(1)

    if not link_elems:  # this location does not have `Top Posts` or it
        # really is empty..
        main_elem = browser.find_element_by_xpath(
            get_links_for_location.__name__, "top_elements"
        )
        top_posts = []
    sleep(2)

    try:
        possible_posts = browser.execute_script(
            "return window._sharedData.entry_data."
            "LocationsPage[0].graphql.location.edge_location_to_media.count"
        )

    except WebDriverException:
        logger.info(
            "Failed to get the amount of possible posts in '{}' "
            "location".format(location)
        )
        possible_posts = None

    logger.info(
        "desired amount: {}  |  top posts [{}]: {}  |  possible posts: "
        "{}".format(
            amount,
            "enabled" if not skip_top_posts else "disabled",
            len(top_posts),
            possible_posts,
        )
    )

    if possible_posts is not None:
        possible_posts = (
            possible_posts if not skip_top_posts else possible_posts - len(top_posts)
        )
        amount = possible_posts if amount > possible_posts else amount
        # sometimes pages do not have the correct amount of posts as it is
        # written there, it may be cos of some posts is deleted but still
        # keeps counted for the location

    # Get links
    links = get_links(browser, location, logger, media, main_elem)
    filtered_links = len(links)
    try_again = 0
    sc_rolled = 0
    nap = 1.5
    put_sleep = 0
    try:
        while filtered_links in range(1, amount):
            if sc_rolled > 100:
                logger.info("Scrolled too much! ~ sleeping a bit :>")
                sleep(600)
                sc_rolled = 0

            for i in range(3):
                browser.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                update_activity(browser, state=None)
                sc_rolled += 1
                sleep(nap)  # if not slept, and internet speed is low,
                # instagram will only scroll one time, instead of many times
                # you sent scroll command...

            sleep(3)
            links.extend(get_links(browser, location, logger, media, main_elem))

            links_all = links  # uniqify links while preserving order
            s = set()
            links = []
            for i in links_all:
                if i not in s:
                    s.add(i)
                    links.append(i)

            if len(links) == filtered_links:
                try_again += 1
                nap = 3 if try_again == 1 else 5
                logger.info(
                    "Insufficient amount of links ~ trying again: {}".format(try_again)
                )
                sleep(3)

                if try_again > 2:  # you can try again as much as you want
                    # by changing this number
                    if put_sleep < 1 and filtered_links <= 21:
                        logger.info(
                            "Cor! Did you send too many requests? ~ let's " "rest some"
                        )
                        sleep(600)
                        put_sleep += 1

                        browser.execute_script("location.reload()")
                        update_activity(browser, state=None)
                        try_again = 0
                        sleep(10)

                        main_elem = get_main_element(
                            browser, link_elems, skip_top_posts
                        )
                    else:
                        logger.info(
                            "'{}' location POSSIBLY has less images than "
                            "desired:{} found:{}...".format(
                                location, amount, len(links)
                            )
                        )
                        break
            else:
                filtered_links = len(links)
                try_again = 0
                nap = 1.5
    except Exception:
        raise

    sleep(4)

    return links[:amount]


def get_links_for_tag(browser, tag, amount, skip_top_posts, randomize, media, logger):
    """
    Fetches the number of links specified by amount and returns a list of links
    """

    if media is None:
        # All known media types
        media = MEDIA_ALL_TYPES
    elif media == MEDIA_PHOTO:
        # Include posts with multiple images in it
        media = [MEDIA_PHOTO, MEDIA_CAROUSEL]
    else:
        # Make it an array to use it in the following part
        media = [media]

    tag = tag[1:] if tag[:1] == "#" else tag

    tag_link = "https://www.instagram.com/explore/tags/{}".format(tag)
    web_address_navigator(browser, tag_link)

    top_elements = browser.find_element_by_xpath(
        read_xpath(get_links_for_tag.__name__, "top_elements")
    )
    top_posts = top_elements.find_elements_by_tag_name("a")
    sleep(1)

    if skip_top_posts:
        main_elem = browser.find_element_by_xpath(
            read_xpath(get_links_for_tag.__name__, "main_elem")
        )
    else:
        main_elem = browser.find_element_by_tag_name("main")
    link_elems = main_elem.find_elements_by_tag_name("a")
    sleep(1)

    if not link_elems:  # this tag does not have `Top Posts` or it really is
        # empty..
        main_elem = browser.find_element_by_xpath(
            read_xpath(get_links_for_tag.__name__, "top_elements")
        )
        top_posts = []
    sleep(2)

    try:
        possible_posts = browser.execute_script(
            "return window._sharedData.entry_data."
            "TagPage[0].graphql.hashtag.edge_hashtag_to_media.count"
        )

    except WebDriverException:
        try:
            possible_posts = browser.find_element_by_xpath(
                read_xpath(get_links_for_tag.__name__, "possible_post")
            ).text
            if possible_posts:
                possible_posts = format_number(possible_posts)

            else:
                logger.info(
                    "Failed to get the amount of possible posts in '{}' tag  "
                    "~empty string".format(tag)
                )
                possible_posts = None

        except NoSuchElementException:
            logger.info(
                "Failed to get the amount of possible posts in {} tag".format(tag)
            )
            possible_posts = None

    if skip_top_posts:
        amount = amount + 9

    logger.info(
        "desired amount: {}  |  top posts [{}]: {}  |  possible posts: "
        "{}".format(
            amount,
            "enabled" if not skip_top_posts else "disabled",
            len(top_posts),
            possible_posts,
        )
    )

    if possible_posts is not None:
        amount = possible_posts if amount > possible_posts else amount
    # sometimes pages do not have the correct amount of posts as it is
    # written there, it may be cos of some posts is deleted but still keeps
    # counted for the tag

    # Get links
    links = get_links(browser, tag, logger, media, main_elem)
    filtered_links = len(links)
    try_again = 0
    sc_rolled = 0
    nap = 1.5
    put_sleep = 0
    try:
        while filtered_links in range(1, amount):
            if sc_rolled > 100:
                logger.info("Scrolled too much! ~ sleeping a bit :>")
                sleep(600)
                sc_rolled = 0

            for i in range(3):
                browser.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                update_activity(browser, state=None)
                sc_rolled += 1
                sleep(nap)  # if not slept, and internet speed is low,
                # instagram will only scroll one time, instead of many times
                # you sent scoll command...

            sleep(3)
            links.extend(get_links(browser, tag, logger, media, main_elem))

            links_all = links  # uniqify links while preserving order
            s = set()
            links = []
            for i in links_all:
                if i not in s:
                    s.add(i)
                    links.append(i)

            if len(links) == filtered_links:
                try_again += 1
                nap = 3 if try_again == 1 else 5
                logger.info(
                    "Insufficient amount of links ~ trying again: {}".format(try_again)
                )
                sleep(3)

                if try_again > 2:  # you can try again as much as you want
                    # by changing this number
                    if put_sleep < 1 and filtered_links <= 21:
                        logger.info(
                            "Cor! Did you send too many requests? ~ let's " "rest some"
                        )
                        sleep(600)
                        put_sleep += 1

                        browser.execute_script("location.reload()")
                        update_activity(browser, state=None)
                        try_again = 0
                        sleep(10)

                        main_elem = get_main_element(
                            browser, link_elems, skip_top_posts
                        )
                    else:
                        logger.info(
                            "'{}' tag POSSIBLY has less images than "
                            "desired:{} found:{}...".format(tag, amount, len(links))
                        )
                        break
            else:
                filtered_links = len(links)
                try_again = 0
                nap = 1.5
    except Exception:
        raise

    sleep(4)

    if skip_top_posts:
        del links[0:9]

    if randomize is True:
        random.shuffle(links)

    return links[:amount]


def get_links_for_username(
    browser,
    username,
    person,
    amount,
    logger,
    logfolder,
    randomize=False,
    media=None,
    taggedImages=False,
):
    """
    Fetches the number of links specified by amount and returns a list of links
    """

    if media is None:
        # All known media types
        media = MEDIA_ALL_TYPES
    elif media == MEDIA_PHOTO:
        # Include posts with multiple images in it
        media = [MEDIA_PHOTO, MEDIA_CAROUSEL]
    else:
        # Make it an array to use it in the following part
        media = [media]

    logger.info("Getting {} image list...".format(person))

    user_link = "https://www.instagram.com/{}/".format(person)
    if taggedImages:
        user_link = user_link + "tagged/"

    # Check URL of the webpage, if it already is user's profile page,
    # then do not navigate to it again
    web_address_navigator(browser, user_link)

    if not is_page_available(browser, logger):
        logger.error(
            "Instagram error: The link you followed may be broken, or the "
            "page may have been removed..."
        )
        return False

    # if private user, we can get links only if we following
    following_status, _ = get_following_status(
        browser, "profile", username, person, None, logger, logfolder
    )

    # if following_status is None:
    #    browser.wait_for_valid_connection(browser, username, logger)

    # if following_status == 'Follow':
    #    browser.wait_for_valid_authorization(browser, username, logger)

    is_private = is_private_profile(browser, logger, following_status == "Following")
    if (
        is_private is None
        or (is_private is True and following_status not in ["Following", True])
        or (following_status == "Blocked")
    ):
        logger.info("This user is private and we are not following")
        return False

    # Get links
    links = []
    main_elem = browser.find_element_by_tag_name("article")
    posts_count = get_number_of_posts(browser)
    attempt = 0

    if posts_count is not None and amount > posts_count:
        logger.info(
            "You have requested to get {} posts from {}'s profile page BUT"
            " there only {} posts available :D".format(amount, person, posts_count)
        )
        amount = posts_count

    while len(links) < amount:
        initial_links = links
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # update server calls after a scroll request
        update_activity(browser, state=None)
        sleep(0.66)

        # using `extend`  or `+=` results reference stay alive which affects
        # previous assignment (can use `copy()` for it)
        main_elem = browser.find_element_by_tag_name("article")
        links = links + get_links(browser, person, logger, media, main_elem)
        links = sorted(set(links), key=links.index)

        if len(links) == len(initial_links):
            if attempt >= 7:
                logger.info(
                    "There are possibly less posts than {} in {}'s profile "
                    "page!".format(amount, person)
                )
                break
            else:
                attempt += 1
        else:
            attempt = 0

    if randomize is True:
        random.shuffle(links)

    return links[:amount]


def get_media_edge_comment_string(media):
    """AB test (Issue 3712) alters the string for media edge, this resoves it"""
    options = ["edge_media_to_comment", "edge_media_preview_comment"]
    for option in options:
        try:
            media[option]
        except KeyError:
            continue
        return option


def check_link(
    browser,
    post_link,
    dont_like,
    mandatory_words,
    mandatory_language,
    mandatory_character,
    is_mandatory_character,
    check_character_set,
    ignore_if_contains,
    logger,
):
    """
    Check the given link if it is appropriate

    :param browser: The selenium webdriver instance
    :param post_link:
    :param dont_like: hashtags of inappropriate phrases
    :param mandatory_words: words of appropriate phrases
    :param ignore_if_contains:
    :param logger: the logger instance
    :return: tuple of
        boolean: True if inappropriate,
        string: the username,
        boolean: True if it is video media,
        string: the message if inappropriate else 'None',
        string: set the scope of the return value
    """

    # Check URL of the webpage, if it already is post's page, then do not
    # navigate to it again
    web_address_navigator(browser, post_link)

    # Check if the Post is Valid/Exists
    try:
        post_page = browser.execute_script(
            "return window.__additionalData[Object.keys(window.__additionalData)[0]].data"
        )

    except WebDriverException:  # handle the possible `entry_data` error
        try:
            browser.execute_script("location.reload()")
            update_activity(browser, state=None)

            post_page = browser.execute_script(
                "return window._sharedData.entry_data.PostPage[0]"
            )

        except WebDriverException:
            post_page = None

    if post_page is None:
        logger.warning("Unavailable Page: {}".format(post_link.encode("utf-8")))
        return True, None, None, "Unavailable Page", "Failure"

    # Gets the description of the post's link and checks for the dont_like tags
    graphql = "graphql" in post_page
    if graphql:
        media = post_page["graphql"]["shortcode_media"]
        is_video = media["is_video"]
        user_name = media["owner"]["username"]
        image_text = media["edge_media_to_caption"]["edges"]
        image_text = image_text[0]["node"]["text"] if image_text else None
        location = media["location"]
        location_name = location["name"] if location else None
        media_edge_string = get_media_edge_comment_string(media)
        # double {{ allows us to call .format here:
        try:
            browser.execute_script(
                "window.insta_data = window.__additionalData[Object.keys(window.__additionalData)[0]].data"
            )
        except WebDriverException:
            browser.execute_script(
                "window.insta_data = window._sharedData.entry_data.PostPage[0]"
            )
        owner_comments = browser.execute_script(
            """
            latest_comments = window.insta_data.graphql.shortcode_media.{}.edges;
            if (latest_comments === undefined) {{
                latest_comments = Array();
                owner_comments = latest_comments
                    .filter(item => item.node.owner.username == arguments[0])
                    .map(item => item.node.text)
                    .reduce((item, total) => item + '\\n' + total, '');
                return owner_comments;}}
            else {{
                return null;}}
        """.format(
                media_edge_string
            ),
            user_name,
        )

    else:
        media = post_page[0]["shortcode_media"]
        is_video = media["is_video"]
        user_name = media["owner"]["username"]
        image_text = media["caption"]
        owner_comments = browser.execute_script(
            """
            latest_comments = window._sharedData.entry_data.PostPage[
            0].media.comments.nodes;
            if (latest_comments === undefined) {
                latest_comments = Array();
                owner_comments = latest_comments
                    .filter(item => item.user.username == arguments[0])
                    .map(item => item.text)
                    .reduce((item, total) => item + '\\n' + total, '');
                return owner_comments;}
            else {
                return null;}
        """,
            user_name,
        )

    if owner_comments == "":
        owner_comments = None

    # Append owner comments to description as it might contain further tags
    if image_text is None:
        image_text = owner_comments

    elif owner_comments:
        image_text = image_text + "\n" + owner_comments

    # If the image still has no description gets the first comment
    if image_text is None:
        if graphql:
            media_edge_string = get_media_edge_comment_string(media)
            image_text = media[media_edge_string]["edges"]
            image_text = image_text[0]["node"]["text"] if image_text else None

        else:
            image_text = media["comments"]["nodes"]
            image_text = image_text[0]["text"] if image_text else None

    if image_text is None:
        image_text = "No description"

    logger.info("Image from: {}".format(user_name.encode("utf-8")))
    logger.info("Link: {}".format(post_link.encode("utf-8")))
    logger.info("Description: {}".format(image_text.encode("utf-8")))

    # Check if mandatory character set, before adding the location to the text
    if mandatory_language:
        if not check_character_set(image_text):
            return (
                True,
                user_name,
                is_video,
                "Mandatory language not " "fulfilled",
                "Not mandatory " "language",
            )

    # Append location to image_text so we can search through both in one go
    if location_name:
        logger.info("Location: {}".format(location_name.encode("utf-8")))
        image_text = image_text + "\n" + location_name

    if mandatory_words:
        if not evaluate_mandatory_words(image_text, mandatory_words):
            return (
                True,
                user_name,
                is_video,
                "Mandatory words not " "fulfilled",
                "Not mandatory " "likes",
            )

    image_text_lower = [x.lower() for x in image_text]
    ignore_if_contains_lower = [x.lower() for x in ignore_if_contains]
    if any((word in image_text_lower for word in ignore_if_contains_lower)):
        return False, user_name, is_video, "None", "Pass"

    dont_like_regex = []

    for dont_likes in dont_like:
        if dont_likes.startswith("#"):
            dont_like_regex.append(dont_likes + r"([^\d\w]|$)")
        elif dont_likes.startswith("["):
            dont_like_regex.append("#" + dont_likes[1:] + r"[\d\w]+([^\d\w]|$)")
        elif dont_likes.startswith("]"):
            dont_like_regex.append(r"#[\d\w]+" + dont_likes[1:] + r"([^\d\w]|$)")
        else:
            dont_like_regex.append(r"#[\d\w]*" + dont_likes + r"[\d\w]*([^\d\w]|$)")

    for dont_likes_regex in dont_like_regex:
        quash = re.search(dont_likes_regex, image_text, re.IGNORECASE)
        if quash:
            quashed = (
                (((quash.group(0)).split("#")[1]).split(" ")[0])
                .split("\n")[0]
                .encode("utf-8")
            )  # dismiss possible space and newlines
            iffy = (
                (re.split(r"\W+", dont_likes_regex))[3]
                if dont_likes_regex.endswith("*([^\\d\\w]|$)")
                else (re.split(r"\W+", dont_likes_regex))[1]  # 'word' without format
                if dont_likes_regex.endswith("+([^\\d\\w]|$)")
                else (re.split(r"\W+", dont_likes_regex))[3]  # '[word'
                if dont_likes_regex.startswith("#[\\d\\w]+")
                else (re.split(r"\W+", dont_likes_regex))[1]  # ']word'
            )  # '#word'
            inapp_unit = 'Inappropriate! ~ contains "{}"'.format(
                quashed if iffy == quashed else '" in "'.join([str(iffy), str(quashed)])
            )
            return True, user_name, is_video, inapp_unit, "Undesired word"

    return False, user_name, is_video, "None", "Success"


def like_image(browser, username, blacklist, logger, logfolder, total_liked_img):
    """Likes the browser opened image"""
    # check action availability
    if quota_supervisor("likes") == "jump":
        return False, "jumped"

    like_xpath = read_xpath(like_image.__name__, "like")
    unlike_xpath = read_xpath(like_image.__name__, "unlike")

    # find first for like element
    like_elem = browser.find_elements_by_xpath(like_xpath)

    if len(like_elem) == 1:
        # sleep real quick right before clicking the element
        sleep(2)
        like_elem = browser.find_elements_by_xpath(like_xpath)
        if len(like_elem) > 0:
            click_element(browser, like_elem[0])
        # check now we have unlike instead of like
        liked_elem = browser.find_elements_by_xpath(unlike_xpath)

        if len(liked_elem) == 1:
            logger.info("--> Image Liked!")
            Event().liked(username)
            update_activity(
                browser, action="likes", state=None, logfolder=logfolder, logger=logger
            )

            if blacklist["enabled"] is True:
                action = "liked"
                add_user_to_blacklist(
                    username, blacklist["campaign"], action, logger, logfolder
                )

            # get the post-like delay time to sleep
            naply = get_action_delay("like")
            sleep(naply)

            # after every 10 liked image do checking on the block
            if total_liked_img % 10 == 0 and not verify_liked_image(browser, logger):
                return False, "block on likes"

            return True, "success"

        else:
            # if like not seceded wait for 2 min
            logger.info("--> Image was not able to get Liked! maybe blocked ?")
            sleep(120)

    else:
        liked_elem = browser.find_elements_by_xpath(unlike_xpath)
        if len(liked_elem) == 1:
            logger.info("--> Image already liked!")
            return False, "already liked"

    logger.info("--> Invalid Like Element!")

    return False, "invalid element"


def verify_liked_image(browser, logger):
    """Check for a ban on likes using the last liked image"""

    browser.refresh()
    unlike_xpath = read_xpath(like_image.__name__, "unlike")
    like_elem = browser.find_elements_by_xpath(unlike_xpath)

    if len(like_elem) == 1:
        return True
    else:
        logger.info(
            "-------- WARNING! Image was NOT liked! " "You have a BLOCK on likes!"
        )
        return False


def get_tags(browser, url):
    """Gets all the tags of the given description in the url"""

    # Check URL of the webpage, if it already is the one to be navigated,
    # then do not navigate to it again
    web_address_navigator(browser, url)

    try:
        browser.execute_script(
            "window.insta_data = window.__additionalData[Object.keys(window.__additionalData)[0]].data"
        )
    except WebDriverException:
        browser.execute_script(
            "window.insta_data = window._sharedData.entry_data.PostPage[0]"
        )

    graphql = browser.execute_script("return ('graphql' in window.insta_data)")

    if graphql:
        image_text = browser.execute_script(
            "return window.insta_data.graphql."
            "shortcode_media.edge_media_to_caption.edges[0].node.text"
        )

    else:
        image_text = browser.execute_script(
            "return window.insta_data.media.caption.text"
        )

    tags = findall(r"#\w*", image_text)

    return tags


def get_links(browser, page, logger, media, element):
    links = []
    try:
        # Get image links in scope from hashtag, location and other pages
        link_elems = element.find_elements_by_xpath('//a[starts-with(@href, "/p/")]')
        sleep(2)
        if link_elems:
            for link_elem in link_elems:
                try:
                    post_href = link_elem.get_attribute("href")
                    post_elem = element.find_elements_by_xpath(
                        "//a[@href='/p/" + post_href.split("/")[-2] + "/']/child::div"
                    )

                    if len(post_elem) == 1 and MEDIA_PHOTO in media:
                        # Single photo
                        links.append(post_href)

                    if len(post_elem) == 2:
                        # Carousel or Video
                        post_category = element.find_element_by_xpath(
                            "//a[@href='/p/"
                            + post_href.split("/")[-2]
                            + "/']/child::div[@class='u7YqG']/child::span"
                        ).get_attribute("aria-label")

                        if post_category in media:
                            links.append(post_href)
                except WebDriverException:
                    logger.info(
                        "Cannot detect post media type. Skip {}".format(post_href)
                    )
        else:
            logger.info("'{}' page does not contain a picture".format(page))
    except BaseException as e:
        logger.error("link_elems error {}".format(str(e)))
    return links


def verify_liking(browser, maximum, minimum, logger):
    """ Get the amount of existing existing likes and compare it against maximum
    & minimum values defined by user """
    try:
        likes_count = browser.execute_script(
            "return window.__additionalData[Object.keys(window.__additionalData)[0]].data"
            ".graphql.shortcode_media.edge_media_preview_like.count"
        )

    except WebDriverException:
        try:
            browser.execute_script("location.reload()")
            update_activity(browser, state=None)

            likes_count = browser.execute_script(
                "return window._sharedData.entry_data."
                "PostPage[0].graphql.shortcode_media.edge_media_preview_like"
                ".count"
            )

        except WebDriverException:
            try:
                likes_count = browser.find_element_by_css_selector(
                    "section._1w76c._nlmjy > div > a > span"
                ).text

                if likes_count:
                    likes_count = format_number(likes_count)
                else:
                    logger.info("Failed to check likes' count  ~empty string\n")
                    return True

            except NoSuchElementException:
                logger.info("Failed to check likes' count\n")
                return True

    if maximum is not None and likes_count > maximum:
        logger.info(
            "Not liked this post! ~more likes exist off maximum limit at "
            "{}".format(likes_count)
        )
        return False
    elif minimum is not None and likes_count < minimum:
        logger.info(
            "Not liked this post! ~less likes exist off minumum limit "
            "at {}".format(likes_count)
        )
        return False

    return True


def like_comment(browser, original_comment_text, logger):
    """ Like the given comment """
    comments_block_XPath = read_xpath(
        like_comment.__name__, "comments_block"
    )  # quite an efficient
    # location path

    try:
        comments_block = browser.find_elements_by_xpath(comments_block_XPath)
        for comment_line in comments_block:
            comment_elem = comment_line.find_elements_by_tag_name("span")[0]
            comment = extract_text_from_element(comment_elem)

            if comment and (comment == original_comment_text):
                # find "Like" span (a direct child of Like button)
                span_like_elements = comment_line.find_elements_by_xpath(
                    read_xpath(like_comment.__name__, "span_like_elements")
                )
                if not span_like_elements:
                    # this is most likely a liked comment
                    return True, "success"

                # like the given comment
                span_like = span_like_elements[0]
                comment_like_button = span_like.find_element_by_xpath(
                    read_xpath(like_comment.__name__, "comment_like_button")
                )
                click_element(browser, comment_like_button)

                # verify if like succeeded by waiting until the like button
                # element goes stale..
                button_change = explicit_wait(
                    browser, "SO", [comment_like_button], logger, 7, False
                )

                if button_change:
                    logger.info("--> Liked the comment!")
                    sleep(random.uniform(1, 2))
                    return True, "success"

                else:
                    logger.info("--> Unfortunately, comment was not liked.")
                    sleep(random.uniform(0, 1))
                    return False, "failure"

    except (NoSuchElementException, StaleElementReferenceException) as exc:
        logger.error(
            "Error occured while liking a comment.\n\t{}\n\n".format(
                str(exc).encode("utf-8")
            )
        )
        return False, "error"

    return None, "unknown"
