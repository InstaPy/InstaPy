from instapy.utils.time_util import sleep
from instapy.utils.views_mixin import BaseMixin


class Landing(BaseMixin):
    """Handler for the landing page."""

    def __init__(self, *args, **kwargs):
        """Start page with some defaults."""
        super(Landing, self).__init__(*args, **kwargs)

    def login(self, username, password):
        """Log user in."""
        self.browser_check()
        self.get_base_url()
        self.click_by_xpath("//article/div/div/p/a[text()='Log in']")
        self.fill_form(inputs=[username, password])
        self.click_by_xpath("//form/span/button[text()='Log in']")

        # We need some extra time here...
        sleep(5)

        return (self.count_by_xpath("//nav") == 2)

landing = Landing()
landing.set_target('instagram')
