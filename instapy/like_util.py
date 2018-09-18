""" Module that handles the like features """
import random
import re
from re import findall
from selenium.webdriver.common.keys import Keys

from .time_util import sleep
from .util import format_number
from .util import add_user_to_blacklist
from .util import click_element
from .util import is_private_profile
from .util import update_activity
from .util import web_address_navigator
from .util import get_number_of_posts
from .quota_supervisor import quota_supervisor

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException




def get_links_from_feed(browser, amount, num_of_search, logger):
    """Fetches random number of links from feed and returns a list of links"""

    feeds_link = 'https://www.instagram.com/'

    #Check URL of the webpage, if it already is in Feeds page, then do not navigate to it again
    web_address_navigator(browser, feeds_link)

    for i in range(num_of_search + 1):
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)

    # get links
    link_elems = browser.find_elements_by_xpath(
        "//article/div[2]/div[2]/a")

    total_links = len(link_elems)
    logger.info("Total of links feched for analysis: {}".format(total_links))
    links = []
    try:
        if link_elems:
            links = [link_elem.get_attribute('href') for link_elem in link_elems]
            logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            for i, link in enumerate(links):
                print(i, link)
            logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    except BaseException as e:
        logger.error("link_elems error {}".format(str(e)))

    return links



def get_links_for_location(browser,
                           location,
                           amount,
                           logger,
                           media=None,
                           skip_top_posts=True):

    """Fetches the number of links specified
    by amount and returns a list of links"""
    if media is None:
        # All known media types
        media = ['', 'Post', 'Video']
    elif media == 'Photo':
        # Include posts with multiple images in it
        media = ['', 'Post']
    else:
        # Make it an array to use it in the following part
        media = [media]

    location_link = "https://www.instagram.com/explore/locations/{}".format(location)
    web_address_navigator(browser, location_link)

    top_elements = browser.find_element_by_xpath('//main/article/div[1]')
    top_posts = top_elements.find_elements_by_tag_name('a')
    sleep(1)

    if skip_top_posts:
        main_elem = browser.find_element_by_xpath('//main/article/div[2]')
    else:
        main_elem = browser.find_element_by_tag_name('main')

    link_elems = main_elem.find_elements_by_tag_name('a')
    sleep(1)

    if not link_elems:  # this location does not have `Top Posts` or it really is empty..
        main_elem = browser.find_element_by_xpath('//main/article/div[1]')
        top_posts = []
    sleep(2)

    try:
        possible_posts = browser.execute_script(
            "return window._sharedData.entry_data."
            "LocationsPage[0].graphql.location.edge_location_to_media.count")
    except WebDriverException:
        logger.info("Failed to get the amount of possible posts in '{}' location".format(location))
        possible_posts = None

    logger.info("desired amount: {}  |  top posts [{}]: {}  |  possible posts: {}".format(amount,
                                      ('enabled' if not skip_top_posts else 'disabled'), len(top_posts), possible_posts))

    if possible_posts is not None:
        possible_posts = possible_posts if not skip_top_posts else possible_posts-len(top_posts)
        amount = possible_posts if amount > possible_posts else amount
        #sometimes pages do not have the correct amount of posts as it is written there, it may be cos of some posts is deleted but still keeps counted for the location

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
                    "window.scrollTo(0, document.body.scrollHeight);")
                sc_rolled += 1
                update_activity()
                sleep(
                    nap)  # if not slept, and internet speed is low, instagram will only scroll one time, instead of many times you sent scroll command...
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
                logger.info("Insufficient amount of links ~ trying again: {}".format(try_again))
                sleep(3)
                if try_again > 2:  # you can try again as much as you want by changing this number
                    if put_sleep < 1 and filtered_links <= 21:
                        logger.info("Cor! Did you send too many requests? ~ let's rest some")
                        sleep(600)
                        put_sleep += 1
                        browser.execute_script("location.reload()")
                        try_again = 0
                        sleep(10)
                        main_elem = (browser.find_element_by_xpath('//main/article/div[1]') if not link_elems else
                                     browser.find_element_by_xpath('//main/article/div[2]') if skip_top_posts else
                                     browser.find_element_by_tag_name('main'))
                    else:
                        logger.info("'{}' location POSSIBLY has less images than desired...".format(location))
                        break
            else:
                filtered_links = len(links)
                try_again = 0
                nap = 1.5
    except:
        raise

    sleep(4)

    return links[:amount]



def get_links_for_tag(browser,
                      tag,
                      amount,
                      skip_top_posts,
                      randomize,
                      media,
                      logger):
    """Fetches the number of links specified
    by amount and returns a list of links"""

    if media is None:
        # All known media types
        media = ['', 'Post', 'Video']
    elif media == 'Photo':
        # Include posts with multiple images in it
        media = ['', 'Post']
    else:
        # Make it an array to use it in the following part
        media = [media]

    tag = (tag[1:] if tag[:1] == '#' else tag)

    tag_link = "https://www.instagram.com/explore/tags/{}".format(tag)
    web_address_navigator(browser, tag_link)

    top_elements = browser.find_element_by_xpath('//main/article/div[1]')
    top_posts = top_elements.find_elements_by_tag_name('a')
    sleep(1)

    if skip_top_posts:
        main_elem = browser.find_element_by_xpath('//main/article/div[2]')
    else:
        main_elem = browser.find_element_by_tag_name('main')
    link_elems = main_elem.find_elements_by_tag_name('a')
    sleep(1)

    if not link_elems:   #this tag does not have `Top Posts` or it really is empty..
        main_elem = browser.find_element_by_xpath('//main/article/div[1]')
        top_posts = []
    sleep(2)

    try:
        possible_posts = browser.execute_script(
            "return window._sharedData.entry_data."
            "TagPage[0].graphql.hashtag.edge_hashtag_to_media.count")
    except WebDriverException:
        try:
            possible_posts = (browser.find_element_by_xpath(
                                "//span[contains(@class, 'g47SY')]").text)
            if possible_posts:
                possible_posts = format_number(possible_posts)
            else:
                logger.info("Failed to get the amount of possible posts in '{}' tag  ~empty string".format(tag))
                possible_posts = None
        except NoSuchElementException:
            logger.info("Failed to get the amount of possible posts in {} tag".format(tag))
            possible_posts = None

    logger.info("desired amount: {}  |  top posts [{}]: {}  |  possible posts: {}".format(amount,
                                      ('enabled' if not skip_top_posts else 'disabled'), len(top_posts), possible_posts))

    if possible_posts is not None:
        possible_posts = possible_posts if not skip_top_posts else possible_posts-len(top_posts)
        amount = possible_posts if amount > possible_posts else amount
    #sometimes pages do not have the correct amount of posts as it is written there, it may be cos of some posts is deleted but still keeps counted for the tag

    #Get links
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
                    "window.scrollTo(0, document.body.scrollHeight);")
                sc_rolled += 1
                update_activity()
                sleep(nap)   #if not slept, and internet speed is low, instagram will only scroll one time, instead of many times you sent scoll command...
            sleep(3)
            links.extend(get_links(browser, tag, logger, media, main_elem))

            links_all = links   #uniqify links while preserving order
            s = set()
            links = []
            for i in links_all:
                if i not in s:
                    s.add(i)
                    links.append(i)
            if len(links) == filtered_links:
                try_again += 1
                nap = 3 if try_again==1 else 5
                logger.info("Insufficient amount of links ~ trying again: {}".format(try_again))
                sleep(3)
                if try_again > 2:   #you can try again as much as you want by changing this number
                    if put_sleep < 1 and filtered_links <= 21 :
                        logger.info("Cor! Did you send too many requests? ~ let's rest some")
                        sleep(600)
                        put_sleep += 1
                        browser.execute_script("location.reload()")
                        try_again = 0
                        sleep(10)
                        main_elem = (browser.find_element_by_xpath('//main/article/div[1]') if not link_elems else
                                      browser.find_element_by_xpath('//main/article/div[2]') if skip_top_posts else
                                       browser.find_element_by_tag_name('main'))
                    else:
                        logger.info("'{}' tag POSSIBLY has less images than desired...".format(tag))
                        break
            else:
                filtered_links = len(links)
                try_again = 0
                nap = 1.5
    except:
        raise

    sleep(4)

    if randomize == True:
        random.shuffle(links)

    return links[:amount]


def get_links_for_username(browser,
                           username,
                           amount,
                           logger,
                           randomize=False,
                           media=None):

    """Fetches the number of links specified
    by amount and returns a list of links"""
    if media is None:
        # All known media types
        media = ['', 'Post', 'Video']
    elif media == 'Photo':
        # Include posts with multiple images in it
        media = ['', 'Post']
    else:
        # Make it an array to use it in the following part
        media = [media]

    logger.info('Getting {} image list...'.format(username))

    user_link = "https://www.instagram.com/{}/".format(username)

    #Check URL of the webpage, if it already is user's profile page, then do not navigate to it again
    web_address_navigator(browser, user_link)

    body_elem = browser.find_element_by_tag_name('body')
    abort = True

    try:
        is_private = is_private_profile(browser, logger)
    except:
        logger.info('Interaction begin...')
    else:
        if is_private:
            logger.warning('This user is private...')
            return False

    if "Page Not Found" in browser.title:
        logger.error('Intagram error: The link you followed may be broken, or the page may have been removed...')
        return False

    #Get links
    links = []
    main_elem = browser.find_element_by_tag_name('article')
    posts_count = get_number_of_posts(browser)
    attempt = 0

    if posts_count is not None and amount > posts_count:
        logger.info("You have requested to get {} posts from {}'s profile page BUT"
                    " there only {} posts available :D".format(amount, username, posts_count))
        amount = posts_count

    while len(links) < amount:
        initial_links = links
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        # update server calls after a scroll request
        update_activity()
        sleep(0.66)

        # using `extend`  or `+=` results reference stay alive which affects previous assignment (can use `copy()` for it)
        links = links + get_links(browser, username, logger, media, main_elem)
        links = sorted(set(links), key=links.index)

        if len(links) == len(initial_links):
            if attempt >= 7:
                logger.info("There are possibly less posts than {} in {}'s profile page!".format(amount, username))
                break
            else:
                attempt += 1
        else:
            attempt = 0

    if randomize == True:
        random.shuffle(links)

    return links[:amount]



def check_link(browser, post_link, dont_like, mandatory_words, ignore_if_contains, logger):
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

    #Check URL of the webpage, if it already is post's page, then do not navigate to it again
    web_address_navigator(browser, post_link)

    """Check if the Post is Valid/Exists"""
    try:
        post_page = browser.execute_script(
            "return window._sharedData.entry_data.PostPage")
    except WebDriverException:   #handle the possible `entry_data` error
        try:
            browser.execute_script("location.reload()")
            post_page = browser.execute_script(
            "return window._sharedData.entry_data.PostPage")
        except WebDriverException:
            post_page = None

    if post_page is None:
        logger.warning('Unavailable Page: {}'.format(post_link.encode('utf-8')))
        return True, None, None, 'Unavailable Page', "Failure"

    """Gets the description of the post's link and checks for the dont_like tags"""
    graphql = 'graphql' in post_page[0]
    if graphql:
        media = post_page[0]['graphql']['shortcode_media']
        is_video = media['is_video']
        user_name = media['owner']['username']
        image_text = media['edge_media_to_caption']['edges']
        image_text = image_text[0]['node']['text'] if image_text else None
        owner_comments = browser.execute_script('''
      latest_comments = window._sharedData.entry_data.PostPage[0].graphql.shortcode_media.edge_media_to_comment.edges;
      if (latest_comments === undefined) latest_comments = Array();
      owner_comments = latest_comments
        .filter(item => item.node.owner.username == '{}')
        .map(item => item.node.text)
        .reduce((item, total) => item + '\\n' + total, '');
      return owner_comments;
    '''.format(user_name))
    else:
        media = post_page[0]['media']
        is_video = media['is_video']
        user_name = media['owner']['username']
        image_text = media['caption']
        owner_comments = browser.execute_script('''
      latest_comments = window._sharedData.entry_data.PostPage[0].media.comments.nodes;
      if (latest_comments === undefined) latest_comments = Array();
      owner_comments = latest_comments
        .filter(item => item.user.username == '{}')
        .map(item => item.text)
        .reduce((item, total) => item + '\\n' + total, '');
      return owner_comments;
    '''.format(user_name))

    if owner_comments == '':
        owner_comments = None

    """Append owner comments to description as it might contain further tags"""
    if image_text is None:
        image_text = owner_comments
    elif owner_comments:
        image_text = image_text + '\n' + owner_comments

    """If the image still has no description gets the first comment"""
    if image_text is None:
        if graphql:
            image_text = media['edge_media_to_comment']['edges']
            image_text = image_text[0]['node']['text'] if image_text else None
        else:
            image_text = media['comments']['nodes']
            image_text = image_text[0]['text'] if image_text else None
    if image_text is None:
        image_text = "No description"

    logger.info('Image from: {}'.format(user_name.encode('utf-8')))
    logger.info('Link: {}'.format(post_link.encode('utf-8')))
    logger.info('Description: {}'.format(image_text.encode('utf-8')))

    if mandatory_words :
        if not all((word in image_text for word in mandatory_words)) :
            return True, user_name, is_video, 'Mandatory words not fulfilled', "Not mandatory likes"

    image_text_lower = map(lambda x: x.lower(), image_text)
    ignore_if_contains_lower = map(lambda x: x.lower(), ignore_if_contains)
    if any((word in image_text_lower for word in ignore_if_contains_lower)):
        return False, user_name, is_video, 'None', "Pass"

    dont_like_regex = []

    for dont_likes in dont_like:
        if dont_likes.startswith("#"):
            dont_like_regex.append(dont_likes + "([^\d\w]|$)")
        elif dont_likes.startswith("["):
            dont_like_regex.append("#" + dont_likes[1:] + "[\d\w]+([^\d\w]|$)")
        elif dont_likes.startswith("]"):
            dont_like_regex.append("#[\d\w]+" + dont_likes[1:] + "([^\d\w]|$)")
        else:
            dont_like_regex.append(
                "#[\d\w]*" + dont_likes + "[\d\w]*([^\d\w]|$)")

    for dont_likes_regex in dont_like_regex:
        quash = re.search(dont_likes_regex, image_text, re.IGNORECASE)
        if quash:
            quashed = (((quash.group(0)).split('#')[1]).split(' ')[0]).split('\n')[0].encode('utf-8')   # dismiss possible space and newlines
            iffy = ((re.split(r'\W+', dont_likes_regex))[3] if dont_likes_regex.endswith('*([^\\d\\w]|$)') else   # 'word' without format
                     (re.split(r'\W+', dont_likes_regex))[1] if dont_likes_regex.endswith('+([^\\d\\w]|$)') else   # '[word'
                      (re.split(r'\W+', dont_likes_regex))[3] if dont_likes_regex.startswith('#[\\d\\w]+') else     # ']word'
                       (re.split(r'\W+', dont_likes_regex))[1])                                                      # '#word'
            inapp_unit = 'Inappropriate! ~ contains "{}"'.format(
                quashed if iffy == quashed else
                '" in "'.join([str(iffy), str(quashed)]))
            return True, user_name, is_video, inapp_unit, "Undesired word"

    return False, user_name, is_video, 'None', "Success"



def like_image(browser, username, blacklist, logger, logfolder):
    """Likes the browser opened image"""
    # check action availability
    if quota_supervisor("likes") == "jump":
        return False, "jumped"

    like_xpath = "//button/span[@aria-label='Like']"
    unlike_xpath = "//button/span[@aria-label='Unlike']"

    # find first for like element
    like_elem = browser.find_elements_by_xpath(like_xpath)

    if len(like_elem) == 1:
        # sleep real quick right before clicking the element
        sleep(2)
        click_element(browser, like_elem[0])
        # check now we have unlike instead of like
        liked_elem = browser.find_elements_by_xpath(unlike_xpath)

        if len(liked_elem) == 1:
            logger.info('--> Image Liked!')
            update_activity('likes')

            if blacklist['enabled'] is True:
                action = 'liked'
                add_user_to_blacklist(
                    username, blacklist['campaign'], action, logger, logfolder)
            sleep(2)
            return True, "success"

        else:
            # if like not seceded wait for 2 min
            logger.info('--> Image was not able to get Liked! maybe blocked ?')
            sleep(120)

    else:
        liked_elem = browser.find_elements_by_xpath(unlike_xpath)
        if len(liked_elem) == 1:
            logger.info('--> Image already liked!')
            return False, "already liked"

    logger.info('--> Invalid Like Element!')

    return False, "invalid element"



def get_tags(browser, url):
    """Gets all the tags of the given description in the url"""

    #Check URL of the webpage, if it already is the one to be navigated, then do not navigate to it again
    web_address_navigator(browser, url)

    graphql = browser.execute_script(
        "return ('graphql' in window._sharedData.entry_data.PostPage[0])")
    if graphql:
        image_text = browser.execute_script(
            "return window._sharedData.entry_data.PostPage[0].graphql."
            "shortcode_media.edge_media_to_caption.edges[0].node.text")
    else:
        image_text = browser.execute_script(
            "return window._sharedData.entry_data."
            "PostPage[0].media.caption.text")

    tags = findall(r'#\w*', image_text)
    return tags



def get_links(browser, page, logger, media, element):
    # Get image links in scope from hashtag, location and other pages
    link_elems = element.find_elements_by_tag_name('a')
    sleep(2)
    links = []
    try:
        if link_elems:
            new_links = [link_elem.get_attribute('href') for link_elem in link_elems
                         if link_elem and link_elem.text in media]
            links.extend(new_links)
        else:
            logger.info("'{}' page does not contain a picture".format(page))
    except BaseException as e:
        logger.error("link_elems error {}".format(str(e)))
    return links



def verify_liking(browser, max, min, logger):
        """ Get the amount of existing existing likes and compare it against max & min values defined by user """
        try:
            likes_count = browser.execute_script(
                "return window._sharedData.entry_data."
                "PostPage[0].graphql.shortcode_media.edge_media_preview_like.count")
        except WebDriverException:
            try:
                browser.execute_script("location.reload()")
                likes_count = browser.execute_script(
                    "return window._sharedData.entry_data."
                    "PostPage[0].graphql.shortcode_media.edge_media_preview_like.count")
            except WebDriverException:
                try:
                    likes_count = (browser.find_element_by_css_selector(
                                        "section._1w76c._nlmjy > div > a > span").text)
                    if likes_count:
                        likes_count = format_number(likes_count)
                    else:
                        logger.info("Failed to check likes' count  ~empty string\n")
                        return True
                except NoSuchElementException:
                    logger.info("Failed to check likes' count\n")
                    return True

        if max is not None and likes_count > max:
            logger.info("Not liked this post! ~more likes exist off maximum limit at {}".format(likes_count))
            return False
        elif min is not None and likes_count < min:
            logger.info("Not liked this post! ~less likes exist off minumum limit at {}".format(likes_count))
            return False

        return True



