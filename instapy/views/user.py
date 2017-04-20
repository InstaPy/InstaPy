from instapy.utils.views_mixin import BaseMixin


class User(BaseMixin):
    """Handler for user pages."""

    def __init__(self, *args, **kwargs):
        """Start page with some defaults."""
        super(User, self).__init__(*args, **kwargs)

    def get_page(self, username):
        """Get page for a given object."""
        self.browser_check()
        self.set_current_obj(username)
        return self.get_object_url()

    def get_followers(self):
        """Get number of followers from current page."""
        self.page_check()
        followers = self.browser.execute_script("""
            return window._sharedData.entry_data.ProfilePage[0]
                   .user.followed_by.count
        """)

        return followers

    def get_followers_list(self):
        """Get all followers from current page."""
        raise NotImplementedError

    def follow(self, unfollow=False):
        """Follow current user page.

        if unfollow: unfollows user.
        """
        self.page_check()
        follow_xpath = "//*[contains(text(), 'Follow')]"
        follow_text = 'Following' if unfollow else 'Follow'
        follow = self.get_text_by_xpath(follow_xpath) == follow_text
        if follow:
            self.click_by_xpath(follow_xpath)

        return follow

    def unfollow(self):
        """Unfollow current user page."""
        return self.follow(unfollow=True)


user = User()
user.set_target('instagram')
