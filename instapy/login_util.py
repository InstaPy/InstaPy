"""Module only used for the login part of the script"""
from time import sleep
from selenium.common.exceptions import NoSuchElementException

def login_user(browser, username, password):
  """Logins the user with the given username and password"""
  browser.get('https://www.instagram.com')

  #clicks the log in if you have an account link
  login_elem = browser.find_element_by_class_name('_fcn8k')
  login_elem.click()

  # enters username and password and logs the user in
  username_elem = browser.find_element_by_name('username')
  passwd_elem = browser.find_element_by_name('password')
  login_div = browser.find_element_by_class_name('_uikn3')
  login_elem = login_div.find_element_by_tag_name('button')

  username_elem.send_keys(username)
  passwd_elem.send_keys(password)
  login_elem.click()

  sleep(2)

  try:
    browser.find_element_by_class_name('_q90d5')
    return False
  except NoSuchElementException as err:
    return True