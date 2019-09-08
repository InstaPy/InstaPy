"""
Class to define the specific actions for the legacy engine
"""

from instapy.common import Logger
from instapy.drivers import Actions
from instapy import InstaPy

# ideally
# class LegacyEngine(Engine):
class LegacyEngine(object):
    """
    Class that contains all the different method used originally
    by instapy
    """


    @classmethod
    def follow_likers(cls,
                      instapy: InstaPy,
                      usernames: list,
                      photos_grab_amount: int = 3,
                      follow_likers_per_photo: int = 3,
                      randomize: bool = True,
                      interact: bool = False,
                      ):

        """ Follows users' likers """
        # TODO: replace with something better
        # if self.aborting:
        #     return self

        message = "Starting to follow likers.."
        Logger.highlight_print(instapy.username, message, "feature", "info")

        if not isinstance(usernames, list):
            usernames = [usernames]

        if photos_grab_amount > 12:
            Logger.info(
                "Sorry, you can only grab likers from first 12 photos for "
                "given username now.\n"
            )
            photos_grab_amount = 12

        followed_all = 0
        followed_new = 0

        # hold the current global values for differentiating at the end
        already_followed_init = instapy.already_followed
        not_valid_users_init = instapy.not_valid_users
        liked_init = instapy.liked_img
        already_liked_init = instapy.already_liked
        commented_init = instapy.commented
        inap_img_init = instapy.inap_img

        # relax_point = random.randint(7, 14)  # you can use some plain value
        # `10` instead of this quitely randomized score
        instapy.quotient_breach = False

        for username in usernames:
            if instapy.quotient_breach:
                break

            posts = instapy.actions.get_posts(username, photos_grab_amount, randomize)

            # sleep(1)
            if not isinstance(posts, list):
                posts = [posts]

            for post in posts:
                if instapy.quotient_breach:
                    break

                likers = post.get_likers(follow_likers_per_photo)
                # likers is of type User
                # This way of iterating will prevent sleep interference
                # between functions
                random.shuffle(likers)

                for liker in likers[:follow_likers_per_photo]:
                    if instapy.quotient_breach:
                        Logger.warning(
                            "--> Follow quotient reached its peak!"
                            "\t~leaving Follow-Likers activity\n"
                        )
                        break

                    # what does this do???
                    followed = liker.follow(interact)

                    if followed > 0:
                        followed_all += 1
                        followed_new += 1
                        Logger.info("Total Follow: {}\n".format(str(followed_all)))

                        instapy.action_delay(action='follow')

                        # to delete this code, just kept to validate for the moment
                        # Take a break after a good following

                        # if followed_new >= relax_point:
                        #     delay_random = random.randint(
                        #         ceil(sleep_delay * 0.85), ceil(sleep_delay * 1.14)
                        #     )
                        #     sleep_time = (
                        #         "{} seconds".format(delay_random)
                        #         if delay_random < 60
                        #         else "{} minutes".format(
                        #             truncate_float(delay_random / 60, 2)
                        #         )
                        #     )
                        #     Logger.info(
                        #         "------=>  Followed {} new users ~sleeping "
                        #         "about {}".format(followed_new, sleep_time)
                        #     )
                        #     sleep(delay_random)
                        #     relax_point = random.randint(7, 14)
                        #     followed_new = 0
                        #     pass

        Logger.info("Finished following Likers!\n")

        # find the feature-wide action sizes by taking a difference
        already_followed = instapy.already_followed - already_followed_init
        not_valid_users = instapy.not_valid_users - not_valid_users_init
        liked = instapy.liked_img - liked_init
        already_liked = instapy.already_liked - already_liked_init
        commented = instapy.commented - commented_init
        inap_img = instapy.inap_img - inap_img_init

        # print results
        Logger.info("Followed: {}".format(followed_all))
        Logger.info("Already followed: {}".format(already_followed))
        Logger.info("Not valid users: {}".format(not_valid_users))

        if interact is True:
            print("")
            # print results out of interactions
            Logger.info("Liked: {}".format(liked))
            Logger.info("Already Liked: {}".format(already_liked))
            Logger.info("Commented: {}".format(commented))
            Logger.info("Inappropriate: {}".format(inap_img))

        return followed_all
