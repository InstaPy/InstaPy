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

    def __init__(self, link=None, name=None, text=None, post_count=None, follower_count=None, following_count=None):
        self.link = link
        self.name = name

        if self.name and not self.link:
            self.link = "https://www.instagram.com/{}/".format(self.name)

        elif self.link and not self.name:
            self.name = self.link.rstrip("/").rsplit("/", 1)[-1]

        self.text = text # TODO: retrieve bio from user profile
        self.post_count = post_count
        self.follower_count = follower_count
        self.following_count = following_count


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
        return "User({0}, {1}, {2}, {3}, {4}, {5})".format(hash(self), self.link, self.name, self.post_count, self.follower_count, self.following_count)


    def __str__(self):
        return repr(self)


    def show(self, session):
        web_address_navigator(session.browser, self.link)


    def count_posts(self, session, refresh=False):
        print("[+] counting posts")

        if not self.post_count or refresh:
            self.show(session)
            self.post_count = get_number_of_posts(session.browser)

        print(" - {0} posts".format(self.post_count))
        return self.post_count


    def count_followers(self, session, refresh=False):
        print("[+] counting followers")

        if not self.follower_count or refresh:
            self.follower_count, _ = get_relationship_counts(session.browser, self.name, session.logger)

        print(" - {0} followers".format(self.follower_count))
        return self.follower_count


    def count_following(self, session, refresh=False):
        print("[+] counting following")

        if not self.following_count or refresh:
            _, self.following_count = get_relationship_counts(session.browser, self.name, session.logger)

        print(" - {0} following".format(self.following_count))
        return self.following_count


    def populate(self, session):
        print("[+] populating user values")
        self.show(session)
        self.count_posts(session, refresh=False)
        self.count_followers(session, refresh=False)
        self.count_following(session, refresh=False)


    def refresh(self, session):
        print("[+] refreshing user values")
        self.show(session)
        self.count_posts(session, refresh=True)
        self.follower_count, self.following_count = get_relationship_counts(session.browser, self.name, session.logger)


    def follow(self, session):
        print("[+] follow user")
        self.show(session)

        user_id = find_user_id(session.browser, "profile", self.name, session.logger)

        follow_state, msg = follow_user(
                    session.browser,
                    "profile",
                    session.username,
                    self.name,
                    None,
                    session.blacklist,
                    session.logger,
                    session.logfolder,
                )

        print(" - followed {0}: {1}".format(self.name, follow_state))
        return follow_state


    def unfollow(self, session):
        print("[+] unfollow user")
        self.show(session)

        user_id = find_user_id(session.browser, "profile", self.name, session.logger)
        unfollow_state, msg = unfollow_user(
                            session.browser,
                            "profile",
                            session.username,
                            self.name,
                            user_id,
                            None,
                            session.relationship_data,
                            session.logger,
                            session.logfolder,
                        )

        print(" - unfollowed {0}: {1}".format(self.name, unfollow_state))
        return unfollow_state


    def get_following(self, session, offset=0, limit=None, live_match=False, store_locally=True):
        print("[+] get user following")
        self.show(session)

        if not limit:
            limit = self.count_following(session) - offset

        raw_following = get_following_original(
            session.browser,
            self.name,
            limit + offset,
            session.relationship_data,
            live_match,
            store_locally,
            session.logger,
            session.logfolder,
        )

        following = set()
        start = min(offset, len(raw_following))
        last = min(offset+limit, len(raw_following))
        for raw_followed in raw_following[start:last]:
            follower = User(name=raw_followed)
            following.add(follower)

        print(" - returning {0} of the total {1}".format(len(following), self.count_following(session)))
        return following


    def get_followers(self, session, offset=0, limit=None, live_match=False, store_locally=True):
        print("[+] get user followers")
        self.show(session)

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

        followers = set()
        start = min(offset, len(raw_followers))
        last = min(offset+limit, len(raw_followers))
        for raw_follower in raw_followers[start:last]:
            follower = User(name=raw_follower)
            followers.add(follower)

        print(" - returning {0} of the total {1}".format(len(followers), self.count_followers(session)))
        return followers


    def get_posts(self, session, offset=0, limit=None):
        # avoid curcular dependencies
        from .posts import Post

        print("[+] get user posts")
        self.show(session)

        if not limit:
            limit = self.count_followers(session) - offset

        raw_links = get_links_for_username(
            session.browser,
            session.username,
            self.name,
            limit + offset,
            session.logger,
            session.logfolder,
            randomize=False,
            media=None,
            taggedImages=False,
        )

        posts = set()

        start = min(offset, len(raw_links))
        last = min(offset+limit, len(raw_links))
        for raw_link in raw_links[start:last]:
            post = Post(link=raw_link)
            posts.add(post)

        print(" - returning {0} of the total {1}".format(len(posts), self.count_posts(session)))
        return posts
