""" Module that handles the like features """
# import built-in & third-party modules
import random
import re
from re import findall

# import exceptions
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver.common.by import By

# import InstaPy modules
from .comment_util import open_comment_section
from .constants import (
    MEDIA_ALL_TYPES,
    MEDIA_CAROUSEL,
    MEDIA_IGTV,
    MEDIA_PHOTO,
    MEDIA_VIDEO,
)
from .event import Event
from .follow_util import get_following_status
from .quota_supervisor import quota_supervisor
from .time_util import sleep
from .util import (
    add_user_to_blacklist,
    click_element,
    evaluate_mandatory_words,
    explicit_wait,
    extract_text_from_element,
    format_number,
    get_action_delay,
    get_additional_data,
    get_number_of_posts,
    is_page_available,
    is_private_profile,
    update_activity,
    web_address_navigator,
)
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
    link_elems = browser.find_elements(
        By.XPATH, read_xpath(get_links_from_feed.__name__, "get_links")
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
        logger.error("link_elems error \n\t{}".format(str(e).encode("utf-8")))

    return links


def get_main_element(browser, link_elems, skip_top_posts):
    main_elem = None

    if not link_elems:
        main_elem = browser.find_element(
            By.XPATH, read_xpath(get_links_for_location.__name__, "top_elements")
        )
    else:
        if skip_top_posts:
            main_elem = browser.find_element(
                By.XPATH, read_xpath(get_links_for_location.__name__, "main_elem")
            )
        else:
            main_elem = browser.find_element(By.TAG_NAME, "main")

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

    top_elements = browser.find_element(
        By.XPATH, read_xpath(get_links_for_location.__name__, "top_elements")
    )
    top_posts = top_elements.find_elements(By.TAG_NAME, "a")
    sleep(1)

    if skip_top_posts:
        main_elem = browser.find_element(
            By.XPATH, read_xpath(get_links_for_location.__name__, "main_elem")
        )
    else:
        main_elem = browser.find_element(By.TAG_NAME, "main")

    link_elems = main_elem.find_elements(By.TAG_NAME, "a")
    sleep(1)

    if not link_elems:  # this location does not have `Top Posts` or it
        # really is empty..
        main_elem = browser.find_element(
            By.XPATH, get_links_for_location.__name__, "top_elements"
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
                            "Cor! Did you send too many requests?  ~let's rest some"
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

    top_elements = browser.find_element(
        By.XPATH, read_xpath(get_links_for_tag.__name__, "top_elements")
    )
    top_posts = top_elements.find_elements(By.TAG_NAME, "a")
    sleep(1)

    if skip_top_posts:
        main_elem = browser.find_element(
            By.XPATH, read_xpath(get_links_for_tag.__name__, "main_elem")
        )
    else:
        main_elem = browser.find_element(By.TAG_NAME, "main")
    link_elems = main_elem.find_elements(By.TAG_NAME, "a")
    sleep(1)

    if not link_elems:  # this tag does not have `Top Posts` or it really is
        # empty..
        main_elem = browser.find_element(
            By.XPATH, read_xpath(get_links_for_tag.__name__, "top_elements")
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
            possible_posts = browser.find_element(
                By.XPATH, read_xpath(get_links_for_tag.__name__, "possible_post")
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
                # you sent scroll command...

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
                            "Cor! Did you send too many requests?  ~let's rest some"
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

    # if private user, we can get links only if we following
    following_status, _ = get_following_status(
        browser, "profile", username, person, None, logger, logfolder
    )

    # Check URL of the webpage, if it already is user's profile page,
    # then do not navigate to it again
    web_address_navigator(browser, user_link)

    if not is_page_available(browser, logger):
        logger.error(
            "Instagram error: The link you followed may be broken, or the "
            "page may have been removed..."
        )
        return False

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
        logger.info(
            "This user is private and we are not following. '{}':'{}'".format(
                is_private, following_status
            )
        )
        return False

    # Get links
    links = []
    main_elem = browser.find_element(By.TAG_NAME, "article")
    posts_count = get_number_of_posts(browser)
    attempt = 0

    if posts_count is not None and amount > posts_count:
        logger.info(
            "You have requested to get {} posts from {}'s profile page but"
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
        main_elem = browser.find_element(By.TAG_NAME, "article")
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
    """AB test (Issue 3712) alters the string for media edge, this resolves it"""
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
    post_page = get_additional_data(browser)

    if post_page is None:
        logger.warning("Unavailable Page: {}".format(post_link.encode("utf-8")))
        return True, None, None, "Unavailable Page", "Failure"

    # Gets the description of the post's link and checks for the dont_like tags
    graphql = "graphql" in post_page
    location_name = None

    if graphql:
        media = post_page["graphql"]["shortcode_media"]
        is_video = media["is_video"]
        user_name = media["owner"]["username"]
        image_text = media["edge_media_to_caption"]["edges"]
        image_text = image_text[0]["node"]["text"] if image_text else None
        location = media["location"]
        location_name = location["name"] if location else None
        media_edge_string = get_media_edge_comment_string(media)
        # Gets all comments on media
        comments = (
            media[media_edge_string]["edges"]
            if media[media_edge_string]["edges"]
            else None
        )
        owner_comments = ""
        # Concat all owner comments
        if comments is not None:
            for comment in comments:
                if comment["node"]["owner"]["username"] == user_name:
                    owner_comments = owner_comments + "\n" + comment["node"]["text"]

    else:
        logger.info("post_page: {}".format(post_page))
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
    logger.info("Image link: {}".format(post_link.encode("utf-8")))
    logger.info("Description: {}".format(image_text.encode("utf-8")))

    # Check if mandatory character set, before adding the location to the text
    if mandatory_language:
        if not check_character_set(image_text):
            return (
                True,
                user_name,
                is_video,
                "Mandatory language not fulfilled",
                "Not mandatory language",
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
                "Mandatory words not fulfilled",
                "Not mandatory likes",
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

    media = "Image"  # by default
    like_xpath = read_xpath(like_image.__name__, "like")
    unlike_xpath = read_xpath(like_image.__name__, "unlike")
    play_xpath = read_xpath(like_image.__name__, "play")

    play_elem = browser.find_elements(By.XPATH, play_xpath)
    if len(play_elem) == 1:
        # This is because now IG is not only Images, User can share Images and
        # Videos in one post at the same time, it could be Image -> Video or
        # Video -> Image so we will try to Like the post like one object.
        media = "Video"
        comment = read_xpath(open_comment_section.__name__, "comment_elem")
        element = browser.find_element(By.XPATH, comment)

        # Now, move until 'Comment' section to determine the status of post
        # Notice that some videos comes from TikTok and could have larger size
        # c'est la vie...
        logger.info("--> Found 'Play' button for a video, trying to like it")
        browser.execute_script("arguments[0].scrollIntoView(true);", element)

    # find first for like element
    like_elem = browser.find_elements(By.XPATH, like_xpath)

    if len(like_elem) == 1:
        # sleep real quick right before clicking the element
        sleep(2)
        logger.info("--> {}...".format(media))

        like_elem = browser.find_elements(By.XPATH, like_xpath)
        if len(like_elem) > 0:
            click_element(browser, like_elem[0])
        # check now we have unlike instead of like
        liked_elem = browser.find_elements(By.XPATH, unlike_xpath)

        if len(liked_elem) == 1:
            logger.info("--> {} liked!".format(media))
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

            # after liking an image we do check if liking activity was blocked
            if not verify_liked_image(browser, logger):
                return False, "block on likes"

            return True, "success"

        else:
            # if like not seceded wait for 2 min
            logger.info(
                "--> {} was not able to get liked! maybe blocked?".format(media)
            )
            sleep(120)

    else:
        liked_elem = browser.find_elements(By.XPATH, unlike_xpath)
        if len(liked_elem) == 1:
            logger.info("--> {} already liked!".format(media))
            return False, "already liked"

    logger.info("--> Invalid Like Element!")

    return False, "invalid element"


def verify_liked_image(browser, logger):
    """Check for a ban on likes using the last liked image"""

    browser.refresh()
    unlike_xpath = read_xpath(like_image.__name__, "unlike")
    like_elem = browser.find_elements(By.XPATH, unlike_xpath)

    if len(like_elem) == 1:
        return True
    else:
        logger.warning("--> Image was NOT liked! You have a BLOCK on likes!")
        return False


def get_tags(browser, url):
    """Gets all the tags of the given description in the url"""

    # Check URL of the webpage, if it already is the one to be navigated,
    # then do not navigate to it again
    web_address_navigator(browser, url)

    additional_data = get_additional_data(browser)
    image_text = additional_data["graphql"]["shortcode_media"]["edge_media_to_caption"][
        "edges"
    ][0]["node"]["text"]

    if not image_text:
        image_text = ""

    tags = findall(r"#\w*", image_text)

    return tags


def get_links(browser, page, logger, media, element):
    links = []
    post_href = None

    try:
        # Get image links in scope from hashtag, location and other pages
        link_elems = element.find_elements(By.XPATH, '//a[starts-with(@href, "/p/")]')
        sleep(random.randint(2, 5))

        if link_elems:
            for link_elem in link_elems:
                try:
                    post_href = link_elem.get_attribute("href")
                    post_elem = element.find_elements(
                        By.XPATH,
                        "//a[@href='/p/" + post_href.split("/")[-2] + "/']/child::div",
                    )

                    if len(post_elem) == 1 and MEDIA_PHOTO in media:
                        logger.info("Found media type: {}".format(MEDIA_PHOTO))
                        links.append(post_href)

                    if len(post_elem) == 2:
                        logger.info(
                            "Found media type: {} - {} - {}".format(
                                MEDIA_CAROUSEL, MEDIA_VIDEO, MEDIA_IGTV
                            )
                        )
                        # If you see "Cannot detect post media type. Skip https://www.instagram.com/p/CFvUn0gpaMZ/"
                        # consider updating the @class,'CzVzU', new format types could be added
                        # Media types from constants.py must be updated here, otherwise the links
                        # cannot be categorized.
                        post_category = element.find_element(
                            By.XPATH,
                            "//a[@href='/p/"
                            + post_href.split("/")[-2]
                            + "/']/div[contains(@class,'CzVzU')]/child::*/*[name()='svg']",
                        ).get_attribute("aria-label")

                        logger.info("Post category: {}".format(post_category))

                        if post_category in media:
                            links.append(post_href)

                except WebDriverException:
                    # If "post_href" is None skip the logger to avoid confusion,
                    # the links that are not empty will be catched into the next
                    # loop. Other case, the "post_href" is not empty and needs
                    # to be displayed to the STDOUT for further review.
                    if post_href:
                        logger.info(
                            "Cannot detect post media type. Skip {}".format(post_href)
                        )
        else:
            logger.info("'{}' page does not contain a picture".format(page))

    except BaseException as e:
        logger.error("link_elems error \n\t{}".format(str(e).encode("utf-8")))

    # This block is intended to provide more information to the InstaPy user, they would like to
    # know why the Links cannot be "[Un]Liked", I would like to say that first check if the Media
    # Type is new, second check if the xpath has been updated and finally verify the acct is not
    # under a cold-down stage.
    # If the user can use the link outside InstaPy, they would know IG targeted the acct as
    # automated.
    for i, link in enumerate(links):
        logger.info("Links retrieved:: [{}/{}]".format(i + 1, link))

    return links


def verify_liking(browser, maximum, minimum, logger):
    """Get the amount of existing existing likes and compare it against maximum
    & minimum values defined by user"""

    post_page = get_additional_data(browser)
    likes_count = post_page["graphql"]["shortcode_media"]["edge_media_preview_like"][
        "count"
    ]

    if not likes_count:
        likes_count = 0

    if maximum is not None and likes_count > maximum:
        logger.info(
            "Not liked this post! ~more likes exist off maximum limit at "
            "{}".format(likes_count)
        )
        return False
    elif minimum is not None and likes_count < minimum:
        logger.info(
            "Not liked this post! ~less likes exist off minimum limit "
            "at {}".format(likes_count)
        )
        return False

    return True


def like_comment(browser, original_comment_text, logger):
    """Like the given comment"""
    comments_block_XPath = read_xpath(
        like_comment.__name__, "comments_block"
    )  # quite an efficient
    # location path

    try:
        comments_block = browser.find_elements(By.XPATH, comments_block_XPath)
        for comment_line in comments_block:
            comment_elem = comment_line.find_elements(By.TAG_NAME, "span")[0]
            comment = extract_text_from_element(comment_elem)

            if comment and (comment == original_comment_text):
                # find "Like" span (a direct child of Like button)
                span_like_elements = comment_line.find_elements(
                    By.XPATH, read_xpath(like_comment.__name__, "span_like_elements")
                )
                if not span_like_elements:
                    # this is most likely a liked comment
                    return True, "success"

                # like the given comment
                span_like = span_like_elements[0]
                comment_like_button = span_like.find_element(
                    By.XPATH, read_xpath(like_comment.__name__, "comment_like_button")
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
            "Error occurred while liking a comment.\n\t{}".format(
                str(exc).encode("utf-8")
            )
        )
        return False, "error"

    return None, "unknown"
