"""
Class to define the specific actions for the legacy engine
"""

from instapy.common import Logger
from instapy.drivers import WebDriver
from instapy import InstaPy

# ideally
# class LegacyEngine(Engine):
class LegacyEngine(object):
    """
    Class that contains all the different method used originally
    by instapy
    """

    @classmethod
    def follow_likers(
        cls,
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
        already_followed_init = instapy.settings.already_followed
        not_valid_users_init = instapy.setting.not_valid_users
        liked_init = instapy.settings.liked_img
        already_liked_init = instapy.settings.already_liked
        commented_init = instapy.settings.commented
        inap_img_init = instapy.settings.inap_img

        # relax_point = random.randint(7, 14)  # you can use some plain value
        # `10` instead of this quitely randomized score
        instapy.settings.quotient_breach = False

        for username in usernames:
            if instapy.settings.quotient_breach:
                break

            posts = instapy.driver.user.get_posts(username, photos_grab_amount, randomize)

            # sleep(1)
            if not isinstance(posts, list):
                posts = [posts]

            for post in posts:
                if instapy.settings.quotient_breach:
                    break

                likers = instapy.driver.post.get_likers(follow_likers_per_photo)
                # likers is of type User
                # This way of iterating will prevent sleep interference
                # between functions
                random.shuffle(likers)

                for liker in likers[:follow_likers_per_photo]:
                    if instapy.settings.quotient_breach:
                        Logger.warning(
                            "--> Follow quotient reached its peak!"
                            "\t~leaving Follow-Likers activity\n"
                        )
                        break


                    followed = instapy.driver.liker.follow()
                    if interact:
                        # have an interact function that do it
                        # cls.interact(liker) !will activate later
                        pass

                    if followed > 0:
                        followed_all += 1
                        followed_new += 1
                        Logger.info("Total Follow: {}\n".format(str(followed_all)))


        Logger.info("Finished following Likers!\n")

        # find the feature-wide action sizes by taking a difference
        already_followed = instapy.settings.already_followed - already_followed_init
        not_valid_users = instapy.settings.not_valid_users - not_valid_users_init
        liked = instapy.settings.liked_img - liked_init
        already_liked = instapy.settings.already_liked - already_liked_init
        commented = instapy.settings.commented - commented_init
        inap_img = instapy.settings.inap_img - inap_img_init

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
