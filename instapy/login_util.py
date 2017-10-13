"""Module only used for the login part of the script"""
from .time_util import sleep
from selenium.webdriver.common.action_chains import ActionChains


def login_user(browser, username, password, switch_language=True):
    """Logins the user with the given username and password"""
    browser.get('https://www.instagram.com')

    # Changes instagram language to english, to ensure no errors ensue from
    # having the site on a different language
    # Might cause problems if the OS language is english
    if switch_language:
        browser.find_element_by_xpath(
            "//footer[@class='_s5vm9']/div[@class='_g7lf5 _9z659']/nav["
            "@class='_luodr']/ul[@class='_g8wl6']/li[@class='_538w0'][10]/"
            "span[@class='_pqycz _hqmnd']/select[@class='_fsoey']/option"
            "[text()='English']").click()

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
    ActionChains(browser).move_to_element(input_password[0]). \
        click().send_keys(password).perform()

    login_button = browser.find_element_by_xpath(
        "//form/span/button[text()='Log in']")
    ActionChains(browser).move_to_element(login_button).click().perform()

    sleep(5)

    # Check if user is logged-in (If there's two 'nav' elements)
    nav = browser.find_elements_by_xpath('//nav')
    if len(nav) == 2:
        return True
    else:
        return False
