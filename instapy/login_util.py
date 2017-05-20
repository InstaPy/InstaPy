"""Module only used for the login part of the script"""
from .time_util import sleep
from selenium.webdriver.common.action_chains import ActionChains

def login_user(browser, username, password):
  """Logins the user with the given username and password"""
  browser.get('https://www.instagram.com')

  # Changes instagram language to english, to ensure no errors ensue from having the site on a different language
  browser.find_element_by_xpath("//footer[@class='_oofbn']/div[@class='_mhrsk _pcuq6']/nav["
                                "@class='_p1gbi']/ul[@class='_fh0f2']/li[@class='_fw3ds'][10]/"
                                "span[@class='_17z9g']/select[@class='_nif11']/option"
                                "[text()='English']").click()
  #Check if the first div is 'Create an Account' or 'Log In'
  login_elem = browser.find_element_by_xpath("//article/div/div/p/a[text()='Log in']")
  if login_elem is not None:
    action = ActionChains(browser).move_to_element(login_elem).click().perform()

  #Enter username and password and logs the user in
  #Sometimes the element name isn't 'Username' and 'Password' (valid for placeholder too)
  inputs = browser.find_elements_by_xpath("//form/div/input")
  action = ActionChains(browser).move_to_element(inputs[0]).click().send_keys(username) \
          .move_to_element(inputs[1]).click().send_keys(password).perform()

  login_button = browser.find_element_by_xpath("//form/span/button[text()='Log in']")
  action = ActionChains(browser).move_to_element(login_button).click().perform()

  sleep(2)
  
  #Check if user is logged-in (If there's two 'nav' elements)
  nav = browser.find_elements_by_xpath('//nav')
  if len(nav) == 2:
    return True
  else:
    return False
