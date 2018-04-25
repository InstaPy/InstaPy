"""Module only used for the login part of the script"""
from .time_util import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from .util import update_activity
import pickle


def bypass_suspicious_login(browser):
    """Bypass suspicious loggin attempt verification. This should be only enabled
    when there isn't available cookie for the username, otherwise it will and
    shows "Unable to locate email or phone button" message, folollowed by
    CRITICAL - Wrong login data!"""
    # close sign up Instagram modal if available
    try:
        close_button = browser.find_element_by_xpath("[text()='Close']")
        ActionChains(
            browser).move_to_element(close_button).click().perform()
    except NoSuchElementException:
        pass

    try:
        # click on "This was me" button if challenge page was called
        this_was_me_button = browser.find_element_by_xpath(
            "//button[@name='choice'][text()='This Was Me']")
        ActionChains(
            browser).move_to_element(this_was_me_button).click().perform()
    except NoSuchElementException:
        # no verification needed
        pass

    try:
        user_email = browser.find_element_by_xpath(
            "//label[@for='choice_1']").text
    except NoSuchElementException:
        try:
            user_email = browser.find_element_by_xpath(
                "//label[@class='_q0nt5']").text
        except:
            try:
                user_email = browser.find_element_by_xpath(
                    "//label[@class='_q0nt5 _a7z3k']").text
            except:
                print("Unable to locate email or phone button, maybe "
                      "bypass_suspicious_login=True isn't needed anymore.")
                return False

    send_security_code_button = browser.find_element_by_xpath(
        ("//button[text()='Send Security Code']"))
    (ActionChains(browser)
     .move_to_element(send_security_code_button)
     .click()
     .perform())

    print('Instagram detected an unusual login attempt')
    print('A security code wast sent to your {}'.format(user_email))
    security_code = input('Type the security code here: ')

    security_code_field = browser.find_element_by_xpath((
        "//input[@id='security_code']"))
    (ActionChains(browser)
     .move_to_element(security_code_field)
     .click().send_keys(security_code).perform())

    submit_security_code_button = browser.find_element_by_xpath((
        "//button[text()='Submit']"))

    (ActionChains(browser)
     .move_to_element(submit_security_code_button)
     .click().perform())

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
               logfolder,
               switch_language=True,
               bypass_suspicious_attempt=False):
    """Logins the user with the given username and password"""
    assert username, 'Username not provided'
    assert password, 'Password not provided'

    browser.get('https://www.instagram.com')
    # update server calls
    update_activity()
    cookie_loaded = False

    # try to load cookie from username
    try:
        browser.get('https://www.google.com')
        for cookie in pickle.load(open('{0}{1}_cookie.pkl'
                                       .format(logfolder,username), 'rb')):
            browser.add_cookie(cookie)
            cookie_loaded = True
    except (WebDriverException, OSError, IOError):
        print("Cookie file not found, creating cookie...")

    browser.get('https://www.instagram.com')

    # Cookie has been loaded, user should be logged in. Ensurue this is true
    login_elem = browser.find_elements_by_xpath(
        "//*[contains(text(), 'Log in')]")
    # Login text is not found, user logged in
    # If not, issue with cookie, create new cookie
    if len(login_elem) == 0:
        return True

    # If not, issue with cookie, create new cookie
    if cookie_loaded:
        print("Issue with cookie for user " + username
              + ". Creating new cookie...")

    # Changes instagram language to english, to ensure no errors ensue from
    # having the site on a different language
    # Might cause problems if the OS language is english
    if switch_language:
        browser.find_element_by_xpath(
          "//select[@class='_fsoey']/option[text()='English']").click()

    # Check if the first div is 'Create an Account' or 'Log In'
    login_elem = browser.find_element_by_xpath(
        "//article/div/div/p/a[text()='Log in']")
    if login_elem is not None:
        ActionChains(browser).move_to_element(login_elem).click().perform()

    # Enter username and password and logs the user in
    # Sometimes the element name isn't 'Username' and 'Password'
    # (valid for placeholder too)
    input_username = browser.find_elements_by_xpath(
        "//input[@name='username']")

    ActionChains(browser).move_to_element(input_username[0]). \
        click().send_keys(username).perform()
    sleep(1)
    input_password = browser.find_elements_by_xpath(
        "//input[@name='password']")
    if not isinstance(password, str):
        password = str(password)
    ActionChains(browser).move_to_element(input_password[0]). \
        click().send_keys(password).perform()

    login_button = browser.find_element_by_xpath(
        "//form/span/button[text()='Log in']")
    ActionChains(browser).move_to_element(login_button).click().perform()
    # update server calls
    update_activity()

    if bypass_suspicious_attempt is True:
        bypass_suspicious_login(browser)

    sleep(5)

    # Check if user is logged-in (If there's two 'nav' elements)
    nav = browser.find_elements_by_xpath('//nav')
    if len(nav) == 2:
        # create cookie for username
        pickle.dump(browser.get_cookies(),
                    open('{0}{1}_cookie.pkl'.format(logfolder,username), 'wb'))
        return True
    else:
        return False
