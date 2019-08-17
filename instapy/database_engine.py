import os
import sqlite3

from .settings import Settings

SELECT_FROM_PROFILE_WHERE_NAME = "SELECT * FROM profiles WHERE name = :name"

INSERT_INTO_PROFILE = "INSERT INTO profiles (name) VALUES (?)"

SQL_CREATE_PROFILE_TABLE = """
    CREATE TABLE IF NOT EXISTS `profiles` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `name` TEXT NOT NULL);"""

SQL_CREATE_RECORD_ACTIVITY_TABLE = """
    CREATE TABLE IF NOT EXISTS `recordActivity` (
        `profile_id` INTEGER REFERENCES `profiles` (id),
        `likes` SMALLINT UNSIGNED NOT NULL,
        `comments` SMALLINT UNSIGNED NOT NULL,
        `follows` SMALLINT UNSIGNED NOT NULL,
        `unfollows` SMALLINT UNSIGNED NOT NULL,
        `server_calls` INT UNSIGNED NOT NULL,
        `created` DATETIME NOT NULL);"""

SQL_CREATE_FOLLOW_RESTRICTION_TABLE = """
    CREATE TABLE IF NOT EXISTS `followRestriction` (
        `profile_id` INTEGER REFERENCES `profiles` (id),
        `username` TEXT NOT NULL,
        `times` TINYINT UNSIGNED NOT NULL);"""

SQL_CREATE_SHARE_WITH_PODS_RESTRICTION_TABLE = """
    CREATE TABLE IF NOT EXISTS `shareWithPodsRestriction` (
        `profile_id` INTEGER REFERENCES `profiles` (id),
        `postid` TEXT NOT NULL,
        `times` TINYINT UNSIGNED NOT NULL);"""

SQL_CREATE_COMMENT_RESTRICTION_TABLE = """
    CREATE TABLE IF NOT EXISTS `commentRestriction` (
        `profile_id` INTEGER REFERENCES `profiles` (id),
        `postid` TEXT NOT NULL,
        `times` TINYINT UNSIGNED NOT NULL);"""

SQL_CREATE_ACCOUNTS_PROGRESS_TABLE = """
    CREATE TABLE IF NOT EXISTS `accountsProgress` (
        `profile_id` INTEGER NOT NULL,
        `followers` INTEGER NOT NULL,
        `following` INTEGER NOT NULL,
        `total_posts` INTEGER NOT NULL,
        `created` DATETIME NOT NULL,
        `modified` DATETIME NOT NULL,
        CONSTRAINT `fk_accountsProgress_profiles1`
        FOREIGN KEY(`profile_id`) REFERENCES `profiles`(`id`));"""


def get_database(make=False):
    logger = Settings.logger
    credentials = Settings.profile

    profile_id, name = credentials["id"], credentials["name"]
    address = validate_database_address()

    if not os.path.isfile(address) or make:
        create_database(address, logger, name)

    profile_id = (
        get_profile(name, address, logger) if profile_id is None or make else profile_id
    )

    return address, profile_id


def create_database(address, logger, name):
    try:
        connection = sqlite3.connect(address)
        with connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()

            create_tables(
                cursor,
                [
                    "profiles",
                    "recordActivity",
                    "followRestriction",
                    "shareWithPodsRestriction",
                    "commentRestriction",
                    "accountsProgress",
                ],
            )

            connection.commit()

    except Exception as exc:
        logger.warning(
            "Wah! Error occurred while getting a DB for '{}':\n\t{}".format(
                name, str(exc).encode("utf-8")
            )
        )

    finally:
        if connection:
            # close the open connection
            connection.close()


def create_tables(cursor, tables):
    if "profiles" in tables:
        cursor.execute(SQL_CREATE_PROFILE_TABLE)

    if "recordActivity" in tables:
        cursor.execute(SQL_CREATE_RECORD_ACTIVITY_TABLE)

    if "followRestriction" in tables:
        cursor.execute(SQL_CREATE_FOLLOW_RESTRICTION_TABLE)

    if "shareWithPodsRestriction" in tables:
        cursor.execute(SQL_CREATE_SHARE_WITH_PODS_RESTRICTION_TABLE)

    if "commentRestriction" in tables:
        cursor.execute(SQL_CREATE_COMMENT_RESTRICTION_TABLE)

    if "accountsProgress" in tables:
        cursor.execute(SQL_CREATE_ACCOUNTS_PROGRESS_TABLE)


def verify_database_directories(address):
    db_dir = os.path.dirname(address)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)


def validate_database_address():
    address = Settings.database_location
    if not address.endswith(".db"):
        slash = "\\" if "\\" in address else "/"
        address = address if address.endswith(slash) else address + slash
        address += "instapy.db"
        Settings.database_location = address
    verify_database_directories(address)
    return address


def get_profile(name, address, logger):
    try:
        conn = sqlite3.connect(address)
        with conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            profile = select_profile_by_username(cursor, name)

            if profile is None:
                add_profile(conn, cursor, name)
                # reselect the table after adding data to get the proper `id`
                profile = select_profile_by_username(cursor, name)
    except Exception as exc:
        logger.warning(
            "Heeh! Error occurred while getting a DB profile for '{}':\n\t{}".format(
                name, str(exc).encode("utf-8")
            )
        )
    finally:
        if conn:
            # close the open connection
            conn.close()

    profile = dict(profile)
    profile_id = profile["id"]
    # assign the id to its child in `Settings` class
    Settings.profile["id"] = profile_id

    return profile_id


def add_profile(conn, cursor, name):
    cursor.execute(INSERT_INTO_PROFILE, (name,))
    # commit the latest changes
    conn.commit()


def select_profile_by_username(cursor, name):
    cursor.execute(SELECT_FROM_PROFILE_WHERE_NAME, {"name": name})
    profile = cursor.fetchone()

    return profile
