"""
Where we keep all the stats of a session
"""

#libraries import
import time

class Stats(object):
    """
    handling the stats of an instapy session
    """

    def __init__(self):
        self.start_time = time.time()
        self.liked_img = 0
        self.already_liked = 0
        self.liked_comments = 0
        self.commented = 0
        self.replied_to_comments = 0
        self.followed = 0
        self.already_followed = 0
        self.unfollowed = 0
        self.followed_by = 0
        self.following_num = 0
        self.inap_img = 0
        self.not_valid_users = 0
        self.video_played = 0
        self.already_Visited = 0
        self.stories_watched = 0
        self.reels_watched = 0


    def live_report(self):
        """
           adapted version of instapy live report function for showing up on a telegram message
           :return:
           """
        stats = [
            self.liked_img,
            self.already_liked,
            self.commented,
            self.followed,
            self.already_followed,
            self.unfollowed,
            self.stories_watched,
            self.reels_watched,
            self.inap_img,
            self.not_valid_users,
        ]

        sessional_run_time = cls._run_time()
        run_time_info = (
            "{} seconds".format(sessional_run_time)
            if sessional_run_time < 60
            else "{} minutes".format(truncate_float(sessional_run_time / 60, 2))
            if sessional_run_time < 3600
            else "{} hours".format(truncate_float(sessional_run_time / 60 / 60, 2))
        )
        run_time_msg = "[Session lasted {}]".format(run_time_info)

        if any(stat for stat in stats):
            return (
                "Sessional Live Report:\n"
                "|> LIKED {} images\n"
                "|> ALREADY LIKED: {}\n"
                "|> COMMENTED on {} images\n"
                "|> FOLLOWED {} users\n"
                "|> ALREADY FOLLOWED: {}\n"
                "|> UNFOLLOWED {} users\n"
                "|> LIKED {} comments\n"
                "|> REPLIED to {} comments\n"
                "|> INAPPROPRIATE images: {}\n"
                "|> NOT VALID users: {}\n"
                "|> WATCHED {} story(ies)\n"
                "|> WATCHED {} reel(s)\n"
                "\n{}".format(
                    cls.liked_img,
                    cls.already_liked,
                    cls.commented,
                    cls.followed,
                    cls.already_followed,
                    cls.unfollowed,
                    cls.liked_comments,
                    cls.replied_to_comments,
                    cls.inap_img,
                    cls.not_valid_users,
                    cls.stories_watched,
                    cls.reels_watched,
                    run_time_msg,
                )
            )
        else:
            return (
                "Sessional Live Report:\n"
                "|> No any statistics to show\n"
                "\n{}".format(run_time_msg)
            )

    def _run_time(self):
        """
        get the time spent in the current session
        :return:
        """
        real_time = time.time()
        run_time = real_time - self.start_time
        run_time = truncate_float(run_time, 2)

        return run_time
