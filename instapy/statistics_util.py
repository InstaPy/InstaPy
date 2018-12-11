from .util import web_address_navigator
from .util import get_relationship_counts
from .util import getUserData
from .util import get_database
#from .commenters_util import get_photo_urls_from_profile

from datetime import datetime
import sqlite3



def saveStatistics(browser, username, logger):

    followers_count, following_count = get_relationship_counts(browser, username, logger)
    web_address_navigator(browser, "https://www.instagram.com/"+ username +"/")
    number_of_posts = getUserData("graphql.user.edge_owner_to_timeline_media.count", browser)
    logger.info(" Stats: Followercount > " + str(followers_count) + " Following > " + str(following_count) + " posts: " + str(number_of_posts))
    date = datetime.today()

    try:
        # get a DB and start a connection
        db, id = get_database()
        conn = sqlite3.connect(db)

        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("INSERT INTO accountStatistics (profile_id, follower_count, follow_count, post_count, created) VALUES (?, ?, ?, ?, ?)",
                        (id, followers_count, following_count, number_of_posts, date))

    except Exception as exc:
        logger.error("Dap! Error occurred with Account Statistics:\n\t{}".format(str(exc).encode("utf-8")))

    finally:
        if conn:
            # close the open connection
            conn.close()


#work in progress
#def saveEngagementRate(browser, username, logger, post_count):
    #photo_urls = get_photo_urls_from_profile(browser, username, post_count, False)
