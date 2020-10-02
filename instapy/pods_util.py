import requests
import sqlite3
from .settings import Settings
from .database_engine import get_database


def get_server_endpoint(topic):
    if topic == "fashion":
        return Settings.pods_fashion_server_endpoint
    elif topic == "food":
        return Settings.pods_food_server_endpoint
    elif topic == "travel":
        return Settings.pods_travel_server_endpoint
    elif topic == "sports":
        return Settings.pods_sports_server_endpoint
    elif topic == "entertainment":
        return Settings.pods_entertainment_server_endpoint
    else:
        return Settings.pods_server_endpoint


def get_recent_posts_from_pods(topic, logger):
    """ fetches all recent posts shared with pods """
    params = {"topic": topic}
    r = requests.get(get_server_endpoint(topic) + "/getRecentPostsV1", params=params)
    try:
        logger.info("Downloaded postids from Pod {}:".format(topic))
        if r.status_code == 200:
            logger.info(r.json())
            return r.json()
        else:
            logger.error(r.text)
            return []
    except Exception as err:
        logger.error("Could not get postids from pod {} - {}".format(topic, err))
        return []


def group_posts(posts, logger):
    no_comments_post_ids = []
    light_post_ids = []
    normal_post_ids = []
    heavy_post_ids = []
    for postobj in posts:
        try:
            if postobj["mode"] == "no_comments":
                no_comments_post_ids.append(postobj)
            elif postobj["mode"] == "light":
                light_post_ids.append(postobj)
            elif postobj["mode"] == "heavy":
                heavy_post_ids.append(postobj)
            else:
                normal_post_ids.append(postobj)
        except Exception as err:
            logger.error(
                "Failed with Error {}, please upgrade your instapy".format(err)
            )
            normal_post_ids.append(postobj)
    return no_comments_post_ids, light_post_ids, normal_post_ids, heavy_post_ids


def share_my_post_with_pods(postid, topic, engagement_mode, logger):
    """ share_my_post_with_pod """
    params = {"postid": postid, "topic": topic, "mode": engagement_mode}
    r = requests.get(get_server_endpoint(topic) + "/publishMyLatestPost", params=params)
    try:
        logger.info("Publishing to Pods {}".format(postid))
        if r.status_code == 200:
            logger.info(r.text)
            return True
        else:
            logger.error(r.text)
            return False
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
                {"id_var": id, "name_var": postid},
            )
            data = cur.fetchone()
            share_data = dict(data) if data else None

            if operation == "write":
                if share_data is None:
                    # write a new record
                    cur.execute(
                        "INSERT INTO shareWithPodsRestriction (profile_id, "
                        "postid, times) VALUES (?, ?, ?)",
                        (id, postid, 1),
                    )
                else:
                    # update the existing record
                    share_data["times"] += 1
                    sql = (
                        "UPDATE shareWithPodsRestriction set times = ? WHERE "
                        "profile_id=? AND postid = ?"
                    )
                    cur.execute(sql, (share_data["times"], id, postid))

                # commit the latest changes
                conn.commit()

            elif operation == "read":
                if share_data is None:
                    return False

                elif share_data["times"] < limit:
                    return False

                else:
                    exceed_msg = "" if share_data["times"] == limit else "more than "
                    logger.info(
                        "---> {} has already been shared with pods {}{} times".format(
                            postid, exceed_msg, str(limit)
                        )
                    )
                    return True

    except Exception as exc:
        logger.error(
            "Dap! Error occurred with share Restriction:\n\t{}".format(
                str(exc).encode("utf-8")
            )
        )

    finally:
        if conn:
            # close the open connection
            conn.close()


def comment_restriction(operation, postid, limit, logger):
    """ Keep track of already shared posts """
    try:
        # get a DB and start a connection
        db, id = get_database()
        conn = sqlite3.connect(db)

        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(
                "SELECT * FROM commentRestriction WHERE profile_id=:id_var "
                "AND postid=:name_var",
                {"id_var": id, "name_var": postid},
            )
            data = cur.fetchone()
            share_data = dict(data) if data else None

            if operation == "write":
                if share_data is None:
                    # write a new record
                    cur.execute(
                        "INSERT INTO commentRestriction (profile_id, "
                        "postid, times) VALUES (?, ?, ?)",
                        (id, postid, 1),
                    )
                else:
                    # update the existing record
                    share_data["times"] += 1
                    sql = (
                        "UPDATE commentRestriction set times = ? WHERE "
                        "profile_id=? AND postid = ?"
                    )
                    cur.execute(sql, (share_data["times"], id, postid))

                # commit the latest changes
                conn.commit()

            elif operation == "read":
                if share_data is None:
                    return False

                elif share_data["times"] < limit:
                    return False

                else:
                    exceed_msg = "" if share_data["times"] == limit else "more than "
                    logger.info(
                        "---> {} has been commented on {}{} times".format(
                            postid, exceed_msg, str(limit)
                        )
                    )
                    return True

    except Exception as exc:
        logger.error(
            "Dap! Error occurred with comment Restriction:\n\t{}".format(
                str(exc).encode("utf-8")
            )
        )

    finally:
        if conn:
            # close the open connection
            conn.close()
