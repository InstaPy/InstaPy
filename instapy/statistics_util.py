from .util import web_address_navigator
from .util import get_relationship_counts
from .util import getUserData
from .util import get_database
from .commenters_util import get_photo_urls_from_profile
from datetime import datetime
import sqlite3



def save_statistics(browser, username, logger, save_engagement=True, amount=5):
    save_account_statistics(browser, username, logger)

    if save_engagement == True:
        save_engagement_rate(browser, username, logger, amount)




def save_account_statistics(browser, username, logger):

    # get a DB and start a connection
    db, id = get_database()
    conn = sqlite3.connect(db)

    try:

        followers_count, following_count = get_relationship_counts(browser, username, logger)
        web_address_navigator(browser, "https://www.instagram.com/"+ username +"/")
        number_of_posts = getUserData("graphql.user.edge_owner_to_timeline_media.count", browser)
        logger.info(" Stats: Followercount > " + str(followers_count) + " Following > " + str(following_count) + " posts: " + str(number_of_posts))

        date = datetime.today()




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



def save_engagement_rate(browser, username, logger, post_count = 5):

    db, id = get_database()
    conn = sqlite3.connect(db)

    try:

        followers_count, following_count = get_relationship_counts(browser, username, logger)
        photo_urls = get_photo_urls_from_profile(browser, username, post_count, False)

        rate = 0

        for url in photo_urls:
            web_address_navigator(browser, url)

            #TODO: Not Working Xpath not found for some unknown reason
            try:
                #xpatch changes depending on the nummber of likes
                elem = browser.find_element_by_xpath("//section/div/div/button/span/")
                likes = elem.get_attribute("innerHTML")

            except Exception as ex1:

                logger.warn(ex1)
                logger.info("Adapt, improvise, overcome. (trying other xpath)")


                try:
                    elem = browser.find_element_by_xpath("//section/div/div/a/")
                    likes = elem.get_attribute("innerHTML")

                    likes = likes.split(" ")[0]  # remove text --> now only nummber
                    likes = likes.replace("<span>", "")
                    likes = likes.replace("</span>", "")
                    likes = likes.replace(" ", "")

                except Exception as ex2:
                    raise ex2

            logger.info(likes)
            rate = rate + (int(likes) / int(followers_count))

        rate = round(rate / int(len(photo_urls)), 2)

        date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(" Stats: Average Engagementrate for the last " + str(post_count) + " Posts: " + str(rate) + "%")
        #Save to DB
        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO postStatistics(profile_id, avg_engagement, analysed_posts_urls, analysed_posts_count, created) VALUES (?, ?, ?, ?, ?)",
                (id, rate, ",".join(photo_urls), post_count, date))

    except Exception as exc:
        logger.error("Dap! Error occurred with Post Statistics:\n\t{}".format(str(exc).encode("utf-8")))

    finally:
        if conn:
            # close the open connection
            conn.close()

