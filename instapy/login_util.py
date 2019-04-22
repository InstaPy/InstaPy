"""Module only used for the login part of the script"""
# import built-in & third-party modules
import pickle
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# import InstaPy modules
from .time_util import sleep
from .util import update_activity
from .util import web_address_navigator
from .util import explicit_wait
from .util import click_element
from .util import check_authorization
from .util import reload_webpage

# import exceptions
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import MoveTargetOutOfBoundsException


def bypass_suspicious_login(browser, bypass_with_mobile):
    """Bypass suspicious loggin attempt verification. This should be only
    enabled
    when there isn't available cookie for the username, otherwise it will and
    shows "Unable to locate email or phone button" message, folollowed by
    CRITICAL - Wrong login data!"""
    # close sign up Instagram modal if available
    try:
        close_button = browser.find_element_by_xpath("[text()='Close']")

        (ActionChains(browser)
         .move_to_element(close_button)
         .click()
         .perform())

        # update server calls
        update_activity()

    except NoSuchElementException:
        pass

    try:
        # click on "This was me" button if challenge page was called
        this_was_me_button = browser.find_element_by_xpath(
            "//button[@name='choice'][text()='This Was Me']")

        (ActionChains(browser)
         .move_to_element(this_was_me_button)
         .click()
         .perform())

        # update server calls
        update_activity()

    except NoSuchElementException:
        # no verification needed
        pass

    try:
        choice = browser.find_element_by_xpath(
            "//label[@for='choice_1']").text

    except NoSuchElementException:
        try:
            choice = browser.find_element_by_xpath(
                "//label[@class='_q0nt5']").text

        except Exception:
            try:
                choice = browser.find_element_by_xpath(
                    "//label[@class='_q0nt5 _a7z3k']").text

            except Exception:
                print("Unable to locate email or phone button, maybe "
                      "bypass_suspicious_login=True isn't needed anymore.")
                return False

    if bypass_with_mobile:
        choice = browser.find_element_by_xpath(
            "//label[@for='choice_0']").text

        mobile_button = browser.find_element_by_xpath(
            "//label[@for='choice_0']")

        (ActionChains(browser)
         .move_to_element(mobile_button)
         .click()
         .perform())

        sleep(5)

    send_security_code_button = browser.find_element_by_xpath(
        "//button[text()='Send Security Code']")

    (ActionChains(browser)
     .move_to_element(send_security_code_button)
     .click()
     .perform())

    # update server calls
    update_activity()

    print('Instagram detected an unusual login attempt')
    print('A security code was sent to your {}'.format(choice))
    security_code = input('Type the security code here: ')

    security_code_field = browser.find_element_by_xpath((
        "//input[@id='security_code']"))

    (ActionChains(browser)
     .move_to_element(security_code_field)
     .click()
     .send_keys(security_code)
     .perform())

    # update server calls for both 'click' and 'send_keys' actions
    for i in range(2):
        update_activity()

    submit_security_code_button = browser.find_element_by_xpath(
        "//button[text()='Submit']")

    (ActionChains(browser)
     .move_to_element(submit_security_code_button)
     .click()
     .perform())

    # update server calls
    update_activity()

    try:
        sleep(5)
        # locate wrong security code message
        wrong_login = browser.find_element_by_xpath((
            "//p[text()='Please check the code we sent you and try "
            "again.']"))

        if wrong_login is not None:
            print(('Wrong security code! Please check the code Instagram'
                   'sent you and try again.'))

    except NoSuchElementException:
        # correct security code
        pass


def login_user(browser,
               username,
               password,
               logger,
               logfolder,
               bypass_suspicious_attempt=False,
               bypass_with_mobile=False):
    """Logins the user with the given username and password"""
    assert username, 'Username not provided'
    assert password, 'Password not provided'

    ig_homepage = "https://www.instagram.com"
    web_address_navigator(browser, ig_homepage)
    cookie_loaded = False

    # try to load cookie from username
    try:
        for cookie in pickle.load(open('{0}{1}_cookie.pkl'
                                       .format(logfolder, username), 'rb')):
            browser.add_cookie(cookie)
            cookie_loaded = True
    except (WebDriverException, OSError, IOError):
        print("Cookie file not found, creating cookie...")

    # force refresh after cookie load or check_authorization() will FAIL
    reload_webpage(browser)

    # cookie has been LOADED, so the user SHOULD be logged in
    # check if the user IS logged in
    login_state = check_authorization(browser,
                                      username,
                                      "activity counts",
                                      logger,
                                      False)
    if login_state is True:
        dismiss_notification_offer(browser, logger)
        return True

    # if user is still not logged in, then there is an issue with the cookie
    # so go create a new cookie..
    if cookie_loaded:
        print("Issue with cookie for user {}. Creating "
              "new cookie...".format(username))

    # Check if the first div is 'Create an Account' or 'Log In'
    try:
        login_elem = browser.find_element_by_xpath(
            "//a[text()='Log in']")
    except NoSuchElementException:
        print("Login A/B test detected! Trying another string...")
        try:
            login_elem = browser.find_element_by_xpath(
                "//a[text()='Log In']")
        except NoSuchElementException:
            return False

    if login_elem is not None:
        try:
            (ActionChains(browser)
             .move_to_element(login_elem)
             .click()
             .perform())
        except MoveTargetOutOfBoundsException:
            login_elem.click()

        # update server calls
        update_activity()

    # Enter username and password and logs the user in
    # Sometimes the element name isn't 'Username' and 'Password'
    # (valid for placeholder too)

    # wait until it navigates to the login page
    login_page_title = "Login"
    explicit_wait(browser, "TC", login_page_title, logger)

    # wait until the 'username' input element is located and visible
    input_username_XP = "//input[@name='username']"
    explicit_wait(browser, "VOEL", [input_username_XP, "XPath"], logger)

    input_username = browser.find_element_by_xpath(input_username_XP)

    (ActionChains(browser)
     .move_to_element(input_username)
     .click()
     .send_keys(username)
     .perform())

    # update server calls for both 'click' and 'send_keys' actions
    for i in range(2):
        update_activity()

    sleep(1)

    #  password
    input_password = browser.find_elements_by_xpath(
        "//input[@name='password']")

    if not isinstance(password, str):
        password = str(password)

    (ActionChains(browser)
     .move_to_element(input_password[0])
     .click()
     .send_keys(password)
     .perform())

    sleep(1)

    (ActionChains(browser)
     .move_to_element(input_password[0])
     .click()
     .send_keys(Keys.ENTER)
     .perform())

    # update server calls for both 'click' and 'send_keys' actions
    for i in range(4):
        update_activity()

    dismiss_get_app_offer(browser, logger)
    dismiss_notification_offer(browser, logger)

    if bypass_suspicious_attempt is True:
        bypass_suspicious_login(browser, bypass_with_mobile)

    # wait until page fully load
    explicit_wait(browser, "PFL", [], logger, 5)

    # Check if user is logged-in (If there's two 'nav' elements)
    nav = browser.find_elements_by_xpath('//nav')
    if len(nav) == 2:
        # create cookie for username
        pickle.dump(browser.get_cookies(), open(
            '{0}{1}_cookie.pkl'.format(logfolder, username), 'wb'))
        return True
    else:
        return False


def dismiss_get_app_offer(browser, logger):
    """ Dismiss 'Get the Instagram App' page after a fresh login """
    offer_elem = "//*[contains(text(), 'Get App')]"
    dismiss_elem = "//*[contains(text(), 'Not Now')]"

    # wait a bit and see if the 'Get App' offer rises up
    offer_loaded = explicit_wait(
        browser, "VOEL", [offer_elem, "XPath"], logger, 5, False)

    if offer_loaded:
        dismiss_elem = browser.find_element_by_xpath(dismiss_elem)
        click_element(browser, dismiss_elem)


def dismiss_notification_offer(browser, logger):
    """ Dismiss 'Turn on Notifications' offer on session start """
    offer_elem_loc = "//div/h2[text()='Turn on Notifications']"
    dismiss_elem_loc = "//button[text()='Not Now']"

    # wait a bit and see if the 'Turn on Notifications' offer rises up
    offer_loaded = explicit_wait(
        browser, "VOEL", [offer_elem_loc, "XPath"], logger, 4, False)

    if offer_loaded:
        dismiss_elem = browser.find_element_by_xpath(dismiss_elem_loc)
        click_element(browser, dismiss_elem)
