"""Methods to extract the data for the given usernames profile"""
# code created by modification of original code copied from
# https://github.com/timgrossmann/instagram-profilecrawl/blob/master/util/extractor.py
# import built-in & third-party modules
import collections
import random
import time
from datetime import datetime, timedelta
from operator import itemgetter
from time import sleep

# import exceptions
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# import InstaPy modules
from .util import (
    click_element,
    close_dialog_box,
    get_number_of_posts,
    get_users_from_dialog,
    progress_tracker,
    scroll_bottom,
    update_activity,
    username_url_to_username,
    web_address_navigator,
)
from .xpath import read_xpath


def check_exists_by_xpath(browser, xpath):
    try:
        browser.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


def remove_duplicates_preserving_order(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def extract_post_info(browser, logger):
    """Get the information from the current post"""
    web_address_navigator(browser, browser.current_url + "comments/")
    comments = []
    user_commented_list = []
    last_comment_count = 0
    # load all hidden comments
    while check_exists_by_xpath(
        browser, read_xpath(extract_post_info.__name__, "load_more_comments_element")
    ):
        load_more_comments_element = browser.find_element(
            By.XPATH,
            read_xpath(extract_post_info.__name__, "load_more_comments_element"),
        )
        click_element(browser, load_more_comments_element)
        sleep(0.5)
        # get comment list
        comment_list = browser.find_element(
            By.XPATH, read_xpath(extract_post_info.__name__, "comment_list")
        )
        comments = comment_list.find_elements(
            By.XPATH, read_xpath(extract_post_info.__name__, "comments")
        )
        # check instagram comment load bug
        if len(comments) == last_comment_count:
            break
        if (len(comments) - last_comment_count) < 3:
            break
        last_comment_count = len(comments)

    # get all comment list
    comment_list = browser.find_element(
        By.XPATH, read_xpath(extract_post_info.__name__, "comment_list")
    )
    comments = comment_list.find_elements(
        By.XPATH, read_xpath(extract_post_info.__name__, "comments")
    )

    # get all commenter list
    try:
        for comm in comments:
            user_commented = (
                comm.find_element(By.TAG_NAME, "a").get_attribute("href").split("/")
            )
            logger.info("Found commenter: {}".format(user_commented[3]))
            user_commented_list.append(user_commented[3])

    except Exception as e:
        logger.warning("Cant get comments".format(str(e).encode("utf-8")))

    date_time = browser.find_element(By.TAG_NAME, "time").get_attribute("datetime")
    return user_commented_list, date_time


def extract_information(browser, username, daysold, max_pic, logger):
    """Get all the information for the given username"""
    web_address_navigator(browser, "https://www.instagram.com/" + username)

    try:
        num_of_posts = get_number_of_posts(browser)
        num_of_posts = min(num_of_posts, max_pic)
        # we don't need to scroll more than is max number of posts we want
        # to extract

        links1 = []
        links2 = []
        links3 = []
        # list links1 contains 30 links from the current view, as that is the
        # maximum Instagram is showing at one time
        # list links2 contains all the links collected so far without
        # duplicates, in mixed order
        # list links3 contains all the links collected so far with
        # duplicates in preserved order

    except Exception as e:
        logger.error(
            "Error: Couldn't get user profile. Moving on... \n\t{}".format(
                str(e).encode("utf-8")
            )
        )
        return []

    # PROFILE SCROLLING AND HARVESTING LINKS
    try:
        body_elem = browser.find_element(By.TAG_NAME, "body")
        previouslen = -1

        # every 60 links we will open picture and check it's date not to
        # scroll endlessly in huge profiles such as natgeo
        opened_overlay = 42
        sleep(0.5)

        # cycle that scrolls down the feed and collects links and saving
        # them into links2
        while len(links2) < num_of_posts:
            prev_divs = browser.find_elements(By.TAG_NAME, "main")
            # harvesting current img links:
            links_elems = [div.find_elements(By.TAG_NAME, "a") for div in prev_divs]
            links1 = sum(
                [
                    [link_elem.get_attribute("href") for link_elem in elems]
                    for elems in links_elems
                ],
                [],
            )
            # saving links for later:
            for link in links1:
                if "/p/" in link:
                    links2.append(link)
                    links3.append(link)

            links2 = list(set(links2))
            # if after previous scroll, size of links2 didnt increase,
            # we should finish else we continue
            if len(links2) == previouslen:
                logger.info("Cannot scroll, quitting...")
                sleep(0.5)
                break

            else:
                logger.info(
                    "Scrolling profile. Links and posts: {}/{}",
                    len(links2),
                    num_of_posts,
                )

                # TRYING TO END SCROLLING IN TIME
                # check the date of the image once in a 60 to not scroll too
                # much
                # only do it if we have a lot to images to go
                if (num_of_posts - len(links2) > 60) and (len(links2) > opened_overlay):
                    opened_overlay += 60

                    logger.info("Clicking on one photo...")
                    try:
                        one_pic_elem = browser.find_element(
                            By.XPATH,
                            read_xpath(extract_information.__name__, "one_pic_elem"),
                        )
                        click_element(browser, one_pic_elem)
                    except Exception:
                        logger.error("Cant click on the photo...")

                    sleep(1.5)

                    # following 6 lines give like to opened picture, to use
                    # our time effectively and look less suspicious
                    try:
                        like_element = browser.find_elements(
                            By.XPATH,
                            read_xpath(extract_information.__name__, "like_element"),
                        )
                        click_element(browser, like_element[0])
                        logger.info("Clicking like...")
                    except Exception:
                        pass
                    sleep(2)

                    pic_date_time = browser.find_element(
                        By.TAG_NAME, "time"
                    ).get_attribute("datetime")
                    pastdate = datetime.now() - timedelta(days=daysold)
                    date_of_pic = datetime.strptime(
                        pic_date_time, "%Y-%m-%dT%H:%M:%S.%fZ"
                    )

                    # Informational
                    logger.info("Closing overlay...")
                    close_overlay = browser.find_element(
                        By.XPATH,
                        read_xpath(extract_information.__name__, "close_overlay"),
                    )
                    click_element(browser, close_overlay)

                    logger.info("Date of this picture was: {}".format(date_of_pic))

                    if date_of_pic < pastdate:
                        logger.info("Finished scrolling, too old photos...")
                        sleep(3)
                        break
                    else:
                        logger.info("Photos seems to be fresh, continuing scrolling...")
                        sleep(2)

                previouslen = len(links2)
                body_elem = browser.find_element(By.TAG_NAME, "body")
                body_elem.send_keys(Keys.END)
                sleep(1.5)

    except (NoSuchElementException, StaleElementReferenceException) as e:
        logger.warning(
            "- Something went terribly wrong\n - Stopping everything and "
            "moving on with what I have. \n\t{}".format(str(e).encode("utf-8"))
        )

    links4 = remove_duplicates_preserving_order(links3)

    # PICTURES SCRAPPER ONE BY ONE
    # into user_commented_total_list go all username links who commented on
    # any post of this user
    counter = 1
    user_commented_total_list = []
    for link in links4:
        if max_pic <= 0:
            break
        max_pic -= 1
        logger.info("{} of max {} --- {} to go.".format(counter, len(links4), max_pic))
        counter = counter + 1
        logger.info("Scrapping link: {}".format(link))

        try:
            web_address_navigator(browser, link)
            user_commented_list, pic_date_time = extract_post_info(browser, logger)
            user_commented_total_list = user_commented_total_list + user_commented_list

            # stop if date older than daysago
            pastdate = datetime.now() - timedelta(days=daysold)
            date_of_pic = datetime.strptime(pic_date_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            logger.info("Date of pic: {}".format(date_of_pic))

            if date_of_pic > pastdate:
                logger.info("Recent pic, continue...")
            else:
                logger.info("Old pic, ending getting users who commented.")
                sleep(3)
                break
            sleep(1)
        except NoSuchElementException as e:
            logger.error(
                "- Could not get information from post: {} \n\t{}".format(
                    link, str(e).encode("utf-8")
                )
            )

    # PREPARE THE USER LIST TO EXPORT
    # sorts the list by frequencies, so users who comment the most are at
    # the top
    counter = collections.Counter(user_commented_total_list)
    com = sorted(counter.most_common(), key=itemgetter(1, 0), reverse=True)
    com = map(lambda x: [x[0]] * x[1], com)
    user_commented_total_list = [item for sublist in com for item in sublist]

    # remove duplicates preserving order (that's why not using set())
    user_commented_list = []
    last = ""
    for index, _ in enumerate(user_commented_total_list):
        if username.lower() != user_commented_total_list[index]:
            if (
                last != user_commented_total_list[index]
                and "p" not in user_commented_total_list[index]
            ):
                user_commented_list.append(user_commented_total_list[index])
            last = user_commented_total_list[index]

    logger.info(
        "Getting list of users who commented on this profile finished: {}".format(
            user_commented_list
        )
    )
    return user_commented_list


def users_liked(browser, photo_url, amount=100, logger=None):
    photo_likers = []
    try:
        web_address_navigator(browser, photo_url)
        photo_likers = likers_from_photo(browser, amount, logger)
        sleep(2)
    except NoSuchElementException:
        logger.info(
            "Could not get information from post: {} nothing to return".format(
                photo_url
            )
        )

    return photo_likers


def likers_from_photo(browser, amount=20, logger=None):
    """Get the list of users from the 'Likes' dialog of a photo"""

    try:
        if check_exists_by_xpath(
            browser, read_xpath(likers_from_photo.__name__, "second_counter_button")
        ):
            liked_this = browser.find_elements(
                By.XPATH,
                read_xpath(likers_from_photo.__name__, "second_counter_button"),
            )
            element_to_click = liked_this[0]
        elif check_exists_by_xpath(
            browser, read_xpath(likers_from_photo.__name__, "liked_counter_button")
        ):
            liked_this = browser.find_elements(
                By.XPATH, read_xpath(likers_from_photo.__name__, "liked_counter_button")
            )
            likers = []

            for liker in liked_this:
                if " like this" not in liker.text:
                    likers.append(liker.text)

            if " others" in liked_this[-1].text:
                element_to_click = liked_this[-1]

            elif " likes" in liked_this[0].text:
                element_to_click = liked_this[0]

            else:
                logger.info(
                    "Few likes, not guaranteed you don't follow these"
                    " likers already.\nGot photo likers: {}".format(likers)
                )
                return likers

        else:
            # If you are here, it is because you discovered that sometimes an
            # xpath does not work, at the moment the number of views in a video
            # does not behave like the number of likes in a photo. Clicking on
            # the number of views only shows the same number in a floating
            # window; no users to get.
            # www.instagram.com/p/CASprIDgOOO/ -> 3,275,561 views -> 11-24-20
            logger.info("Couldn't find liked counter button. May be a video.")
            logger.info("Trying again for some image, moving on...")
            return []

        sleep(1)
        click_element(browser, element_to_click)
        logger.info("Opening likes...")

        # update server calls
        update_activity(browser, state=None)
        sleep(1)

        # get a reference to the 'Likes' dialog box
        dialog = browser.find_element(
            By.XPATH, read_xpath("class_selectors", "likes_dialog_body_xpath")
        )

        # scroll down the page
        previous_len = -1
        browser.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", dialog
        )
        update_activity(browser, state=None)
        sleep(1)

        start_time = time.time()
        user_list = []

        while (
            not user_list
            or (len(user_list) != previous_len)
            and (len(user_list) < amount)
        ):

            if previous_len + 10 >= amount:
                logger.info("Scrolling finished...")
                if amount < 10:
                    user_list = get_users_from_dialog(user_list, dialog, logger)
                sleep(1)
                break

            previous_len = len(user_list)
            scroll_bottom(browser, dialog, 2)

            user_list = get_users_from_dialog(user_list, dialog, logger)

            # write & update records at Progress Tracker
            progress_tracker(len(user_list), amount, start_time, None)
            print("\n")

        random.shuffle(user_list)
        sleep(1)

        close_dialog_box(browser)

        logger.info(
            "Got {} likers shuffled randomly whom you can follow:\n{}".format(
                len(user_list), user_list
            )
        )
        return user_list

    except Exception as exc:
        logger.warning("Some problem occurred! \n\t{}".format(str(exc).encode("utf-8")))
        return []


def get_photo_urls_from_profile(
    browser, username, links_to_return_amount=1, randomize=True, logger=None
):
    # try:
    # input can be both username or user profile url
    username = username_url_to_username(username)
    logger.info("Getting likers from user: {}".format(username))

    web_address_navigator(browser, "https://www.instagram.com/" + username + "/")
    sleep(1)

    photos_a_elems = browser.find_elements(
        By.XPATH, read_xpath(get_photo_urls_from_profile.__name__, "photos_a_elems")
    )

    links = []
    for photo_element in photos_a_elems:
        photo_url = photo_element.get_attribute("href")
        # logger.info("Photo url: {}".format(photo_url))
        if "/p/" in photo_url:
            links.append(photo_url)

    if randomize is True:
        logger.info("Shuffling links")
        random.shuffle(links)

    logger.info(
        "Got {} , returning {} links: {}".format(
            len(links),
            min(links_to_return_amount, len(links)),
            links[:links_to_return_amount],
        )
    )

    sleep(1)
    return links[:links_to_return_amount]
