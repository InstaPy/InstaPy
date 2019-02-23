import requests
import sqlite3
from .settings import Settings
from .database_engine import get_database

def get_recent_posts_from_pods(logger):
    """ fetches all recent posts shared with pods """
    params = {'category' : 'general'}
    r = requests.get(Settings.pods_server_endpoint + '/getRecentPosts', params=params)
    try:
        logger.info("Downloaded postids from Pods:")
        logger.info(r.json())
        return r.json()
    except Exception as err:
        logger.error(err)
        return None

def share_my_post_with_pods(postid, logger):
    """ share_my_post_with_pod """
    logger.info("Publishing to Pods {}".format(postid))
    params = {'postid' : postid, 'category' : 'general'}
    r = requests.get(Settings.pods_server_endpoint + '/publishMyLatestPost', params=params)
    try:
        logger.info(r)
        logger.info(r.json())
        return True
    except Exception as err:
        logger.error(err)
        return False

def share_with_pods_restriction(operation, postid, limit, logger):
    """ Keep track of already shared posts """
    try:
        # get a DB and start a connection
        db, id = get_database()
        conn = sqlite3.connect(db)

        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(
                "SELECT * FROM shareWithPodsRestriction WHERE profile_id=:id_var "
                "AND postid=:name_var",
                {"id_var": id, "name_var": postid})
            data = cur.fetchone()
            share_data = dict(data) if data else None

            if operation == "write":
                if share_data is None:
                    # write a new record
                    cur.execute(
                        "INSERT INTO shareWithPodsRestriction (profile_id, "
                        "postid, times) VALUES (?, ?, ?)",
                        (id, postid, 1))
                else:
                    # update the existing record
                    share_data["times"] += 1
                    sql = "UPDATE shareWithPodsRestriction set times = ? WHERE " \
                          "profile_id=? AND postid = ?"
                    cur.execute(sql, (share_data["times"], id, postid))

                # commit the latest changes
                conn.commit()

            elif operation == "read":
                if share_data is None:
                    return False

                elif share_data["times"] < limit:
                    return False

                else:
                    exceed_msg = "" if share_data[
                                           "times"] == limit else "more than "
                    logger.info("---> {} has already been shared with pods {}{} times"
                                .format(postid, exceed_msg, str(limit)))
                    return True

    except Exception as exc:
        logger.error(
            "Dap! Error occurred with share Restriction:\n\t{}".format(
                str(exc).encode("utf-8")))

    finally:
        if conn:
            # close the open connection
            conn.close()

