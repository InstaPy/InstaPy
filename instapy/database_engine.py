import os
import sqlite3

from .settings import Settings
from .time_util import sleep


def get_db(make=False):
    """ Get a database and required tables at request """
    address = Settings.database_location
    logger = Settings.logger
    credentials = Settings.profile
    # get existing profile credentials
    id, name = credentials.values()
    # make sure the address points to a database file
    if not address.endswith(".db"):
        slash = "\\" if "\\" in address else "/"
        address = address if address.endswith(slash) else address+slash
        address += "instapy.db"
        Settings.database_location = address
    # make the given path if not exists
    db_dir = os.path.dirname(address)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    make = True if not os.path.isfile(address) else make

    if make == True:
        try:
            conn = sqlite3.connect(address)
            with conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()

                #get 'profiles' table ready
                cur.execute("""
                CREATE TABLE IF NOT EXISTS `profiles` (
                  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                  `name` TEXT NOT NULL
                );
                            """)

                # get 'recordActivity`' table ready
                cur.execute("""
                CREATE TABLE IF NOT EXISTS `recordActivity` (
                  `profile_id` INTEGER REFERENCES `profiles` (id),
                  `likes` SMALLINT UNSIGNED NOT NULL,
                  `comments` SMALLINT UNSIGNED NOT NULL,
                  `follows` SMALLINT UNSIGNED NOT NULL,
                  `unfollows` SMALLINT UNSIGNED NOT NULL,
                  `server_calls` INT UNSIGNED NOT NULL,
                  `created` DATETIME NOT NULL
                  );
                            """)

                # get 'followRestriction' table ready
                cur.execute("""CREATE TABLE IF NOT EXISTS `followRestriction` (
                  `profile_id` INTEGER REFERENCES `profiles` (id),
                  `username` TEXT NOT NULL,
                  `times` TINYINT UNSIGNED NOT NULL
                  );
                            """)

                # commit the latest changes
                conn.commit()

        except Exception as exc:
            logger.warning("Wah! Error occured while getting a DB for '{}':\n\t{}".format(name, str(exc).encode("utf-8")))

        finally:
            if conn:
                # close the open connection
                conn.close()

    id = get_profile(name, address, logger) if (id is None or make==True) else id

    return address, id



def get_profile(name, address, logger):
    sleep(2)
    """ Get a profile for users and return its id """
    try:
        conn = sqlite3.connect(address)
        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # open a profile if not exists
            cur.execute("SELECT * FROM profiles WHERE name=:var", {"var":name})
            profile = cur.fetchone()

            if profile is None:
                cur.execute("INSERT INTO profiles (name) VALUES (?)", (name,))
                # commit the latest changes
                conn.commit()

                # reselect the table after adding data to get the proper `id`
                cur.execute("SELECT * FROM profiles WHERE name=:var", {"var":name})
                profile = cur.fetchone()

    except Exception as exc:
        logger.warning("Heeh! Error occured while getting a DB profile for '{}':\n\t{}".format(name, str(exc).encode("utf-8")))

    finally:
        if conn:
            # close the open connection
            conn.close()

    profile = dict(profile)
    id = profile["id"]

    # assign the id to its child in `Settings` class
    Settings.profile["id"] = id

    return id



