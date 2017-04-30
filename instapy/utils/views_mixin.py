from sys import version_info

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from .browser_util import reduce_wait
from .exceptions import BrowserException, FormError
from .logger import default_logger
from .time_util import sleep


if version_info.major == 3:
    unicode = str


class BaseMixin(object):
    """Base Mixin for page handlers."""

    def __init__(self, *args, **kwargs):
        """Start page with some defaults."""
        self.logger = default_logger
        self.browser = None
        self.base_url = None
        self.object_url = u''
        self.object_type = None
        self._check404 = {
            'check': False
        }

    def browser_check(self, abort=True):
        """Check if browser is valid.

        if abort: raise exception.
        """
        self.logger.debug(u"Checking browser")
        if self.browser is None:
            self.logger.warning("Browser not found!")
            if abort:
                raise BrowserException("Browser not found!")
            return False
        return True

    def page_check(self, abort=True):
        """Check if page is of propper object.

        if abort: raise exception.
        """
        self.logger.debug(u"Checking page")
        browser = self.browser_check(abort)
        if not browser:
            return browser

        if self.__class__.__name__ == self.object_type:
            return True

        self.logger.warning("Must call `get_object_url` first!")
        if abort:
            raise BrowserException("Current page is not the right one!")

        return False

    def check404(self):
        """Check if page if 404.

        return True if it's a 404 page.
        """
        self.logger.debug(u"Checking 404")
        if self._check404['check']:
            text = None
            with reduce_wait(self.browser):
                text = self.get_text_by_xpath(self._check404['xpath'])

            if text == self._check404['text']:
                self.logger.debug("Page is 404!")
                return True

        else:
            self.logger.warning("Check 404 failed!")

        return False

    def set_target(self, target='instagram'):
        """Set target type.

        For now, only 'instagram' is supported.
        """
        self.logger.debug(u"Setting target as: {}".format(target))
        if target == 'instagram':
            self.base_url = u'https://www.instagram.com/'
            self._check404 = {
                'xpath': '//div[contains(@class, "error-container")]//h2',
                'text': u"Sorry, this page isn't available.",
                'check': True
            }

    def set_browser(self, browser):
        """Set browser instance."""
        self.logger.debug(u"Setting browser")
        self.browser = browser
        return self

    def get_base_url(self, force=False):
        """Get base url if it's not already opened.

        if force, always get the page.
        """
        self.logger.debug(u"Getting base url")
        if force or (self.browser.current_url != self.base_url):
            self.logger.debug(u"  Loading")
            self.logger.debug(u"  {}".format(self.base_url))
            sleep(1)
            self.browser.get(self.base_url)

        return self.check404()

    def set_object_url(self, url):
        """Set path for current object type."""
        self.logger.debug(u"Setting object url as: {}".format(url))
        url = unicode(url)
        self.object_url = url[1:] if url[:1] == '/' else url

    def set_current_obj(self, obj):
        """Set identifier for current object."""
        self.logger.debug(u"Setting current object as: {}".format(obj))
        self._current = unicode(obj)

    def get_current_obj(self, obj=None):
        """Get current object identifier."""
        self.logger.debug(u"Getting current object")
        if obj is None:
            return self._current

        obj = unicode(obj)
        obj = obj[1:] if obj[:1] == '/' else obj
        return obj

    def get_object_url(self, obj=None, force=False):
        """Get current object url.

        if obj: get url for this obj;
        if force: get url even if it's already open.
        """
        self.logger.debug(u"Getting object url")
        obj = self.get_current_obj(obj)

        object_url = ''
        if self.base_url not in obj:
            object_url += self.base_url
        if self.object_url not in obj:
            object_url += self.object_url
        object_url += obj

        if force or (self.browser.current_url != object_url):
            self.logger.debug(u"  Loading")
            self.logger.debug(u"  {}".format(object_url))
            sleep(1)
            self.browser.get(object_url)

        success = not self.check404()
        self.object_type = self.__class__.__name__ if success else None

        return success

    def get_attribute_by_xpath(self, xpath, attr):
        """Get element attribute based on it's xpath."""
        self.logger.debug(u"Getting element {}".format(attr))
        self.logger.debug(u"  with xpath = {}".format(xpath))
        sleep(1)
        element = self.browser.find_element_by_xpath(xpath)
        if attr == 'text':
            value = element.text
        else:
            value = element.get_attribute(attr)
        return value

    def get_text_by_xpath(self, xpath):
        """Get element text based on it's xpath."""
        return self.get_attribute_by_xpath(xpath, 'text')

    def find_by_xpath(self, xpath):
        """Find element by it's xpath."""
        self.logger.debug(u"Finding element")
        self.logger.debug(u"  with xpath = {}".format(xpath))
        return self.browser.find_element_by_xpath(xpath)

    def find_multiple_by_xpath(self, xpath):
        """Find all elements with this xpath."""
        self.logger.debug(u"Finding multiple elements")
        self.logger.debug(u"  with xpath = {}".format(xpath))
        return self.browser.find_elements_by_xpath(xpath)

    def click_by_xpath(self, xpath):
        """Click on element based on it's xpath."""
        element = self.find_by_xpath(xpath)
        if element is None:
            return

        self.logger.debug(u"  clicking".format(xpath))
        sleep(1)
        ActionChains(self.browser) \
            .move_to_element(element) \
            .click() \
            .perform()

        sleep(2)
        return element

    def submit_form_by_xpath(self, xpath, inputs):
        """Fill and submit a form based on it's xpath.

        inputs must be a list of inputs to this form.
        """
        input_elements = self.fill_form_by_xpath(xpath, inputs)
        self.logger.debug(u"  ssubmitting")
        last_element = input_elements[-1]
        last_element.submit()

        sleep(2)
        return last_element

    def fill_form_by_xpath(self, xpath, inputs):
        """Fill a form based on it's xpath.

        inputs must be a list of inputs to this form.
        """
        input_elements = self.find_multiple_by_xpath(xpath)

        if len(inputs) != len(input_elements):
            self.logger.error(u"Inputs and Elements missmatch")
            self.logger.debug(u"  {} inputs".format(len(inputs)))
            self.logger.debug(u"  {} elements".format(len(input_elements)))
            raise FormError('Inputs and Elements missmatch!')

        self.logger.debug(u"  sending keys to inputs")
        for i, el in zip(inputs, input_elements):
            sleep(1)
            ActionChains(self.browser) \
                .move_to_element(el) \
                .click() \
                .send_keys(i) \
                .perform()

        return input_elements

    def fill_form(self, inputs):
        """Fill a default form.

        inputs must be a list of inputs to this form.
        """
        self.logger.debug(u"Filling a default form")
        return self.fill_form_by_xpath("//form/div/input", inputs)

    def count_by_xpath(self, xpath):
        """Count number of elements with some xpath."""
        self.logger.debug(u"Counting elements")
        self.logger.debug(u"  with xpath = {}".format(xpath))
        return len(self.find_multiple_by_xpath(xpath))

    def page_round_trip(self, times=1):
        """Make a page round trip.

        i.e. go to the END than go HOME.
        """
        self.logger.debug(u"Round tripping page {} times".format(times))
        body = self.find_by_xpath('//body')
        for i in range(times):
            body.send_keys(Keys.END)
            sleep(1)
            body.send_keys(Keys.HOME)
            sleep(1)
