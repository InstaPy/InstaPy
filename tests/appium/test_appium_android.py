from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction

from time import sleep

insta_username = ''
insta_password = ''
desired_caps = {}

desired_caps['platformName'] = 'Android'
desired_caps['deviceName'] = 'emulator-5554'
desired_caps['appPackage'] = 'com.instagram.android'
desired_caps['appActivity'] = 'com.instagram.mainactivity.MainActivity'
desired_caps['noReset'] = True
desired_caps['fullReset'] = False
desired_caps['unicodeKeyboard'] = True
desired_caps['resetKeyboard'] = True
desired_caps['newCommandTimeout'] = 600

driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
print('Succesfully connected with android device!')
sleep(5)

current_activity = driver.current_activity.split('.')[-1]

# Lets log in!
if 'SignedOut' in current_activity:
    check_login = driver.find_elements_by_xpath("//android.widget.TextView[@text='Log In']")
    check_login[0].click()

    username_edit_text = driver.find_elements_by_xpath("//android.widget.EditText[@resource-id='com.instagram.android:id/login_username']")
    username_edit_text[0].set_value(insta_username)

    password_edit_text = driver.find_elements_by_xpath("//android.widget.EditText[@resource-id='com.instagram.android:id/password']")
    password_edit_text[0].set_value(insta_password)
    sleep(1)

    log_in = driver.find_elements_by_xpath("//android.widget.TextView[@resource-id='com.instagram.android:id/button_text']")
    log_in[0].click()

    if driver.current_activity.split('.')[-1] == 'MainActivity':
        print('Succesfully Logged in!')


# Let's log out!
profile = driver.find_elements_by_xpath("//android.widget.FrameLayout[@content-desc='Profile' and @index=4]")
profile[0].click()
sleep(1)
options = driver.find_elements_by_xpath("//android.widget.FrameLayout[@content-desc='Options']")
options[0].click()
sleep(1)
settings = driver.find_elements_by_xpath("//android.widget.TextView[@resource-id='com.instagram.android:id/menu_settings_row']")
settings[0].click()
sleep(1)

#Scroll down a bit!
driver.swipe(0,0,0,100,100)
sleep(3)

logout = driver.find_element_by_id("com.instagram.android:id/row_simple_link_textview")
logout.click()
sleep(1)
