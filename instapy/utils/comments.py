from random import choice

from spintax import spin

from .logger import default_logger


class Comments(object):
    def __init__(self):
        self.logger = default_logger
        self.comments = []
        self.comments_photos = []
        self.comments_videos = []

    def set_comment(self, comments=[], media=None):
        if media is None:
            self.comments = comments
        elif media in ['', 'Photo', 'Post']:
            self.comments_photos = comments
        elif media in ['Video']:
            self.comments_photos = comments
        else:
            self.logger.warning("Unkown media type: {}".format(media))
            self.logger.warning("  Skipping".format(media))

    def include_comment(self, comments=[], media=None):
        if media is None:
            self.comments += comments
        elif media in ['', 'Photo', 'Post']:
            self.comments_photos += comments
        elif media in ['Video']:
            self.comments_photos += comments
        else:
            self.logger.warning("Unkown media type: {}".format(media))
            self.logger.warning("  Skipping".format(media))

    def get_random_comment(self, media=None):
        if media is None:
            rand_comment = (choice(self.comments))
        elif media in ['', 'Photo', 'Post']:
            rand_comment = (choice(self.comments + self.comments_photos))
        elif media in ['Video']:
            rand_comment = (choice(self.comments + self.comments_videos))
        else:
            self.logger.warning("Unkown media type: {}".format(media))
            self.logger.warning("  Skipping".format(media))
            return None

        return spin(rand_comment)
