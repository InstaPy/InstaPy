from selenium.webdriver.common.action_chains import ActionChains
import os
from random import randint
import pyautogui
from .time_util import sleep
from selenium.webdriver.common.keys import Keys
import random
from random import randint

def upload_file(browser, image_to_post, logger):

    try:
        # Save the window opener (current window, do not mistaken with tab... not the same)
        main_window = browser.current_window_handle

        post_button = browser.find_element_by_xpath('//*[contains(@class, "coreSpriteFeedCreation")]')
        ActionChains(browser).move_to_element(post_button).click().perform()

        browser.switch_to_window(main_window)
        sleep(1)
        # Put focus on current window which will be the window opener
        pyautogui.hotkey('command', 'shift', 'g')
        pyautogui.typewrite(image_to_post)
        pyautogui.press('enter')
        pyautogui.press('enter')
        return True
    except:
        logger.error("Failed to Upload the File")


def make_a_post(logger, browser, folder, description, tags, percentage):

    if(randint(1 ,100) <= percentage):
        # opening the folder
        try:
            images = []
            image_to_post = None
            for filename in os.listdir(os.getcwd()+folder):
                images.append(os.getcwd()+folder+"/"+filename)

            if len(images):
                image_to_post = images[randint(0,len(images)-1)]

            file_uploaded = upload_file(browser, image_to_post, logger)
            sleep(5)

            if(file_uploaded):
                description_added = add_description(browser, description, tags, logger)

                if(description_added):
                    share_button = browser.find_element_by_xpath('//button[contains(text(),"Share")]')
                    ActionChains(browser).move_to_element(share_button).click().perform()
                    sleep(10)
                    logger.info("Made a Post")

                    # removing the posted image
                    os.remove(image_to_post)
                    return True

        except:
            logger.error("Failed to make a Post")
        return False

    else:
        logger.info("Chose not to make a Post")
        return False

def add_description(browser, description, tags, logger):
    try:
        next_button = browser.find_element_by_xpath('//button[contains(text(),"Next")]')
        ActionChains(browser).move_to_element(next_button).click().perform()

        browser.find_element_by_xpath('//textarea[last()]').clear()
        browser.find_element_by_xpath('//textarea[last()]').send_keys(description)
        for i in range(5):
            browser.find_element_by_xpath('//textarea[last()]').send_keys(Keys.ENTER)
            browser.find_element_by_xpath('//textarea[last()]').send_keys("*")
        browser.find_element_by_xpath('//textarea[last()]').send_keys(Keys.ENTER)
        browser.find_element_by_xpath('//textarea[last()]').send_keys(" ".join(random.sample(tags, 20 if len(tags) > 20 else len(tags))))
        return True

    except:
        logger.error("Failed to add Description")