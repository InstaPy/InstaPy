from math import ceil

from instapy.utils.browser_util import reduce_wait
from instapy.utils.time_util import sleep
from instapy.utils.views_mixin import BaseMixin


class Tag(BaseMixin):
    """Handler for tag pages."""

    def __init__(self, *args, **kwargs):
        """Start page with some defaults."""
        super(Tag, self).__init__(*args, **kwargs)
        self.set_object_url('/explore/tags/')
        self.set_media()

    def get_page(self, tag):
        """Get page for a given tag."""
        tag = tag[1:] if tag[:1] == '#' else tag
        self.browser_check()
        self.set_current_obj(tag)
        return self.get_object_url()

    def set_media(self, media=None):
        """Set media to be filtered."""
        if media is None:
            # All known media types
            media = ['', 'Post', 'Video']
        elif media in ['', 'Photo', 'Post']:
            # Include posts with multiple images in it
            media = ['', 'Post']
        else:
            # Make it an array to use it in the following part
            media = [media]
        self.media = media

    def count_by_media(self):
        """Count amount of posts from specified media types."""
        count = 0
        with reduce_wait(self.browser):
            for m in self.media:
                if m:
                    count += self.count_by_xpath(
                        "//main//a//span[text() = {}]".format(m))
                else:
                    count += self.count_by_xpath(
                        "//main//a[not(text())]")
        return count

    def find_by_media(self):
        """Find media objects."""
        links = []
        with reduce_wait(self.browser):
            for m in self.media:
                if m:
                    links += self.find_multiple_by_xpath(
                        "//main//a//span[text() = {}]".format(m))
                else:
                    links += self.find_multiple_by_xpath(
                        "//main//a[not(text())]")

        links = [link_elem.get_attribute('href') for link_elem in links]
        return links

    def get_links(self, amount):
        """Get a certain amount of links for the current tag."""
        self.page_check()

        abort = False
        load_more = self.click_by_xpath("//a[text() = 'Load more']")
        if load_more is None:
            print('Load button not found, working with current images!')
            abort = True
        sleep(2)

        total_links = self.count_by_xpath("//main//a")
        filtered_links = self.count_by_media()

        while (filtered_links < amount) and not abort:
            amount_left = amount - filtered_links
            # Average items of the right media per page loaded
            new_per_page = ceil(12 * filtered_links / total_links)
            if new_per_page == 0:
                # Avoid division by zero
                new_per_page = 1. / 12.
            # Number of page load needed
            new_needed = int(ceil(amount_left / new_per_page))

            if new_needed > 12:
                # Don't go bananas trying to get all of instagram!
                new_needed = 12

            for i in range(new_needed):  # add images x * 12
                # Keep the latest window active while loading more posts
                before_load = total_links
                self.page_round_trip()
                total_links = self.count_by_xpath("//main//a")
                abort = (before_load == total_links)
                if abort:
                    break

            filtered_links = self.count_by_media()

        links = self.find_by_media()
        return links[:amount]


tag = Tag()
tag.set_target('instagram')
