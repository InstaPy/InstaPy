""" Module which handles the follow features """
# import InstaPy modules
from .util import web_address_navigator
from .util import get_username_from_id
from .util import is_page_available
from .util import update_activity
from .util import explicit_wait
from .util import load_user_id
from .xpath import read_xpath

# import exceptions
from selenium.common.exceptions import NoSuchElementException


def get_following_status(
    browser, track, username, person, person_id, logger, logfolder
):
    """ Verify if you are following the user in the loaded page """
    if person == username:
        return "OWNER", None

    if track == "profile":
        ig_homepage = "https://www.instagram.com/"
        web_address_navigator(browser, ig_homepage + person)

    follow_button_XP = read_xpath(get_following_status.__name__, "follow_button_XP")
    failure_msg = "--> Unable to detect the following status of '{}'!"
    user_inaccessible_msg = (
        "Couldn't access the profile page of '{}'!\t~might have changed the"
        " username".format(person)
    )

    # check if the page is available
    valid_page = is_page_available(browser, logger)
    if not valid_page:
        logger.warning(user_inaccessible_msg)
        person_new = verify_username_by_id(
            browser, username, person, None, logger, logfolder
        )
        if person_new:
            ig_homepage = "https://www.instagram.com/"
            web_address_navigator(browser, ig_homepage + person_new)
            valid_page = is_page_available(browser, logger)
            if not valid_page:
                logger.error(failure_msg.format(person_new.encode("utf-8")))
                return "UNAVAILABLE", None
        else:
            logger.error(failure_msg.format(person.encode("utf-8")))
            return "UNAVAILABLE", None

    # wait until the follow button is located and visible, then get it
    try:
        browser.find_element_by_xpath(
            read_xpath(get_following_status.__name__, "follow_button_XP")
        )
        follow_button_XP = read_xpath(get_following_status.__name__, "follow_button_XP")
    except NoSuchElementException:
        try:
            follow_button = browser.find_element_by_xpath(
                read_xpath(get_following_status.__name__, "follow_span_XP_following")
            )
            return "Following", follow_button
        except:
            return "UNAVAILABLE", None
    follow_button = explicit_wait(
        browser, "VOEL", [follow_button_XP, "XPath"], logger, 7, False
    )

    if not follow_button:
        browser.execute_script("location.reload()")
        update_activity(browser, state=None)

        follow_button = explicit_wait(
            browser, "VOEL", [follow_button_XP, "XPath"], logger, 14, False
        )
        if not follow_button:
            # cannot find the any of the expected buttons
            logger.error(failure_msg.format(person.encode("utf-8")))
            return None, None

    # get follow status
    following_status = follow_button.text

    return following_status, follow_button


def verify_username_by_id(browser, username, person, person_id, logger, logfolder):
    """Check if the given user has changed username after the time of
    followed"""

    # try to find the user by ID
    person_id = load_user_id(username, person, logger, logfolder)

    # if person_id is None, inform the InstaPy user that record does not exist
    if person_id not in [None, "unknown", "undefined"]:
        # get the [new] username of the user from the stored user ID
        person_new = get_username_from_id(browser, person_id, logger)

        # if person_new is None, inform the InstaPy user that record does not exist
        if person_new is not None and person_new != person:
            logger.info(
                "User '{}' has changed username and now is called '{}' :S".format(
                    person, person_new
                )
            )
            return person_new

    # check who call this def, since will receive a None value
    logger.info("User '{}' doesn't exist in local records".format(person))
    return None
