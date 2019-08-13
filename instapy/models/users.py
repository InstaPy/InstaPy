#!/usr/bin/env python3
"""
User model for interactions user attributes and perform action on users
"""
from ..util  import get_relationship_counts, get_number_of_posts, find_user_id, web_address_navigator
from ..like_util import get_links_for_username
from ..unfollow_util import follow_user, unfollow_user
from ..relationship_tools import get_following as get_following_original
from ..relationship_tools import get_followers as get_followers_original


class User(object):

    def __init__(self, link=None, name=None, session=None):
        # text=None, post_count=None, follower_count=None, following_count=None):
        self.link = link
        self.name = name
        self.session = session

        self._posts = None
        self._following = None
        self._followers = None


        if self.name and not self.link:
            self.link = "https://www.instagram.com/{}/".format(self.name)

        elif self.link and not self.name:
            self.name = self.link.rstrip("/").rsplit("/", 1)[-1]

        # properties that we have to init correctly
        # don't think this is correct (the __init__ should also be corrected)
        # ensure we are on the correct page to get the infos we need
        if (self.link is not none):
            self.populate()
            self.text = '' # TODO: retrieve bio from user profile

        # we use a getter for post_count, follower_count, following_count
        # we fill it when required





    # Used for working with sets
    def __hash__(self):
        return hash(self.link)


    # Used for working with sets
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return hash(self) == hash(other)
        else:
            return False


    def __repr__(self):
        return "User({0}, {1}, {2}, {3}, {4}, {5})".format(hash(self), self.link, self.name, self.posts, self.followers, self.following)


    def __str__(self):
        return repr(self)

    @property
    def posts(self):
        """
        Getter for post_count (self.post_count will call this function automatically)
        :return:
        """
        if self._posts is None:
            self._posts = get_number_of_posts(self.session.browser)

        return self._posts

    @property
    def followers(self):
        """
        Getter for follower_count (self.follower_count will call this function automatically)
        :return:
        """
        if (self._followers is None) or (self._following is None):
            self._followers, self._following = get_relationship_counts(self.session.browser, self.name, self.session.logger)

        return self._followers

    @property
    def following(self):
        """
        Getter for following_count (self.following_count will call this function automatically)
        :return:
        """
        if (self._followers is None) or (self._following is None):
            self._followers, self._following = get_relationship_counts(self.session.browser, self.name,
                                                                          self.session.logger)

        return self._following

    def populate(self):
        """
         load the data into the User object
         :param session:
         :return:
         """
        print("[+] populating user values")
        web_address_navigator(self.session.browser, self.link)
        print(" - posts={0} following={0} followers={0}".format(self.posts,self.following, self.followers))


    # same as populate, so we should keep only one of the 2
    # def refresh(self, session):
    #     """
    #      description here
    #      :param session:
    #      :return:
    #      """
    #     print("[+] refreshing user values")
    #     self.show(session)
    #     self.count_posts(session, refresh=True)
    #     self.follower_count, self.following_count = get_relationship_counts(session.browser, self.name, session.logger)


    def follow(self):
        """
         description here
         :param session:
         :return:
         """
        print("[+] follow user")

        _ = find_user_id(self.session.browser, "profile", self.name, self.session.logger)

        follow_state, msg = follow_user(
                    self.session.browser,
                    "profile",
                    self.session.username,
                    self.name,
                    None,
                    self.session.blacklist,
                    self.session.logger,
                    self.session.logfolder,
                )

        print(" - followed {0}: {1}".format(self.name, follow_state))
        return follow_state


    def unfollow(self):
        """
         description here
         :param session:
         :return:
         """
        print("[+] unfollow user")

        user_id = find_user_id(self.session.browser, "profile", self.name, self.session.logger)
        unfollow_state, msg = unfollow_user(
                            self.session.browser,
                            "profile",
                            self.session.username,
                            self.name,
                            user_id,
                            None,
                            self.session.relationship_data,
                            self.session.logger,
                            self.session.logfolder,
                        )

        print(" - unfollowed {0}: {1}".format(self.name, unfollow_state))
        return unfollow_state


    def get_following(self, offset=0, limit=None, live_match=False, store_locally=True):
        """
         description here
         :param session:
         :return:
         """
        print("[+] get user following")

        if not limit:
            limit = self.following - offset

        raw_following = get_following_original(
            self.session.browser,
            self.name,
            limit + offset,
            self.session.relationship_data,
            live_match,
            store_locally,
            self.session.logger,
            self.session.logfolder,
        )

        following_set = set()
        start = min(offset, len(raw_following))
        last = min(offset+limit, len(raw_following))
        for raw_followed in raw_following[start:last]:
            following_set.add(User(name=raw_followed))

        print(" - returning {0} of the total {1}".format(len(following_set), self.count_following(session)))
        return following


    def get_followers(self, session, offset=0, limit=None, live_match=False, store_locally=True):
        """
         description here
         :param session:
         :return:
         """
        print("[+] get user followers")

        if not limit:
            limit = self.count_followers(session) - offset

        raw_followers = get_followers_original(
            session.browser,
            self.name,
            limit + offset,
            session.relationship_data,
            live_match,
            store_locally,
            session.logger,
            session.logfolder,
        )

        followers_set = set()
        start = min(offset, len(raw_followers))
        last = min(offset+limit, len(raw_followers))
        for raw_follower in raw_followers[start:last]:
            followers_set.add(User(name=raw_follower, session=session))

        print(" - returning {0} of the total {1}".format(len(followers_set), self.followers))
        return followers


    def get_posts(self, session, offset=0, limit=None):
        """
         description here
         :param session:
         :return:
         """
        # avoid circular dependencies
        from .posts import Post

        print("[+] get user posts")

        if not limit:
            limit = self.followers - offset

        raw_links = get_links_for_username(
            self.session.browser,
            self.session.username,
            self.name,
            limit + offset,
            self.session.logger,
            self.session.logfolder,
            randomize=False,
            media=None,
            taggedImages=False,
        )

        posts_set = set()

        start = min(offset, len(raw_links))
        last = min(offset+limit, len(raw_links))
        for raw_link in raw_links[start:last]:
            posts_set.add(Post(link=raw_link, session=session))

        print(" - returning {0} of the total {1}".format(len(posts_set), self.posts))
        return posts

    def _navigate(self):
        """
        private function that checks where the browser is and if not on the User
        navigate to the correct URL
        :return:
        """
        web_address_navigator(self.session.browser, self.link)