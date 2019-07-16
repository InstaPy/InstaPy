import time
from random import randint
from selenium.common.exceptions import NoSuchElementException
from .util import click_element
from .util import web_address_navigator
from .xpath import read_xpath


def watch_story(browser, elem, logger, action_type):
    """
        Load Tag Stories, and watch it until there is no more stores
        to watch for the related element
    """

    if action_type is "tag":
        story_link = "https://www.instagram.com/explore/tags/{}".format(elem)
    else:
        story_link = "https://www.instagram.com/{}".format(elem)

    web_address_navigator(browser, story_link)

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


