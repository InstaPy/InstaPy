import time
from random import randint
from selenium.common.exceptions import NoSuchElementException
from .util import click_element
from .util import web_address_navigator
from .util import update_activity
from .xpath import read_xpath

import requests


def get_story_data(browser, elem: str, action_type: str, logger) -> dict:
    """not used fort the moment, more coding needed to understand this"""

    # if things change in the future, modify here:
    query_hash = "cda12de4f7fd3719c0569ce03589f4c4"

    if action_type == "tag":
        # pretty easy here, we just have to fill tag_names with the tag we want
        graphql_query_url = "https://www.instagram.com/graphql/query/?query_hash" + \
                            "={}".format(query_hash) + \
                            "&variables={{\"reel_ids\":[],\"tag_names\":[\"{}\"],\"location_ids\":[],".format(elem) + \
                            "\"highlight_reel_ids\":[],\"precomposed_overlay\":false,\"show_story_viewer_list\":true," + \
                            "\"story_viewer_fetch_count\":50,\"story_viewer_cursor\":\"\"," + \
                            "\"stories_video_dash_manifest\":false}"
    else:
        # if we are on a user page, we need to find out it's profile id and fill it into reel_ids
        elem_id = browser.execute_script(
            "return window._sharedData.entry_data."
            "ProfilePage[0].graphql.user.id")
        graphql_query_url = "https://www.instagram.com/graphql/query/?query_hash" + \
                            "={}".format(query_hash) + \
                            "&variables={{\"reel_ids\":[\"{}\"],\"tag_names\":[],\"location_ids\":[],".format(elem_id) + \
                            "\"highlight_reel_ids\":[],\"precomposed_overlay\":false,\"show_story_viewer_list\":true," + \
                            "\"story_viewer_fetch_count\":50,\"story_viewer_cursor\":\"\"," + \
                            "\"stories_video_dash_manifest\":false}"
    cookies = browser.get_cookies()

    s = requests.Session()

    for cookie in cookies:
        required_args = {
            'name': cookie['name'],
            'value': cookie['value']
        }
        if (cookie['name'] == "urlgen") or (cookie['name'] == "rur"):
            optional_args = {
                'domain': cookie['domain'],
                'secure': cookie['secure'],
                'rest': {'HttpOnly': cookie['httpOnly']},
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

    data = s.get(graphql_query_url)
    response = data.json()
    print(response)
    update_activity()

    reels_cnt = 0
    if response['status'] == 'ok':
        # we got a correct response from the server
        # check how many reels we got
        reels_cnt = len(response['data']['reels_media'])

        if reels_cnt == 0:
            # then nothing to watch, we received no stories
            return {'status': 'ok', 'reels_cnt': 0}
        else:
            # we got content
            # check if there is something new to watch otherwise we just return 0
            if response['data']['reels_media'][0]['seen'] is None:
                # nothing has been seen so reel_cnt = len(response['data']['reels_media'])
                reel_cnt = len(response['data']['reels_media'])
            elif response['data']['reels_media'][0]['seen'] < response['data']['reels_media'][0]['latest_reel_media']:
                for item in response['data']['reels_media'][0]['items']:
                    if item['taken_at_timestamp'] > response['data']['reels_media'][0]['seen']:
                        # this is new and we haven't seen it
                        reels_cnt += 1

            return {'status': 'ok', 'reels_cnt': reels_cnt}
    else:
        return {'status': 'not_ok', 'reels_cnt': 0}

    # we have the json describing the stories
    # output the amount of segments, total time, check if there is anything new
    # in case of tags, the users
    #


def watch_story(browser, elem: str, logger, action_type: str):
    """
        Load Stories, and watch it until there is no more stores
        to watch for the related element
    """

    if action_type == "tag":
        story_link = "https://www.instagram.com/explore/tags/{}".format(elem)

    else:
        story_link = "https://www.instagram.com/{}".format(elem)

    web_address_navigator(browser, story_link)
    # wait for the page to load
    time.sleep(randint(2, 6))
    # order is important here otherwise we are not on the page of the story we want to watch
    story_data = get_story_data(browser, elem, action_type, logger)

    if story_data['status'] == 'not ok':
        raise NoSuchElementException

    if story_data['reels_cnt'] == 0:
        # nothing to watch, there is no stories
        return 0

    story_elem = browser.find_element_by_xpath(
        read_xpath(watch_story.__name__ + "_for_{}".format(action_type), "explore_stories"))

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
                read_xpath(watch_story.__name__ + "_for_{}".format(action_type), "wait_finish"))
            time.sleep(randint(2, 6))
        except NoSuchElementException:
            break

    if story_data['reels_cnt'] == 0:
        logger.info('no stories to watch (either there is none) or we have already watched everything')

    logger.info('watched {} reels from {}: {}'.format(story_data['reels_cnt'], action_type, elem.encode('utf-8')))


