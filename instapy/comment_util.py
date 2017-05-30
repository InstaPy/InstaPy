# -*- coding: utf-8 -*-
"""Module which handles the commenting features"""
from random import choice
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .time_util import sleep
import emoji

def comment_image(browser, comments):
  """Checks if it should comment on the image"""
  rand_comment = (choice(comments))
  rand_comment = emoji.demojize(rand_comment)
  rand_comment = emoji.emojize(rand_comment, use_aliases=True)


  try:
    #Explicitly will wait up to 10 seconds to find the element but may return sooner
    comment_input = WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,'//input[@placeholder = "Add a comment…"]')))

    browser.execute_script("arguments[0].value = '" + rand_comment + " ';", comment_input);
    #An extra space is added here and then deleted. This forces the input box to update the reactJS core
    comment_input.send_keys("\b")
    comment_input.submit()

    # print(u'--> Commented: {}'.format(rand_comment))
    print("--> Commented: " + rand_comment.encode('utf-8'))
    sleep(2)
  except TimeoutException:
    print("--> Warning: Comment box could not be found within an acceptable ammount of time, skipping comment")


  return 1
