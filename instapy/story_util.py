import time
from random import randint
from selenium.common.exceptions import NoSuchElementException
from .util import click_element
from .util import web_address_navigator
from .xpath import read_xpath

import requests

def get_story_data(browser, elem, action_type, logger):
    """not used fort the moment, more coding needed to understand this"""

    # if things change in the future, modify here:
    query_hash = "cda12de4f7fd3719c0569ce03589f4c4"

    if action_type == "tag":
        # pretty easy here, we just have to fill tag_names with the tag we want
        graphql_query_URL = "https://www.instagram.com/graphql/query/?query_hash" + \
                            "={}".format(query_hash)+ \
                            "&variables={{\"reel_ids\":[],\"tag_names\":[\"{}\"],\"location_ids\":[],".format(elem) + \
                            "\"highlight_reel_ids\":[],\"precomposed_overlay\":false,\"show_story_viewer_list\":true," + \
                            "\"story_viewer_fetch_count\":50,\"story_viewer_cursor\":\"\"," + \
                            "\"stories_video_dash_manifest\":false}"
    else:
        # if we are on a user page, we need to find out it's profile id and fill it into reel_ids
        elem_id = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].graphql.user.id")
        graphql_query_URL = "https://www.instagram.com/graphql/query/?query_hash" + \
                            "={}".format(query_hash) + \
                            "&variables={{\"reel_ids\":[\"{}\"],\"tag_names\":[],\"location_ids\":[],".format(elem_id) + \
                            "\"highlight_reel_ids\":[],\"precomposed_overlay\":false,\"show_story_viewer_list\":true," + \
                            "\"story_viewer_fetch_count\":50,\"story_viewer_cursor\":\"\"," + \
                            "\"stories_video_dash_manifest\":false}"
    cookies = browser.get_cookies()
    print(cookies)
    s = requests.Session()

    for cookie in cookies:
        print(cookie['name'])
        required_args = {
            'name': cookie['name'],
            'value': cookie['value']
        }
        if (cookie['name'] == "urlgen") or (cookie['name'] == "rur"):
            optional_args = {
                'domain': cookie['domain'],
                'secure': cookie['secure'],
                'rest': { 'HttpOnly': cookie['httpOnly']},
                'path': cookie['path']
            }
        else:
            optional_args = {
                'domain': cookie['domain'],
                'secure': cookie['secure'],
                'rest': {'HttpOnly': cookie['httpOnly']},
                'path': cookie['path'],
                'expires': cookie['expiry']
            }
        s.cookies.set(**required_args, **optional_args)

    response = s.get(graphql_query_URL)

    #we have the json describing the stories
    #output the amount of segments, total time, check if there is anything new
    #in case of tags, the users
    #


def watch_story(browser, elem, logger, action_type):
    """
        Load Stories, and watch it until there is no more stores
        to watch for the related element
    """

    if action_type == "tag":
        story_link = "https://www.instagram.com/explore/tags/{}".format(elem)

    else:
        story_link = "https://www.instagram.com/{}".format(elem)

    web_address_navigator(browser, story_link)
    get_story_data(browser, elem, action_type, logger)


    # wait for the page to load
    time.sleep(randint(2, 6))

    story_elem = browser.find_element_by_xpath(
        read_xpath(watch_story.__name__+"_for_{}".format(action_type), "explore_stories"))

    if not story_elem:
        logger.info("'{}' {} POSSIBLY does not exist", elem, action_type)
        raise NoSuchElementException
    else:
        # load stories/view stories
        click_element(browser, story_elem)

    # watch stories until there is no more stories available
    logger.info('Watching stories...')
    while True:
        try:
            browser.find_element_by_xpath(
                read_xpath(watch_story.__name__+"_for_{}".format(action_type), "wait_finish"))
            time.sleep(randint(2, 6))
        except NoSuchElementException:
            break


