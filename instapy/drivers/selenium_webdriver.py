"""
Class to define everything needed to work with Appium
"""

class SeleniumWebDriver(object):

    driver = None
    webdriver_instance = None  # might not be needed

    def __init__(self,
                 proxy_address,
        proxy_port,
        proxy_username,
        proxy_password,
        headless_browser,
        browser_profile_path,
        disable_image_load,
        geckodriver_path,
    ):
        """

        :param proxy_address:
        :param proxy_port:
        :param proxy_username:
        :param proxy_password:
        :param headless_browser:
        :param browser_profile_path:
        :param disable_image_load:
        :param geckodriver_path:
        """
        print("To be Implemented")
