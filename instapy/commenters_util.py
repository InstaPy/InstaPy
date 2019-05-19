"""Methods to extract the data for the given usernames profile"""
# code created by modification of original code copied from
# https://github.com/timgrossmann/instagram-profilecrawl/blob/master/util
# /extractor.py
import time
from time import sleep
from datetime import datetime, timedelta
import random
import collections
from operator import itemgetter
from selenium.webdriver.common.keys import Keys

from .util import get_number_of_posts
from .util import click_element
from .util import update_activity
from .util import web_address_navigator
from .util import username_url_to_username
from .util import scroll_bottom
from .util import get_users_from_dialog
from .util import progress_tracker
from .util import close_dialog_box
from .settings import Selectors

from selenium.common.exceptions import NoSuchElementException

from .xpath import read_xpath

def check_exists_by_xpath(browser, xpath):
    try:
        browser.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def remove_duplicates_preserving_order(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def extract_post_info(browser):
    """Get the information from the current post"""
    comments = []

    user_commented_list = []
    if browser.find_element_by_xpath(read_xpath(extract_post_info.__name__,"comment_list")):
        comment_list = browser.find_element_by_xpath(read_xpath(extract_post_info.__name__,"comment_list"))
        comments = comment_list.find_elements_by_tag_name(read_xpath(extract_post_info.__name__,"comments"))

        if len(comments) > 1:
            # load hidden comments
            more_comments = 0

            while (" comments" in comments[1].text):
                more_comments += 1
                print("loading more comments.")
                load_more_comments_element = browser.find_element_by_xpath(
                    read_xpath(extract_post_info.__name__,"load_more_comments_element"))
                click_element(browser, load_more_comments_element)
                # comment_list = post.find_element_by_tag_name('ul')
                comments = comment_list.find_elements_by_tag_name('li')

                if more_comments > 10:
                    print("Won't load more than that, moving on..")
                    break

            # if post autor didnt write description, more comments text is
            # in first comment
            if more_comments == 0:
                while (" comments" in comments[0].text):
                    more_comments += 1
                    print("loading more comments.")
                    load_more_comments_element = browser.find_element_by_xpath(
                        read_xpath(extract_post_info.__name__,"load_more_comments_element_alt"))
                    click_element(browser, load_more_comments_element)
                    # comment_list = post.find_element_by_tag_name('ul')
                    comments = comment_list.find_elements_by_tag_name('li')

                    if more_comments > 10:
                        print("Won't load more than that, moving on..")
                        break

            # adding who commented into user_commented_list
            try:
                for comm in comments:
                    user_commented = comm.find_element_by_tag_name(
                        'a').get_attribute("href").split('/')
                    user_commented_list.append(user_commented[3])

            except Exception:
                print("cant get comments")

        print(len(user_commented_list), " comments.")
    date_time = browser.find_element_by_tag_name('time').get_attribute(
        "datetime")

    return user_commented_list, date_time


def extract_information(browser, username, daysold, max_pic):
    """Get all the information for the given username"""
    web_address_navigator(browser, 'https://www.instagram.com/' + username)

    try:
        num_of_posts = get_number_of_posts(browser)
        num_of_posts = (min(num_of_posts, max_pic))
        # we don't need to scroll more than is max number of posts we want
        # to extract

    except Exception:
        print("\nError: Couldn't get user profile. Moving on..")
        return []

    # PROFILE SCROLLING AND HARVESTING LINKS
    try:
        body_elem = browser.find_element_by_tag_name('body')

        links = []
        links2 = []
        links3 = []
        # list links contains 30 links from the current view, as that is the
        # maximum Instagram is showing at one time
        # list links2 contains all the links collected so far without
        # duplicates, in mixed order
        # list links3 contains all the links collected so far with
        # duplicates in preserved order
        previouslen = -1

        # every 60 links we will open picture and check it's date not to
        # scroll endlessly in huge profiles such as natgeo
        opened_overlay = 42
        sleep(0.5)

        # cycle that scrolls down the feed and collects links and saving
        # them into links2
        while (len(links2) < num_of_posts):
            prev_divs = browser.find_elements_by_tag_name('main')
            # harvesting current img links:
            links_elems = [div.find_elements_by_tag_name('a') for div in
                           prev_divs]
            links = sum([[link_elem.get_attribute('href')
                          for link_elem in elems] for elems in links_elems],
                        [])
            # saving links for later:
            for link in links:
                if "/p/" in link:
                    links2.append(link)
                    links3.append(link)
            links2 = list(set(links2))
            # if after previous scroll, size of links2 didnt increase,
            # we should finish else we continue
            if (len(links2) == previouslen):
                print("Cannot scroll, quitting..")
                sleep(0.5)
                break

            else:
                print("Scrolling profile ", len(links2), "/", num_of_posts)

                # TRYING TO END SCROLLING IN TIME
                # check the date of the image once in a 60 to not scroll too
                # much
                # only do it if we have a lot to images to go
                if (num_of_posts - len(links2) > 60) and (
                        len(links2) > opened_overlay):
                    opened_overlay += 60

                    print("clicking on one photo..")
                    try:
                        one_pic_elem = browser.find_element_by_xpath(
                            read_xpath(extract_information.__name__,"one_pic_elem"))
                        click_element(browser, one_pic_elem)
                    except Exception:
                        print("Error: cant click on the photo..")

                    sleep(1.5)

                    # following 6 lines give like to opened picture, to use
                    # our time effectively and look less suspicious
                    try:
                        like_element = browser.find_elements_by_xpath(
                            read_xpath(extract_information.__name__,"like_element"))
                        click_element(browser, like_element[0])
                        print("clicking like..")
                    except Exception:
                        pass
                    sleep(2)

                    pic_date_time = browser.find_element_by_tag_name(
                        'time').get_attribute("datetime")
                    pastdate = datetime.now() - timedelta(days=daysold)
                    date_of_pic = datetime.strptime(pic_date_time,
                                                    "%Y-%m-%dT%H:%M:%S.%fZ")

                    print("closing overlay")
                    close_overlay = browser.find_element_by_xpath(
                        read_xpath(extract_information.__name__,"close_overlay"))
                    click_element(browser, close_overlay)

                    print("date of this picture was:", date_of_pic)

                    if (date_of_pic < pastdate):
                        print("\nFinished scrolling, too old photos")
                        sleep(3)
                        break
                    else:
                        print(
                            "\nPhotos seems to be fresh, continuing scrolling")
                        sleep(2)

                previouslen = len(links2)
                body_elem.send_keys(Keys.END)
                sleep(1.5)

    except NoSuchElementException as err:
        print(
            '\n- Something went terribly wrong\n - Stopping everything and '
            'moving on with what I have\n')
        print(err)

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
        print("\n", counter, " of max ", len(links4), " --- ", max_pic,
              " to go.")
        counter = counter + 1
        print("\nScrapping link: ", link)

        try:
            web_address_navigator(browser, link)
            user_commented_list, pic_date_time = extract_post_info(browser)
            user_commented_total_list = user_commented_total_list + \
                                        user_commented_list

            # stop if date older than daysago
            pastdate = datetime.now() - timedelta(days=daysold)
            date_of_pic = datetime.strptime(pic_date_time,
                                            "%Y-%m-%dT%H:%M:%S.%fZ")
            print("date of pic: ", date_of_pic)
            if (date_of_pic > pastdate):
                print("Recent pic, continue..")
            else:
                print("Old pic, ending getting users who commented.")
                sleep(3)
                break
            sleep(1)
        except NoSuchElementException:
            print('- Could not get information from post: ' + link)

    # PREPARE THE USER LIST TO EXPORT
    # sorts the list by frequencies, so users who comment the most are at
    # the top
    counter = collections.Counter(user_commented_total_list)
    com = sorted(counter.most_common(), key=itemgetter(1, 0), reverse=True)
    com = map(lambda x: [x[0]] * x[1], com)
    user_commented_total_list = [item for sublist in com for item in sublist]

    # remove duplicates preserving order (that's why not using set())
    user_commented_list = []
    last = ''
    for i in range(len(user_commented_total_list)):
        if username.lower() != user_commented_total_list[i]:
            if (last != user_commented_total_list[i] and 'p' not in
                    user_commented_total_list[i]):
                user_commented_list.append(user_commented_total_list[i])
            last = user_commented_total_list[i]

    print("\nGetting list of users who commented on this profile finished: ")
    print(user_commented_list, "\n")
    return user_commented_list


def users_liked(browser, photo_url, amount=100):
    photo_likers = []
    try:
        web_address_navigator(browser, photo_url)
        photo_likers = likers_from_photo(browser, amount)
        sleep(2)
    except NoSuchElementException:
        print('Could not get information from post: ' + photo_url,
              ' nothing to return')

    return photo_likers


def likers_from_photo(browser, amount=20):
    """ Get the list of users from the 'Likes' dialog of a photo """

    liked_counter_button = "//div/article/div[2]/section[2]/div/div/a"

    try:
        liked_this = browser.find_elements_by_xpath(liked_counter_button)
        likers = []

        for liker in liked_this:
            if " like this" not in liker.text:
                likers.append(liker.text)

        if check_exists_by_xpath(browser, liked_counter_button):
            if " others" in liked_this[-1].text:
                element_to_click = liked_this[-1]

            elif " likes" in liked_this[0].text:
                element_to_click = liked_this[0]

            else:
                print("Few likes, not guaranteed you don't follow these"
                      " likers already.\nGot photo likers: {}\n"
                      .format(likers))
                return likers

        else:
            print("Couldn't find liked counter button. May be a video.")
            print("Moving on..")
            return []

        sleep(1)
        click_element(browser, element_to_click)
        print("opening likes")
        # update server calls
        # update_activity()

        sleep(1)

        # get a reference to the 'Likes' dialog box
        dialog = browser.find_element_by_xpath(
            Selectors.likes_dialog_body_xpath)

        # scroll down the page
        previous_len = -1
        browser.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
        update_activity()
        sleep(1)

        start_time = time.time()
        user_list = []

        while (not user_list
               or (len(user_list) != previous_len)
               and (len(user_list) < amount)):

            if previous_len + 10 >= amount:
                print("\nScrolling finished")
                if amount < 10:
                    user_list = get_users_from_dialog(user_list, dialog)
                sleep(1)
                break

            previous_len = len(user_list)
            scroll_bottom(browser, dialog, 2)

            user_list = get_users_from_dialog(user_list, dialog)

            # write & update records at Progress Tracker
            progress_tracker(len(user_list), amount, start_time, None)

        print('\n')
        random.shuffle(user_list)
        sleep(1)

        close_dialog_box(browser)

        print(
            "Got {} likers shuffled randomly whom you can follow:\n{}"
            "\n".format(
                len(user_list), user_list))
        return user_list

    except Exception as exc:
        print("Some problem occured!\n\t{}".format(str(exc).encode("utf-8")))
        return []


def get_photo_urls_from_profile(browser, username, links_to_return_amount=1,
                                randomize=True):
    # try:
    # input can be both username or user profile url
    username = username_url_to_username(username)
    print("\nGetting likers from user: ", username, "\n")
    web_address_navigator(browser,
                          'https://www.instagram.com/' + username + '/')
    sleep(1)

    photos_a_elems = browser.find_elements_by_xpath(read_xpath(get_photo_urls_from_profile.__name__,"photos_a_elems"))

    links = []
    for photo_element in photos_a_elems:
        photo_url = photo_element.get_attribute("href")
        # print ("photo url: ", photo_url)
        if ("/p/" in photo_url):
            links.append(photo_url)

    if randomize is True:
        print("shuffling links")
        random.shuffle(links)
    print("Got ", len(links), ", returning ",
          min(links_to_return_amount, len(links)), " links: ",
          links[:links_to_return_amount])
    sleep(1)
    return links[:links_to_return_amount]