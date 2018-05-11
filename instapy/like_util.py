import re
import random

"""Module that handles the like features"""
from .util import format_number
from math import ceil
from re import findall
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException

from .time_util import sleep
from .util import update_activity
from .util import add_user_to_blacklist
from .util import click_element
from .unfollow_util import get_relationship_counts


def get_links_from_feed(browser, amount, num_of_search, logger):
    """Fetches random number of links from feed and returns a list of links"""

    browser.get('https://www.instagram.com')
    # update server calls
    update_activity()
    sleep(2)

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

    browser.get('https://www.instagram.com/explore/locations/' + location)
    # update server calls
    update_activity()
    sleep(2)

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

    browser.get('https://www.instagram.com/explore/tags/'
                + (tag[1:] if tag[:1] == '#' else tag))
    # update server calls
    update_activity()
    sleep(2)

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

    possible_posts = format_number(browser.find_element_by_xpath(
                                "//span[contains(@class, '_fd86t')]").text)

    logger.info("desired amount: {}  |  top posts [{}]: {}  |  possible posts: {}".format(amount,
                                      ('enabled' if not skip_top_posts else 'disabled'), len(top_posts), possible_posts))
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
                        logger.info("'{}' tag POSSIBLY has less images than desired...".format(tag[1:] if tag[:1] == '#' else tag))
                        break
            else:
                filtered_links = len(links)
                try_again = 0
                nap = 1.5
    except:
        raise
    
    sleep(4)
    
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

    # Get  user profile page
    browser.get('https://www.instagram.com/' + username)
    # update server calls
    update_activity()

    body_elem = browser.find_element_by_tag_name('body')

    try:
        is_private = body_elem.find_element_by_xpath(
            '//h2[@class="_kcrwx"]')
    except:
        logger.info('Interaction begin...')
    else:
        if is_private:
            logger.warning('This user is private...')
            return False

    abort = True

    try:
        load_button = body_elem.find_element_by_xpath(
            '//a[contains(@class, "_1cr2e _epyes")]')
    except:
        try:
            # scroll down to load posts
            for i in range(int(ceil(amount/12))):
                browser.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                sleep(2)
        except:
            logger.warning(
                'Load button not found, working with current images!')
        else:
            abort = False
            body_elem.send_keys(Keys.END)
            sleep(2)
            # update server calls
            update_activity()
    else:
        abort = False
        body_elem.send_keys(Keys.END)
        sleep(2)
        click_element(browser, load_button) # load_button.click()
        # update server calls
        update_activity()

    body_elem.send_keys(Keys.HOME)
    sleep(2)

    # Get Links
    main_elem = browser.find_element_by_tag_name('main')
    link_elems = main_elem.find_elements_by_tag_name('a')
    total_links = len(link_elems)
    # Check there is at least one link
    if total_links == 0:
        return False
    links = []
    filtered_links = 0
    try:
        if link_elems:
            links = [link_elem.get_attribute('href') for link_elem in link_elems
                     if link_elem and link_elem.text in media]
            filtered_links = len(links)

    except BaseException as e:
        logger.error("link_elems error {}}".format(str(e)))

    if randomize:
        # Expanding the pooulation for better random distribution
        amount = amount * 5

    while (filtered_links < amount) and not abort:
        amount_left = amount - filtered_links

        # Average items of the right media per page loaded (total links checked for not zero)
        new_per_page = ceil(12 * filtered_links / total_links)

        if new_per_page == 0:
            # Avoid division by zero
            new_per_page = 1. / 12.
        # Number of page load needed
        new_needed = int(ceil(amount_left / new_per_page))

        if new_needed > 12:
            # Don't go bananas trying to get all of instagram!
            new_needed = 12

        for i in range(new_needed):  # add images x * 12
            # Keep the latest window active while loading more posts
            before_load = total_links
            body_elem.send_keys(Keys.END)
            # update server calls
            update_activity()
            sleep(1)
            body_elem.send_keys(Keys.HOME)
            sleep(1)
            link_elems = main_elem.find_elements_by_tag_name('a')
            total_links = len(link_elems)
            abort = (before_load == total_links)
            if abort:
                break

        links = [link_elem.get_attribute('href') for link_elem in link_elems
                 if link_elem.text in media]
        filtered_links = len(links)

    if randomize:
        # Shuffle the population index
        links = random.sample(links, filtered_links)

    return links[:amount]


def check_link(browser, link, dont_like, ignore_if_contains, ignore_users, username,
               potency_ratio, delimit_by_numbers, max_followers, max_following, min_followers, min_following, logger):
    """
    Check the given link if it is appropriate

    :param browser: The selenium webdriver instance
    :param link:
    :param dont_like: hashtags of inappropriate phrases
    :param ignore_if_contains:
    :param ignore_users:
    :param username:
    :param potency_ratio:
    :param delimit_by_numbers: pre-defined precise relationship bounds
    :param max_followers:
    :param max_following:
    :param min_followers:
    :param min_following:
    :param logger: the logger instance
    :return: tuple of
        boolean: True if inappropriate,
        string: the username,
        boolean: True if it is video media,
        string: the message if inappropriate else 'None'
    """
    browser.get(link)
    # update server calls
    update_activity()
    sleep(2)

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
        logger.warning('Unavailable Page: {}'.format(link.encode('utf-8')))
        return True, None, None, 'Unavailable Page', "Failure"

    """Gets the description of the link and checks for the dont_like tags"""
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

    
    """Checks the potential of target user by relationship status in order to delimit actions within the desired boundary"""
    if potency_ratio or delimit_by_numbers and (max_followers or max_following or min_followers or min_following):

        relationship_ratio = None
        reverse_relationship = False

        # Get followers & following counts
        followers_count, following_count = get_relationship_counts(browser, user_name, logger)

        browser.get(link)
        # update server calls
        update_activity()
        sleep(1)

        if potency_ratio and potency_ratio < 0:
            potency_ratio *= -1
            reverse_relationship = True

        if followers_count and following_count:
            relationship_ratio = (float(followers_count)/float(following_count)
                       if not reverse_relationship
                        else float(following_count)/float(followers_count))
            
        logger.info('User: {} >> followers: {}  |  following: {}  |  relationship ratio: {}'.format(user_name,
        followers_count if followers_count else 'unknown',
        following_count if following_count else 'unknown',
        float("{0:.2f}".format(relationship_ratio)) if relationship_ratio else 'unknown'))

        if followers_count  or following_count:
            if potency_ratio and not delimit_by_numbers:
                if relationship_ratio and relationship_ratio < potency_ratio:
                        return True, user_name, is_video, \
                            "{} is not a {} with the relationship ratio of {}".format(
                            user_name, "potential user" if not reverse_relationship else "massive follower",
                            float("{0:.2f}".format(relationship_ratio))), "Relationship bounds"

            elif delimit_by_numbers:
                if followers_count:
                    if max_followers:
                        if followers_count > max_followers:
                            return True, user_name, is_video, \
                                "User {}'s followers count exceeds maximum limit".format(user_name), "Relationship bounds"
                    if min_followers:
                        if followers_count < min_followers:
                            return True, user_name, is_video, \
                                "User {}'s followers count is less than minimum limit".format(user_name), "Relationship bounds"
                if following_count:
                    if max_following:
                        if following_count > max_following:
                            return True, user_name, is_video, \
                                "User {}'s following count exceeds maximum limit".format(user_name), "Relationship bounds"
                    if min_following:
                        if following_count < min_following:
                            return True, user_name, is_video, \
                                "User {}'s following count is less than minimum limit".format(user_name), "Relationship bounds"
                if potency_ratio:
                    if relationship_ratio and relationship_ratio < potency_ratio:
                        return True, user_name, is_video, \
                            "{} is not a {} with the relationship ratio of {}".format(
                            user_name, "potential user" if not reverse_relationship else "massive follower",
                            float("{0:.2f}".format(relationship_ratio))), "Relationship bounds"


    logger.info('Link: {}'.format(link.encode('utf-8')))
    logger.info('Description: {}'.format(image_text.encode('utf-8')))

    """Check if the user_name is in the ignore_users list"""
    if (user_name in ignore_users) or (user_name == username):
        return True, user_name, is_video, 'Username', "Undesired user"

    if any((word in image_text for word in ignore_if_contains)):
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
    # fetch spans fast
    spans = [x.text.lower() for x in browser.find_elements_by_xpath("//article//a[@role='button']/span")]

    if 'like' in spans:
        like_elem = browser.find_elements_by_xpath(
            "//a[@role='button']/span[text()='Like']/..")

        # sleep real quick right before clicking the element
        sleep(2)
        click_element(browser, like_elem[0])
        # check now we have unlike instead of like
        liked_elem = browser.find_elements_by_xpath(
            "//a[@role='button']/span[text()='Unlike']")
        if len(liked_elem) == 1:
            logger.info('--> Image Liked!')
            update_activity('likes')
            if blacklist['enabled'] is True:
                action = 'liked'
                add_user_to_blacklist(
                    browser, username, blacklist['campaign'], action, logger, logfolder
                )
            sleep(2)
            return True
        else:
            # if like not seceded wait for 2 min
            logger.info('--> Image was not able to get Liked! maybe blocked ?')
            sleep(120)
    else:
        liked_elem = browser.find_elements_by_xpath(
            "//a[@role='button']/span[text()='Unlike']")
        if len(liked_elem) == 1:
            logger.info('--> Image already liked! ')
            return False

    logger.info('--> Invalid Like Element!')
    return False


def get_tags(browser, url):
    """Gets all the tags of the given description in the url"""
    browser.get(url)
    # update server calls
    update_activity()
    sleep(1)

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


def get_links(browser, tag, logger, media, element):
    # Get image links in scope from tags
    link_elems = element.find_elements_by_tag_name('a')
    sleep(2)
    links = []
    try:
        if link_elems:
            new_links = [link_elem.get_attribute('href') for link_elem in link_elems
                         if link_elem and link_elem.text in media]
            links.extend(new_links)
        else:
            logger.info("'{}' tag does not contain a picture".format(tag[1:] if tag[:1] == '#' else tag))
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
                    likes_count = format_number(browser.find_element_by_css_selector(
                                        "section._1w76c._nlmjy > div > a > span").text)
                except NoSuchElementException:
                    logger.info("Failed to check likes' count...\n")
                    raise
                    return True
        
        if max is not None and likes_count > max:
            logger.info("Not liked this post! ~more likes exist off maximum limit at {}".format(likes_count))
            return False
        elif min is not None and likes_count < min:
            logger.info("Not liked this post! ~less likes exist off minumum limit at {}".format(likes_count))
            return False

        return True
