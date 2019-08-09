#!/usr/bin/env python3
"""
Post model for interactions posts attributes and perform action on posts
"""
import time
from datetime import datetime
from enum import Enum

from .. import InstaPy, smart_run
from ..unfollow_util import follow_user, unfollow_user
from ..like_util import get_links_for_tag, like_image
from ..commenters_util import extract_post_info, users_liked
from ..comment_util import get_comments_count, is_commenting_enabled, comment_image, open_comment_section
from ..util import web_address_navigator, get_current_url, explicit_wait, extract_text_from_element, find_user_id
from ..xpath import read_xpath

from .comments import Comment
from .users import User


class Post(object):


    class Types(Enum):
        PHOTO = 0
        CAROUSEL = 1
        VIDEO = 2


    def __init__(self, link=None, type=None, user=None):
        self.link = link
        self.type = type
        self.user = user

        self.like_count = None
        self.comment_count = None


    def __hash__(self):
        return hash(self.link)


    def __eq__(self, other):
        if isinstance(other, type(self)):
            return hash(self) == hash(other)
        else:
            return False


    def __repr__(self):
        return "Post({0}, {1}, {2})".format(hash(self), self.type, self.link)


    def __str__(self):
        return repr(self)


    def show(self, session):
        web_address_navigator(session.browser, self.link)


    def count_likes(self, session, refresh=False):
        print("[+] counting likes")

        if not self.like_count or refresh:
            self.show(session)

            count = session.browser.execute_script(
                "return window._sharedData.entry_data."
                "PostPage[0].graphql.shortcode_media.edge_media_preview_like"
                ".count"
            )

            if not count:
                count = 0

            self.like_count = count

        print(" - {0} likes".format(self.like_count))
        return self.like_count


    def count_comments(self, session, refresh=False):
        print("[+] counting comments")

        if not self.comment_count or refresh:
            self.show(session)

            # Check commenting is available
            commenting_state, msg = is_commenting_enabled(session.browser, session.logger)

            if commenting_state:
                count, msg = get_comments_count(session.browser, session.logger)

            # Fallback in case of error
            if not count:
                count = 0

            self.comment_count = count

        print(" - {0} comments".format(self.comment_count))

        return self.comment_count


    def populate(self, session):
        print("[+] populating post values")
        self.show(session)
        self.count_likes(session, refresh=False)
        self.count_comments(session, refresh=False)


    def refresh(self, session):
        print("[+] refreshing post values")
        self.show(session)
        self.count_likes(session, refresh=True)
        self.count_comments(session, refresh=True)


    def like(self, session, verify=False):
        print("[+] liking post")
        self.show(session)

        if verify:
            like_image(session.browser, session.username, session.blacklist, session.logger, session.logfolder, 0)

        else:
            like_image(session.browser, session.username, session.blacklist, session.logger, session.logfolder, 1)


    # TODO: implement
    def unlike(self, session, verify=False):
        print("[+] unlike post")
        print("NOT YET IMPLEMENTED")
        pass


    def comment(self, session, comment=None):
        print("[+] comment on post")
        self.show(session)

        if comment:
            comment_image(session.browser, session.username, [comment], session.blacklist, session.logger, session.logfolder)

        else:
            comment_image(session.browser, session.username, session.comments, session.blacklist, session.logger, session.logfolder)


    def follow(self, session):
        print("[+] follow user")
        self.show(session)

        user = self.get_user(session)
        user_id = find_user_id(session.browser, "post", user.name, session.logger)

        follow_state, msg = follow_user(
                    session.browser,
                    "post",
                    session.username,
                    user.name,
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

        user = self.get_user(session)
        user_id = find_user_id(session.browser, "post", user.name, session.logger)
        unfollow_state, msg = unfollow_user(
                            session.browser,
                            "post",
                            session.username,
                            user.name,
                            user_id,
                            None,
                            session.relationship_data,
                            session.logger,
                            session.logfolder,
                        )

        print(" - unfollowed {0}: {1}".format(self.name, unfollow_state))
        return unfollow_state


    def get_user(self, session, refresh=False):
        print("[+] retrieving user")

        if not self.user or refresh:
            self.show(session)

            post_page = session.browser.execute_script(
                "return window._sharedData.entry_data.PostPage"
            )

            graphql = "graphql" in post_page[0]
            if graphql:
                media = post_page[0]["graphql"]["shortcode_media"]
                username = media["owner"]["username"]

            else:
                media = post_page[0]["media"]
                username = media["owner"]["username"]

            self.user = username

        return User(name=self.user)


    # Retrieve all comments form a post
    # TODO: scroll for more comments and handle exceptions
    def get_comments(self, session, offset=0, limit=None, randomize=False):
        print("[+] retrieving comments")
        self.show(session)

        if not limit:
            limit = self.count_comments(session) - offset

        open_comment_section(session.browser, session.logger)
        link = get_current_url(session.browser)
        time.sleep(3)

        # Comments block
        comments_block_XPath = read_xpath("get_comments_on_post", "comments_block")

        # wait for page fully load [IMPORTANT!]
        explicit_wait(session.browser, "PFL", [], session.logger, 10)
        comments_block = session.browser.find_elements_by_xpath(comments_block_XPath)

        comments = set()
        start = min(offset, len(comments_block))
        last = min(offset+limit, len(comments_block))
        for comment_line in comments_block[start:last]:
            comment_links = comment_line.find_elements_by_tag_name("a")

            # Commenter
            commenter_elem = comment_links[1]
            commenter = extract_text_from_element(commenter_elem)

            # Text
            comment_elem = comment_line.find_elements_by_tag_name("span")[0]
            text = extract_text_from_element(comment_elem)

            # Likes count
            if len(comment_links) >= 3:
                like_elem = comment_links[2]
                like_text = extract_text_from_element(like_elem)
                like_count = int(like_text.split(" ")[0])

            else:
                like_count = 0

            # Timestamp
            timestamp_elem = comment_line.find_element_by_tag_name("time")
            timestamp_string = timestamp_elem.get_attribute('datetime')
            timestamp = datetime.strptime(timestamp_string, "%Y-%m-%dT%H:%M:%S.%fZ")

            # Make our comment object
            comment = Comment(link=link, user=commenter, text=text, like_count=like_count, timestamp=timestamp)
            comments.add(comment)

            print(comment)

        return comments


    def get_likers(self, session, offset=0, limit=None):
        print("[+] get post likers")
        self.show(session)

        if not limit:
            limit = self.count_likes(session) - offset

        raw_likers = users_liked(session.browser, self.link, amount=limit + offset)

        likers = set()
        start = min(offset, len(raw_likers))
        last = min(offset+limit, len(raw_likers))
        for raw_liker in raw_likers[start:last]:
            liker = User(name=raw_liker)
            likers.add(liker)

        print(" - returning {0} of the total {1}".format(len(likers), self.like_count))
        return likers



