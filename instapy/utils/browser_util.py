from selenium.common.exceptions import NoSuchElementException


class reduce_wait(object):
    def __init__(self, browser, new_wait=1, old_wait=25):
        self.browser = browser
        self.new_wait = new_wait
        self.old_wait = old_wait

    def __enter__(self):
        self.browser.implicitly_wait(self.new_wait)

    def __exit__(self, type, value, traceback):
        self.browser.implicitly_wait(self.old_wait)
        return isinstance(value, NoSuchElementException)
