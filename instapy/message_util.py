"""Module which handles features like sending and receiving messages"""
# import InstaPy modules
from .util import click_element
from .xpath import read_xpath

# import exceptions
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.common.by import By


def message_users(browser, users: list[str], message: str, logger):
    found = 0
    # go to new message page
    browser.get("https://www.instagram.com/direct/new/")
    search_box = browser.switch_to.active_element
    # type usernames into search box, select first option if available
    for user in users:
        search_box.send_keys(user)
        try:
            user_button = browser.find_element(
                By.XPATH, read_xpath(message_users.__name__, "user_button")
            )
            click_element(browser, user_button)
            logger.info("{} found".format(user))
            found += 1
        except NoSuchElementException:
            logger.info("{} not found, skipping".format(user))
            search_box.clear()
    if found == 0:
        logger.info("No users found")
        return
    next_button = browser.find_element(
        By.XPATH, read_xpath(message_users.__name__, "next_button")
    )
    # proceed to message screen
    click_element(browser, next_button)
    # type and send message
    message_box = browser.find_element(
        By.XPATH, read_xpath(message_users.__name__, "message_box")
    )
    message_box.send_keys(message)
    send_button = browser.find_element(
        By.XPATH, read_xpath(message_users.__name__, "send_button")
    )
    logger.info("Messaged {} users".format(found))
    click_element(browser, send_button)
    return


def message_user(browser, user: str, message: str, logger):
    # go to new message page
    browser.get("https://www.instagram.com/direct/new/")
    search_box = browser.switch_to.active_element
    # type usernames into search box, select first option if available
    search_box.send_keys(user)
    try:
        user_button = browser.find_element(
            By.XPATH, read_xpath(message_users.__name__, "user_button")
        )
        click_element(browser, user_button)
    except NoSuchElementException:
        logger.info("{} not found".format(user))
        search_box.clear()
        return
    next_button = browser.find_element(
        By.XPATH, read_xpath(message_users.__name__, "next_button")
    )
    # proceed to message screen
    click_element(browser, next_button)
    # type and send message
    message_box = browser.find_element(
        By.XPATH, read_xpath(message_users.__name__, "message_box")
    )
    message_box.send_keys(message)
    send_button = browser.find_element(
        By.XPATH, read_xpath(message_users.__name__, "send_button")
    )
    click_element(browser, send_button)
    logger.info("Messaged {}".format(user))
    return
