"""Module only used for the login part of the script"""
# import built-in & third-party modules
import json
import os
import pickle
import random
import socket

# import exceptions
from selenium.common.exceptions import (
    MoveTargetOutOfBoundsException,
    NoSuchElementException,
    WebDriverException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# import InstaPy modules
from .time_util import sleep
from .util import (
    check_authorization,
    click_element,
    explicit_wait,
    reload_webpage,
    update_activity,
    web_address_navigator,
)
from .xpath import read_xpath


def find_element_with_fallback(browser, logger, primary_xpaths, fallback_xpaths=None):
    """
    Find element with fallback support for multiple XPaths (v2024 first, then legacy)
    
    Args:
        browser: Selenium browser instance
        logger: Logger instance
        primary_xpaths: List of v2024 XPaths to try first
        fallback_xpaths: List of legacy XPaths to try if primary fails
        
    Returns:
        WebElement if found, None otherwise
    """
    xpaths_to_try = []
    
    # Add primary XPaths first (v2024)
    if isinstance(primary_xpaths, list):
        xpaths_to_try.extend(primary_xpaths)
    else:
        xpaths_to_try.append(primary_xpaths)
    
    # Add fallback XPaths (legacy)
    if fallback_xpaths:
        if isinstance(fallback_xpaths, list):
            xpaths_to_try.extend(fallback_xpaths)
        else:
            xpaths_to_try.append(fallback_xpaths)
    
    for i, xpath in enumerate(xpaths_to_try):
        try:
            element = browser.find_element(By.XPATH, xpath)
            if element:
                if i == 0:
                    logger.debug("- Using v2024 XPath selector")
                elif i < len(primary_xpaths if isinstance(primary_xpaths, list) else [primary_xpaths]):
                    logger.debug("- Using alternative v2024 XPath selector")
                else:
                    logger.debug("- Using legacy XPath selector (fallback)")
                return element
        except NoSuchElementException:
            continue
    
    return None


def bypass_suspicious_login(
    browser, logger, logfolder, bypass_security_challenge_using
):
    """Bypass suspicious loggin attempt verification."""

    # close sign up Instagram modal if available
    dismiss_get_app_offer(browser, logger)
    dismiss_notification_offer(browser, logger)
    dismiss_this_was_me(browser)

    option = None
    if bypass_security_challenge_using == "sms":
        try:
            option = browser.find_element(
                By.XPATH,
                read_xpath(bypass_suspicious_login.__name__, "bypass_with_sms_option"),
            )
        except NoSuchElementException:
            logger.warning(
                "Unable to choose ({}) option to bypass the challenge".format(
                    bypass_security_challenge_using.upper()
                )
            )

    if bypass_security_challenge_using == "email":
        try:
            option = browser.find_element(
                By.XPATH,
                read_xpath(
                    bypass_suspicious_login.__name__, "bypass_with_email_option"
                ),
            )
        except NoSuchElementException:
            logger.warning(
                "Unable to choose ({}) option to bypass the challenge".format(
                    bypass_security_challenge_using.upper()
                )
            )

    # click on your option
    (ActionChains(browser).move_to_element(option).click().perform())
    # next button click will miss the DOM reference for this element, so ->
    option_text = option.text

    # click on security code
    send_security_code_button = browser.find_element(
        By.XPATH,
        read_xpath(bypass_suspicious_login.__name__, "send_security_code_button"),
    )
    (ActionChains(browser).move_to_element(send_security_code_button).click().perform())

    # update server calls
    update_activity(browser, state=None)

    logger.info("Instagram detected an unusual login attempt")
    logger.info('Check Instagram App for "Suspicious Login attempt" prompt')
    logger.info("A security code was sent to your {}".format(option_text))

    security_code = None
    try:
        path = "{}state.json".format(logfolder)
        data = {}
        # check if file exists and has content
        if os.path.isfile(path) and os.path.getsize(path) > 0:
            # load JSON file
            with open(path, "r") as json_file:
                data = json.load(json_file)

        # update connection state
        security_code = data["challenge"]["security_code"]
    except Exception:
        logger.info("Security Code not present in {}state.json file".format(logfolder))

    if security_code is None:
        security_code = input("Type the security code here: ")

    security_code_field = browser.find_element(
        By.XPATH, read_xpath(bypass_suspicious_login.__name__, "security_code_field")
    )

    (
        ActionChains(browser)
        .move_to_element(security_code_field)
        .click()
        .send_keys(security_code)
        .perform()
    )

    # update server calls for both 'click' and 'send_keys' actions
    for _ in range(2):
        update_activity(browser, state=None)

    submit_security_code_button = browser.find_element(
        By.XPATH,
        read_xpath(bypass_suspicious_login.__name__, "submit_security_code_button"),
    )

    (
        ActionChains(browser)
        .move_to_element(submit_security_code_button)
        .click()
        .perform()
    )

    # update server calls
    update_activity(browser, state=None)

    try:
        sleep(3)
        # locate wrong security code message
        wrong_login = browser.find_element(
            By.XPATH, read_xpath(bypass_suspicious_login.__name__, "wrong_login")
        )

        if wrong_login is not None:
            wrong_login_msg = "Wrong security code! Please check the code Instagram sent you and try again."
            update_activity(
                browser,
                action=None,
                state=wrong_login_msg,
                logfolder=logfolder,
                logger=logger,
            )
            logger.warning(wrong_login_msg)

    except NoSuchElementException:
        # correct security code
        pass


def check_browser(browser, logfolder, logger, proxy_address):
    # set initial state to offline
    update_activity(
        browser,
        action=None,
        state="trying to connect",
        logfolder=logfolder,
        logger=logger,
    )

    # check connection status
    try:
        logger.info("-- Connection Checklist [1/2] (Internet Connection Status)")
        browser.get("view-source:https://freegeoip.app/json")
        pre = browser.find_element(By.TAG_NAME, "pre").text
        current_ip_info = json.loads(pre)
        if (
            proxy_address is not None
            and socket.gethostbyname(proxy_address) != current_ip_info["ip"]
        ):
            logger.warning("- Proxy is set, but it's not working properly")
            logger.warning(
                '- Expected Proxy IP is "{}", and the current IP is "{}"'.format(
                    proxy_address, current_ip_info["ip"]
                )
            )
            logger.warning("- Try again or disable the Proxy Address on your setup")
            logger.warning("- Aborting connection...")
            return False
        else:
            logger.info("- Internet Connection Status: ok")
            logger.info(
                '- Current IP is "{}" and it\'s from "{}/{}"'.format(
                    current_ip_info["ip"],
                    current_ip_info["country_name"],
                    current_ip_info["country_code"],
                )
            )
            update_activity(
                browser,
                action=None,
                state="Internet connection is ok",
                logfolder=logfolder,
                logger=logger,
            )
    except Exception:
        logger.warning("- Internet Connection Status: error")
        update_activity(
            browser,
            action=None,
            state="There is an issue with the internet connection",
            logfolder=logfolder,
            logger=logger,
        )
        return False

    # check if hide-selenium extension is running
    logger.info("-- Connection Checklist [2/2] (Hide Selenium Extension)")
    webdriver = browser.execute_script("return window.navigator.webdriver")
    logger.info("- window.navigator.webdriver response: {}".format(webdriver))
    if webdriver:
        logger.warning("- Hide Selenium Extension: error")
    else:
        logger.info("- Hide Selenium Extension: ok")

    # everything is ok, then continue(True)
    return True


def login_user(
    browser,
    username,
    password,
    logger,
    logfolder,
    proxy_address,
    security_code_to_phone,
    security_codes,
    want_check_browser,
):
    """Logins the user with the given username and password"""
    assert username, "Username not provided"
    assert password, "Password not provided"

    # Hotfix - this check crashes more often than not -- plus in not necessary,
    # I can verify my own connection
    if want_check_browser:
        if not check_browser(browser, logfolder, logger, proxy_address):
            return False

    ig_homepage = "https://www.instagram.com"
    web_address_navigator(browser, ig_homepage)

    cookie_file = "{0}{1}_cookie.pkl".format(logfolder, username)
    cookie_loaded = None
    login_state = None

    # try to load cookie from username
    try:
        for cookie in pickle.load(open(cookie_file, "rb")):
            # SameSite = Strict, your cookie will only be sent in a
            # first-party context. In user terms, the cookie will only be sent
            # if the site for the cookie matches the site currently shown in
            # the browser's URL bar.
            if "sameSite" in cookie and cookie["sameSite"] == "None":
                cookie["sameSite"] = "Strict"

            browser.add_cookie(cookie)

        sleep(4)
        cookie_loaded = True
        logger.info("- Cookie file for user '{}' loaded...".format(username))

        # force refresh after cookie load or check_authorization() will FAIL
        reload_webpage(browser)
        sleep(4)

        # cookie has been LOADED, so the user SHOULD be logged in
        login_state = check_authorization(
            browser, username, "activity counts", logger, False
        )
        sleep(4)

    except (WebDriverException, OSError, IOError):
        # Just info the user, not an error
        logger.info("- Cookie file not found, creating cookie...")

    if login_state and cookie_loaded:
        # Cookie loaded and joined IG, dismiss following features if availables
        dismiss_notification_offer(browser, logger)
        dismiss_save_information(browser, logger)
        accept_igcookie_dialogue(browser, logger)
        return True

    # This fix comes from comment in #6060 If not necessary we can remove it
    accept_igcookie_dialogue(browser, logger)

    # if user is still not logged in, then there is an issue with the cookie
    # so go create a new cookie.
    if cookie_loaded:
        logger.warning(
            "- Issue with cookie for user '{}'. Creating new cookie...".format(username)
        )

        # Error could be faced due to "<button class="sqdOP L3NKy y3zKF"
        # type="button"> Cookie could not be loaded" or similar.
        # Session displayed we are in, but then a failure for the first
        # `login_elem` like the element is no longer attached to the DOM.
        # Saw this issue when session hasn't been used for a while; which means
        # "expiry" values in cookie are outdated.
        try:
            # Since having issues with the cookie a new one can be generated,
            # if cookie cannot be created or deleted stop execution.
            logger.info("- Deleting browser cookies...")
            browser.delete_all_cookies()
            browser.refresh()
            # Delete file from Filesystem if any issue with the cookie
            os.remove(cookie_file)
            sleep(random.randint(3, 5))

        except Exception as e:
            # NF: start
            if isinstance(e, WebDriverException):
                logger.exception(
                    "Error occurred while deleting cookies from web browser!\n\t{}".format(
                        str(e).encode("utf-8")
                    )
                )
            return False
            # NF: end

    web_address_navigator(browser, ig_homepage)

    # Check if the first div is 'Create an Account' or 'Log In'
    # v2024 first, then legacy fallbacks
    login_elem_xpaths_v2024 = [
        read_xpath(login_user.__name__, "login_elem_v2024"),
        read_xpath(login_user.__name__, "login_elem_v2024_2"),
    ]
    login_elem_xpaths_legacy = [
        read_xpath(login_user.__name__, "login_elem"),
        read_xpath(login_user.__name__, "login_elem_no_such_exception"),
        read_xpath(login_user.__name__, "login_elem_no_such_exception_2"),
    ]
    
    login_elem = find_element_with_fallback(
        browser, logger, login_elem_xpaths_v2024, login_elem_xpaths_legacy
    )
    
    if login_elem is None:
        logger.exception("Login button not found with any selector!")
        return False

    if login_elem is not None:
        try:
            (ActionChains(browser).move_to_element(login_elem).click().perform())
        except MoveTargetOutOfBoundsException:
            login_elem.click()

        # update server calls
        update_activity(browser, state=None)

    # Enter username and password and logs the user in
    # Sometimes the element name isn't 'Username' and 'Password'
    # (valid for placeholder too)

    # wait until it navigates to the login page
    # 10/2020 -> "WebDriver:GetTitle" - {"value":"Instagram"}
    login_page_title = "Instagram"
    explicit_wait(browser, "TC", login_page_title, logger)

    # Find username input with v2024 first priority
    input_username_xpaths_v2024 = [
        read_xpath(login_user.__name__, "input_username_v2024"),
    ]
    input_username_xpaths_legacy = [
        read_xpath(login_user.__name__, "input_username_XP"),
    ]
    
    input_username = find_element_with_fallback(
        browser, logger, input_username_xpaths_v2024, input_username_xpaths_legacy
    )
    
    if input_username is None:
        logger.exception("Username input field not found!")
        return False

    (
        ActionChains(browser)
        .move_to_element(input_username)
        .click()
        .send_keys(username)
        .perform()
    )

    # update server calls for both 'click' and 'send_keys' actions
    for _ in range(2):
        update_activity(browser, state=None)

    sleep(1)

    # Find password input with v2024 first priority
    input_password_xpaths_v2024 = [
        read_xpath(login_user.__name__, "input_password_v2024"),
    ]
    input_password_xpaths_legacy = [
        read_xpath(login_user.__name__, "input_password"),
    ]
    
    input_password = find_element_with_fallback(
        browser, logger, input_password_xpaths_v2024, input_password_xpaths_legacy
    )
    
    if input_password is None:
        logger.exception("Password input field not found!")
        return False

    if not isinstance(password, str):
        password = str(password)

    (
        ActionChains(browser)
        .move_to_element(input_password)
        .click()
        .send_keys(password)
        .perform()
    )

    sleep(1)

    (
        ActionChains(browser)
        .move_to_element(input_password)
        .click()
        .send_keys(Keys.ENTER)
        .perform()
    )

    # update server calls for both 'click' and 'send_keys' actions
    for _ in range(4):
        update_activity(browser, state=None)

    # Check if account is protected with Two Factor Authentication
    two_factor_authentication(browser, logger, security_codes)

    # After login attempt, press ENTER again if needed (v2024 fallback)
    # This handles cases where the first ENTER didn't trigger submission
    try:
        # Check if we're still on the login form (password field still exists)
        still_on_login = browser.find_element(By.XPATH, read_xpath(login_user.__name__, "input_password_v2024"))
        if still_on_login:
            logger.info("- Retrying login submission (v2024 compatibility)...")
            sleep(1)
            (
                ActionChains(browser)
                .send_keys(Keys.ENTER)
                .perform()
            )
            # update server calls
            update_activity(browser, state=None)
    except NoSuchElementException:
        # Login form submitted successfully, moving on
        pass

    # Dismiss following features if availables
    dismiss_get_app_offer(browser, logger)
    dismiss_notification_offer(browser, logger)
    dismiss_save_information(browser, logger)

    # IG: "Accept cookies from Instagram on this browser?"
    # They said that they're using cookies to help to personalize the content,
    # server relevant ads and provide safer experience.
    accept_igcookie_dialogue(browser, logger)

    # check for login error messages and display it in the logs
    if "instagram.com/challenge" in browser.current_url or "instagram.com/login" in browser.current_url:
        # check if account is disabled by Instagram (v2024 first, then legacy)
        account_disabled = find_element_with_fallback(
            browser, logger,
            [read_xpath(login_user.__name__, "account_disabled_v2024")],
            [read_xpath(login_user.__name__, "account_disabled")]
        )
        if account_disabled:
            logger.warning(account_disabled.text)
            update_activity(
                browser,
                action=None,
                state=account_disabled.text,
                logfolder=logfolder,
                logger=logger,
            )
            return False

        # in case the user doesnt have a phone number linked (v2024 first, then legacy)
        add_phone_number = find_element_with_fallback(
            browser, logger,
            [read_xpath(login_user.__name__, "add_phone_number_v2024")],
            [read_xpath(login_user.__name__, "add_phone_number")]
        )
        if add_phone_number:
            challenge_warn_msg = (
                "Instagram initiated a challenge before allow your account to login. "
                "At the moment there isn't a phone number linked to your Instagram "
                "account. Please, add a phone number to your account, and try again."
            )
            logger.warning(challenge_warn_msg)
            update_activity(
                browser,
                action=None,
                state=challenge_warn_msg,
                logfolder=logfolder,
                logger=logger,
            )
            return False

        # try to initiate security code challenge (v2024 first, then legacy)
        suspicious_login = find_element_with_fallback(
            browser, logger,
            [read_xpath(login_user.__name__, "suspicious_login_attempt_v2024")],
            [read_xpath(login_user.__name__, "suspicious_login_attempt")]
        )
        if suspicious_login:
            update_activity(
                browser,
                action=None,
                state="Trying to solve suspicious attempt login",
                logfolder=logfolder,
                logger=logger,
            )
            bypass_suspicious_login(browser, logger, logfolder, security_code_to_phone)

    # check for wrong username or password message (v2024 first, then legacy)
    error_alert = find_element_with_fallback(
        browser, logger,
        [read_xpath(login_user.__name__, "error_alert_v2024")],
        [read_xpath(login_user.__name__, "error_alert")]
    )
    if error_alert:
        logger.warning(error_alert.text)
        update_activity(
            browser,
            action=None,
            state=error_alert.text,
            logfolder=logfolder,
            logger=logger,
        )
        return False

    if "instagram.com/accounts/onetap" in browser.current_url:
        browser.get(ig_homepage)

    # wait until page fully load
    explicit_wait(browser, "PFL", [], logger, 5)

    # Check if user is logged-in (If there's nav elements, v2024 first, then legacy)
    nav = find_element_with_fallback(
        browser, logger,
        [read_xpath(login_user.__name__, "nav_v2024")],
        [read_xpath(login_user.__name__, "nav")]
    )
    
    if nav is not None:
        # create cookie for username and save it
        cookies_list = browser.get_cookies()

        for cookie in cookies_list:
            if "sameSite" in cookie and cookie["sameSite"] == "None":
                cookie["sameSite"] = "Strict"

        try:
            # Open the cookie file to store the data
            with open(cookie_file, "wb") as cookie_f_handler:
                pickle.dump(cookies_list, cookie_f_handler)

        except pickle.PicklingError:
            # Next time, cookie will be created for the session so we are safe
            logger.warning("- Browser cookie list could not be saved to your local...")

        finally:
            return True

    else:
        logger.warning("- Navigation element not found, login may have failed")
        return False


def dismiss_get_app_offer(browser, logger):
    """Dismiss 'Get the Instagram App' page after a fresh login"""
    offer_elem = read_xpath(dismiss_get_app_offer.__name__, "offer_elem")
    dismiss_elem = read_xpath(dismiss_get_app_offer.__name__, "dismiss_elem")

    # wait a bit and see if the 'Get App' offer rises up
    offer_loaded = explicit_wait(
        browser, "VOEL", [offer_elem, "XPath"], logger, 5, False
    )

    if offer_loaded:
        dismiss_elem = browser.find_element(By.XPATH, dismiss_elem)
        click_element(browser, dismiss_elem)


def dismiss_notification_offer(browser, logger):
    """Dismiss 'Turn on Notifications' offer on session start"""
    offer_elem_loc = read_xpath(dismiss_notification_offer.__name__, "offer_elem_loc")
    dismiss_elem_loc = read_xpath(
        dismiss_notification_offer.__name__, "dismiss_elem_loc"
    )

    # wait a bit and see if the 'Turn on Notifications' offer rises up
    offer_loaded = explicit_wait(
        browser, "VOEL", [offer_elem_loc, "XPath"], logger, 4, False
    )

    if offer_loaded:
        dismiss_elem = browser.find_element(By.XPATH, dismiss_elem_loc)
        click_element(browser, dismiss_elem)


def dismiss_save_information(browser, logger):
    """Dismiss 'Save Your Login Info?' offer on session start"""
    # This question occurs when pkl doesn't exist
    offer_elem_loc = read_xpath(dismiss_save_information.__name__, "offer_elem_loc")
    dismiss_elem_loc = read_xpath(dismiss_save_information.__name__, "dismiss_elem_loc")

    offer_loaded = explicit_wait(
        browser, "VOEL", [offer_elem_loc, "XPath"], logger, 4, False
    )

    if offer_loaded:
        # When prompted chose "Not Now", we don't know if saving information
        # contributes or stimulate IG to target the acct, it would be better to
        # just pretend that we are using IG in different browsers.
        logger.info("- Do not save Login Info by now...")
        dismiss_elem = browser.find_element(By.XPATH, dismiss_elem_loc)
        click_element(browser, dismiss_elem)


def dismiss_this_was_me(browser):
    try:
        # click on "This was me" button if challenge page was called
        this_was_me_button = browser.find_element(
            By.XPATH, read_xpath(dismiss_this_was_me.__name__, "this_was_me_button")
        )
        (ActionChains(browser).move_to_element(this_was_me_button).click().perform())
        # update server calls
        update_activity(browser, state=None)
    except NoSuchElementException:
        # no verification needed
        pass


def two_factor_authentication(browser, logger, security_codes):
    """
    Check if account is protected with Two Factor Authentication codes

    Args:
        :browser: Web driver
        :logger: Library to log actions
        :security_codes: List of Two Factor Authentication codes, also named as Recovery Codes.

    Returns: None
    """

    # Wait until page is loaded after user and password were introduced
    sleep(random.randint(3, 5))

    if "two_factor" in browser.current_url or "challenge" in browser.current_url:

        logger.info("- Two Factor Authentication is enabled...")

        # Chose one code from the security_codes list
        # 0000 is used if no codes were provided in constructor.
        code = random.choice(security_codes)

        try:
            # Check Security code is numeric
            int(code)

            # Find verification code input with v2024 first priority
            security_code = find_element_with_fallback(
                browser, logger,
                [read_xpath(login_user.__name__, "verification_code_v2024")],
                [read_xpath(login_user.__name__, "verification_code")]
            )
            
            if security_code is None:
                logger.warning("- Could not find verification code input field")
                return
                
            # Find confirm button with v2024 first priority
            confirm = find_element_with_fallback(
                browser, logger,
                [read_xpath(login_user.__name__, "confirm_v2024")],
                [read_xpath(login_user.__name__, "confirm")]
            )
            
            if confirm is None:
                logger.warning("- Could not find confirm button")
                return

            (
                ActionChains(browser)
                .move_to_element(security_code)
                .click()
                .send_keys(code)
                .perform()
            )

            sleep(random.randint(1, 3))

            (
                ActionChains(browser)
                .move_to_element(confirm)
                .click()
                .send_keys(Keys.ENTER)
                .perform()
            )

            # update server calls for both 'click' and 'send_keys' actions
            for _ in range(2):
                update_activity(browser, state=None)

            sleep(random.randint(1, 3))

        except NoSuchElementException as e:
            # Unable to login to Instagram!
            logger.warning(
                "- Security code could not be written!\n\t{}".format(
                    str(e).encode("utf-8")
                )
            )
        except ValueError:
            # Unable to login to Instagram!
            logger.warning("- Security code provided is not a number")
    else:
        # Two Factor Authentication is not enabled or the security code has
        # already been entered in previous session.
        # Return None and login to Instagram!
        return


def accept_igcookie_dialogue(browser, logger):
    """Presses 'Accept' button on IG cookie dialogue"""

    # Try with multiple selectors, v2024 first
    accept_button_selectors = [
        read_xpath(accept_igcookie_dialogue.__name__, "accept_button_v2024"),
        read_xpath(accept_igcookie_dialogue.__name__, "accept_button_v2024_2"),
        read_xpath(accept_igcookie_dialogue.__name__, "accept_button"),
    ]
    
    accept_elem = find_element_with_fallback(
        browser, logger, accept_button_selectors[:2], accept_button_selectors[2]
    )

    if accept_elem:
        logger.info("- Accepted IG cookies by default...")
        click_element(browser, accept_elem)
