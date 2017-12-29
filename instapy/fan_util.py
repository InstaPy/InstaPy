from .time_util import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from .like_util import get_links_for_username
from math import ceil
from random import randint

def fan_util(browser, account, logger):
    browser.get('https://www.instagram.com')

    try:

        sleep(randint(1,6))
        explore_button = browser.find_element_by_xpath('//a[@href="/explore/"]')
        ActionChains(browser).move_to_element(explore_button).click().perform()

        sleep(randint(1,6))
        input_field = browser.find_element_by_xpath('//input[@type="text"]')
        ActionChains(browser).move_to_element(input_field).click().send_keys(account).perform()

        sleep(randint(1,6))
        body_elem = browser.find_element_by_tag_name('body')

        user = browser.find_element_by_xpath('//span[text()="'+account+'"]')
        if user:
            # Click on user's account
            ActionChains(browser).move_to_element(user).click().perform()

            # check if the user is private
            try:
                is_private = body_elem.find_element_by_xpath(
                    '//h2[contains(text(),"This Account is Private")]')
            except:
                logger.info('Interaction begin...')
            else:
                if is_private:
                    logger.warning('This user is private...')
                    return False

            follow_account(browser,account)

            # Scroll to the bottom of the page
            try:
                # scroll down to load posts
                for i in range(randint(2,12)):
                    browser.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);")
                    sleep(randint(1,3))
            except:
                logger.warning(
                    'Load button not found, working with current images!')

            # Get all user's Images
            images = get_all_images_on_user_page(browser)

            # Like all user's Images
            for image in images:
                sleep(randint(1, 5))
                ActionChains(browser).move_to_element(image).click().perform()
                like_image(browser, logger)
                try:
                    close_button = browser.find_element_by_xpath('//button[contains(text(),"Close")]')
                    ActionChains(browser).move_to_element(close_button).click().perform()
                except:
                    ActionChains(browser).move_by_offset(0,0).click().perform()
    except:
        return False

    return True

def get_all_images_on_user_page(browser):
    # Getting the images
    try:
        divs = browser.find_elements_by_xpath('//section/main/article/div')
        images = divs[len(divs)-1]
        return images.find_elements_by_tag_name('a')

    except:
        print("The user has no images")
    return []

def like_image(browser, logger):
    """Likes the browser opened image"""
    like_elem = browser.find_elements_by_xpath(
        "//a[@role='button']/span[text()='Like']/..")
    liked_elem = browser.find_elements_by_xpath(
        "//a[@role='button']/span[text()='Unlike']")

    if len(like_elem) == 1:
        like_elem[0].send_keys("\n")
        logger.info('--> Image Liked!')
        sleep(2)
        return True
    elif len(liked_elem) == 1:
        logger.info('--> Already Liked!')
        return False
    else:
        logger.info('--> Invalid Like Element!')
        return False

def follow_account(browser, account):
    # Follow account
    try:
        follow_button = browser.find_element_by_xpath(
            "//button[text()='Follow']")

        if follow_button.is_displayed():
            follow_button.send_keys("\n")
        else:
            browser.execute_script(
                "arguments[0].style.visibility = 'visible'; "
                "arguments[0].style.height = '10px'; "
                "arguments[0].style.width = '10px'; "
                "arguments[0].style.opacity = 1", follow_button)
            follow_button.click()
    except:
        print("Already Following account " + account)