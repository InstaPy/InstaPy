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

from .xpath import read_xpath

def bypass_suspicious_login(browser, bypass_with_mobile):
    """Bypass suspicious loggin attempt verification. This should be only
    enabled
    when there isn't available cookie for the username, otherwise it will and
    shows "Unable to locate email or phone button" message, folollowed by
    CRITICAL - Wrong login data!"""
    # close sign up Instagram modal if available
    try:
        close_button = browser.find_element_by_xpath(
            read_xpath(bypass_suspicious_login.__name__, "close_button")
        )

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
            read_xpath(bypass_suspicious_login.__name__, "this_was_me_button"))

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
            read_xpath(bypass_suspicious_login.__name__, "choice")).text

    except NoSuchElementException:
        try:
            choice = browser.find_element_by_xpath(
                read_xpath(bypass_suspicious_login.__name__, "choice_no_such_element")
            ).text

        except Exception:
            try:
                choice = browser.find_element_by_xpath(
                    read_xpath(bypass_suspicious_login.__name__, "choice_exception")
                ).text

            except Exception:
                print("Unable to locate email or phone button, maybe "
                      "bypass_suspicious_login=True isn't needed anymore.")
                return False

    if bypass_with_mobile:
        choice = browser.find_element_by_xpath(
            read_xpath(bypass_suspicious_login.__name__, "bypass_with_mobile_choice")
        ).text

        mobile_button = browser.find_element_by_xpath(
            read_xpath(bypass_suspicious_login.__name__, "bypass_with_mobile_button")
        )

        (ActionChains(browser)
         .move_to_element(mobile_button)
         .click()
         .perform())

        sleep(5)

    send_security_code_button = browser.find_element_by_xpath(
        read_xpath(bypass_suspicious_login.__name__, "send_security_code_button"))

    (ActionChains(browser)
     .move_to_element(send_security_code_button)
     .click()
     .perform())

    # update server calls
    update_activity()

    print('Instagram detected an unusual login attempt')
    print('A security code was sent to your {}'.format(choice))
    security_code = input('Type the security code here: ')

    security_code_field = browser.find_element_by_xpath(
        read_xpath(bypass_suspicious_login.__name__, "security_code_field")
    )

    (ActionChains(browser)
     .move_to_element(security_code_field)
     .click()
     .send_keys(security_code)
     .perform())

    # update server calls for both 'click' and 'send_keys' actions
    for i in range(2):
        update_activity()

    submit_security_code_button = browser.find_element_by_xpath(
        read_xpath(bypass_suspicious_login.__name__, "submit_security_code_button")
    )

    (ActionChains(browser)
     .move_to_element(submit_security_code_button)
     .click()
     .perform())

    # update server calls
    update_activity()

    try:
        sleep(5)
        # locate wrong security code message
        wrong_login = browser.find_element_by_xpath(
            read_xpath(bypass_suspicious_login.__name__, "wrong_login")
        )

        if wrong_login is not None:
            print('Wrong security code! Please check the code Instagram'
                   'sent you and try again.')

    except NoSuchElementException:
        # correct security code
        pass


def login_user(browser,
               username,
               password,
               logger,
               logfolder,
               bypass_with_mobile=False):
    """Logins the user with the given username and password"""
    assert username, 'Username not provided'
    assert password, 'Password not provided'

    # check connection status
    try:
        logger.info('-- Connection Checklist [1/2] (Internet Connection Status)')
        browser.get("https://www.google.com")
        logger.info('- Internet Connection Status: ok')
    except Exception:
        logger.warn('- Internet Connection Status: error')
        return False

    # check Instagram.com status
    try:
        logger.info('-- Connection Checklist [2/2] (Instagram Server Status)')
        browser.get("https://isitdownorjust.me/instagram-com/")

        # collect isitdownorjust.me website information
        website_status = browser.find_element_by_xpath(
            read_xpath(login_user.__name__, "website_status"))
        response_time = browser.find_element_by_xpath(
            read_xpath(login_user.__name__, "response_time"))
        response_code = browser.find_element_by_xpath(
            read_xpath(login_user.__name__, "response_code"))

        logger.info('- Instagram WebSite Status: {} '.format(website_status.text))
        logger.info('- Instagram Response Time: {} '.format(response_time.text))
        logger.info('- Instagram Reponse Code: {}'.format(response_code.text))
        logger.info('- Instagram Server Status: ok')
    except Exception:
        logger.warn('- Instagram Server Status: error')
        return False

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
            read_xpath(login_user.__name__, "login_elem"))
    except NoSuchElementException:
        print("Login A/B test detected! Trying another string...")
        try:
            login_elem = browser.find_element_by_xpath(
                read_xpath(login_user.__name__, "login_elem_no_such_exception")
            )
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
    input_username_XP = read_xpath(login_user.__name__,"input_username_XP")
    explicit_wait(browser, "VOEL", [input_username_XP, "XPath"], logger)

    input_username = browser.find_element_by_xpath(input_username_XP)

    (ActionChains(browser)
     .move_to_element(input_username)
     .click()
     .send_keys(username)
     .perform())

    # update server calls for both 'click' and 'send_keys' actions
    for _ in range(2):
        update_activity()

    sleep(1)

    #  password
    input_password = browser.find_elements_by_xpath(
        read_xpath(login_user.__name__,"input_password"))

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

    # check for login error messages and display it in the logs
    if ('instagram.com/challenge' in browser.current_url):
        # check if account is disabled by Instagram,
        # or there is an active challenge to solve
        try:
            account_disabled = browser.find_element_by_xpath(
                read_xpath(login_user.__name__, "account_disabled"))
            logger.warn(account_disabled.text)
            return False
        except NoSuchElementException:
            pass

        # in case the user doesnt have a phone number linked to the Instagram account
        try:
            browser.find_element_by_xpath(
                read_xpath(login_user.__name__, "add_phone_number"))
            logger.warn(
                "Instagram initiated a challenge before allow your account to login. "
                "At the moment there isn't a phone number linked to your Instagram "
                "account. Please, add a phone number to your account, and try again.")
            return False
        except NoSuchElementException:
            pass

        # try to initiate security code challenge
        try:
            browser.find_element_by_xpath(
                read_xpath(login_user.__name__, "suspicious_login_attempt"))
            bypass_suspicious_login(browser, bypass_with_mobile)
        except NoSuchElementException:
            pass

    # check for wrong username or password message, and show it to the user
    try:
        error_alert = browser.find_element_by_xpath(
            read_xpath(login_user.__name__, "error_alert"))
        logger.warn(error_alert.text)
        return False
    except NoSuchElementException:
        pass

    # wait until page fully load
    explicit_wait(browser, "PFL", [], logger, 5)

    # Check if user is logged-in (If there's two 'nav' elements)
    nav = browser.find_elements_by_xpath(read_xpath(login_user.__name__,"nav"))
    if len(nav) == 2:
        # create cookie for username
        pickle.dump(browser.get_cookies(), open(
            '{0}{1}_cookie.pkl'.format(logfolder, username), 'wb'))
        return True
    else:
        return False


def dismiss_get_app_offer(browser, logger):
    """ Dismiss 'Get the Instagram App' page after a fresh login """
    offer_elem = read_xpath(dismiss_get_app_offer.__name__,"offer_elem")
    dismiss_elem = read_xpath(dismiss_get_app_offer.__name__,"dismiss_elem")

    # wait a bit and see if the 'Get App' offer rises up
    offer_loaded = explicit_wait(
        browser, "VOEL", [offer_elem, "XPath"], logger, 5, False)

    if offer_loaded:
        dismiss_elem = browser.find_element_by_xpath(dismiss_elem)
        click_element(browser, dismiss_elem)


def dismiss_notification_offer(browser, logger):
    """ Dismiss 'Turn on Notifications' offer on session start """
    offer_elem_loc = read_xpath(dismiss_notification_offer.__name__,"offer_elem_loc")
    dismiss_elem_loc = read_xpath(dismiss_notification_offer.__name__,"dismiss_elem_loc")

    # wait a bit and see if the 'Turn on Notifications' offer rises up
    offer_loaded = explicit_wait(
        browser, "VOEL", [offer_elem_loc, "XPath"], logger, 4, False)

    if offer_loaded:
        dismiss_elem = browser.find_element_by_xpath(dismiss_elem_loc)
        click_element(browser, dismiss_elem)
