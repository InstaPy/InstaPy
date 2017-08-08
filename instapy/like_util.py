import re
import random

"""Module that handles the like features"""
from math import ceil
from re import findall
from selenium.webdriver.common.keys import Keys

from .time_util import sleep


def get_links_for_location(browser, location, amount, media=None):
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

    browser.get('https://www.instagram.com/explore/locations/'
                + location)
    sleep(2)

    # clicking load more
    body_elem = browser.find_element_by_tag_name('body')
    sleep(2)

    abort = True
    try:
        load_button = body_elem.find_element_by_xpath \
            ('//a[contains(@class, "_1cr2e _epyes")]')
    except:
        print('Load button not found, working with current images!')
    else:
        abort = False
        body_elem.send_keys(Keys.END)
        sleep(2)
        load_button.click()

    body_elem.send_keys(Keys.HOME)
    sleep(1)

    # Get links
    main_elem = browser.find_element_by_tag_name('main')
    link_elems = main_elem.find_elements_by_tag_name('a')
    total_links = len(link_elems)
    links = [link_elem.get_attribute('href') for link_elem in link_elems
             if link_elem.text in media]
    filtered_links = len(links)

    while (filtered_links < amount) and not abort:
        amount_left = amount - filtered_links
        # Average items of the right media per page loaded
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

    return links[:amount]


def get_links_for_tag(browser, tag, amount, media=None):
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
    sleep(2)

    # clicking load more
    body_elem = browser.find_element_by_tag_name('body')
    sleep(2)

    abort = True
    try:
        load_button = body_elem.find_element_by_xpath \
            ('//a[contains(@class, "_1cr2e _epyes")]')
    except:
        print('Load button not found, working with current images!')
    else:
        abort = False
        body_elem.send_keys(Keys.END)
        sleep(2)
        load_button.click()

    body_elem.send_keys(Keys.HOME)
    sleep(1)

    # Get links
    main_elem = browser.find_element_by_tag_name('main')
    link_elems = main_elem.find_elements_by_tag_name('a')
    total_links = len(link_elems)
    links = []
    filtered_links = 0
    try:
        if link_elems:
            links = [link_elem.get_attribute('href') for link_elem in link_elems
                     if link_elem and link_elem.text in media]
            filtered_links = len(links)

    except BaseException as e:
        print("link_elems error \n", str(e))

    while (filtered_links < amount) and not abort:
        amount_left = amount - filtered_links
        # Average items of the right media per page loaded
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

    return links[:amount]

def get_links_for_username(browser, username, amount, is_random=False, media=None):
    """Fetches the number of links specified
    by amount and returns a list of links""" 
    if media is None:
        # All known media types
        media = ['', 'Post','Video']
    elif media == 'Photo':
        # Include posts with multiple images in it
        media = ['','Post']
    else:
        # Make it an array to use it in the following part
        media = [media]

    print('Getting ', username, 'image list...')

    # Get  user profile page
    browser.get('https://www.instagram.com/' + username)
    sleep(2)
    
    body_elem = browser.find_element_by_tag_name('body')

    try:
        is_private = body_elem.find_element_by_xpath \
                ('//h2[@class="_glq0k"]')
    except:
        print('Interaction begin...')
        print('')
    else:
        if is_private:
            print('This user is private...')
            print('')
            return False

    sleep(2)

    abort = True
    
    # Clicking load more
    try:
        load_button = body_elem.find_element_by_xpath \
            ('//a[contains(@class, "_1cr2e _epyes")]')
    except:
        print('Load button not found, working with current images!')
    else:
        abort = False
        body_elem.send_keys(Keys.END)
        sleep(2)
        load_button.click()

    body_elem.send_keys(Keys.HOME)
    sleep(2)

    # Get Links
    main_elem = browser.find_element_by_tag_name('main')
    link_elems = main_elem.find_elements_by_tag_name('a')
    total_links = len(link_elems)
    links = []
    filtered_links = 0
    try:
        if link_elems:
            links = [link_elem.get_attribute('href') for link_elem in link_elems
                     if link_elem and link_elem.text in media]
            filtered_links = len(links)

    except BaseException as e:
        print("link_elems error \n", str(e))

    if is_random:
        # Expanding the pooulation for better random distribution
        amount = amount * 5

    while (filtered_links < amount) and not abort:
        amount_left = amount - filtered_links
        # Average items of the right media per page loaded
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

    if is_random:
        # Shuffle the population index
        links = random.sample(links, filtered_links)

    return links[:amount]
    


def check_link(browser, link, dont_like, ignore_if_contains, ignore_users,
               username, like_by_followers_upper_limit, like_by_followers_lower_limit):
    browser.get(link)
    sleep(2)

    """Check if the Post is Valid/Exists"""
    post_page = browser.execute_script("return window._sharedData.entry_data.PostPage")
    if post_page is None:
        print('Unavailable Page: {}'.format(link.encode('utf-8')))
        return True, None, None, 'Unavailable Page'

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

    print('Image from: {}'.format(user_name.encode('utf-8')))

    """Find the number of followes the user has"""
    if like_by_followers_upper_limit or like_by_followers_lower_limit:
        userlink = 'https://www.instagram.com/' + user_name
        browser.get(userlink)
        sleep(1)
        num_followers = browser.execute_script(
            "return window._sharedData.entry_data.ProfilePage[0].user.followed_by.count")
        browser.get(link)
        sleep(1)
        print('Number of Followers: {}'.format(num_followers))

        if like_by_followers_upper_limit and num_followers > like_by_followers_upper_limit:
            return True, user_name, is_video, 'Number of followers exceeds limit'
        if like_by_followers_lower_limit and num_followers < like_by_followers_lower_limit:
            return True, user_name, is_video, 'Number of followers does not reach minimum'

    print('Link: {}'.format(link.encode('utf-8')))
    print('Description: {}'.format(image_text.encode('utf-8')))

    """Check if the user_name is in the ignore_users list"""
    if (user_name in ignore_users) or (user_name == username):
        return True, user_name, is_video, 'Username'

    if any((word in image_text for word in ignore_if_contains)):
        return False, user_name, is_video, 'None'

    dont_like_regex = []

    for dont_likes in dont_like:
        if dont_likes.startswith("#"):
            dont_like_regex.append(dont_likes + "([^\d\w]|$)")
        elif dont_likes.startswith("["):
            dont_like_regex.append("#" + dont_likes[1:] + "[\d\w]+([^\d\w]|$)")
        elif dont_likes.startswith("]"):
            dont_like_regex.append("#[\d\w]+" + dont_likes[1:] + "([^\d\w]|$)")
        else:
            dont_like_regex.append("#[\d\w]*" + dont_likes + "[\d\w]*([^\d\w]|$)")

    for dont_likes_regex in dont_like_regex:
        if re.search(dont_likes_regex, image_text, re.IGNORECASE):
            return True, user_name, is_video, 'Inappropriate'

    return False, user_name, is_video, 'None'


def like_image(browser):
    """Likes the browser opened image"""
    like_elem = browser.find_elements_by_xpath("//a[@role = 'button']/span[text()='Like']")
    liked_elem = browser.find_elements_by_xpath("//a[@role = 'button']/span[text()='Unlike']")

    if len(like_elem) == 1:
        browser.execute_script(
            "document.getElementsByClassName('" + like_elem[0].get_attribute("class") + "')[0].click()")
        print('--> Image Liked!')
        sleep(2)
        return True
    elif len(liked_elem) == 1:
        print('--> Already Liked!')
        return False
    else:
        print('--> Invalid Like Element!')
        return False


def get_tags(browser, url):
    """Gets all the tags of the given description in the url"""
    browser.get(url)
    sleep(1)

    graphql = browser.execute_script("return ('graphql' in window._sharedData.entry_data.PostPage[0])")
    if graphql:
        image_text = browser.execute_script(
            "return window._sharedData.entry_data.PostPage[0].graphql.shortcode_media.edge_media_to_caption.edges[0].node.text")
    else:
        image_text = browser.execute_script("return window._sharedData.entry_data.PostPage[0].media.caption.text")

    tags = findall(r'#\w*', image_text)
    return tags
