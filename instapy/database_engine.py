import os
import sqlite3

from .settings import Settings

SELECT_FROM_PROFILE_WHERE_NAME = "SELECT * FROM profiles WHERE name = :name"
INSERT_INTO_PROFILE = "INSERT INTO profiles (name) VALUES (?)"
SQL_CREATE_PROFILE_TABLE = """CREATE TABLE IF NOT EXISTS `profiles` (
                  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                  `name` TEXT NOT NULL);"""
SQL_CREATE_RECORD_ACTIVITY_TABLE = """CREATE TABLE IF NOT EXISTS `recordActivity` (
                  `profile_id` INTEGER REFERENCES `profiles` (id),
                  `likes` SMALLINT UNSIGNED NOT NULL,
                  `comments` SMALLINT UNSIGNED NOT NULL,
                  `follows` SMALLINT UNSIGNED NOT NULL,
                  `unfollows` SMALLINT UNSIGNED NOT NULL,
                  `server_calls` INT UNSIGNED NOT NULL,
                  `created` DATETIME NOT NULL);"""
SQL_CREATE_FOLLOW_RESTRICTION_TABLE = """CREATE TABLE IF NOT EXISTS `followRestriction` (
                  `profile_id` INTEGER REFERENCES `profiles` (id),
                  `username` TEXT NOT NULL,
                  `times` TINYINT UNSIGNED NOT NULL);"""


def get_database():
    _id = Settings.profile["id"]
    address = Settings.database_location
    return address, _id


def initialize_database():
    logger = Settings.logger
    name = Settings.profile['name']
    address = validate_database_file_address()
    create_database_directories(address)
    create_database(address, logger, name)
    update_profile_settings(name, address, logger)


def create_database(address, logger, name):
    if not os.path.isfile(address):
        try:
            connection = sqlite3.connect(address)
            with connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()

                create_profiles_table(cursor)
                create_record_activity_table(cursor)
                create_follow_restriction_table(cursor)

                connection.commit()

        except Exception as exc:
            logger.warning(
                "Wah! Error occured while getting a DB for '{}':\n\t{}".format(name, str(exc).encode("utf-8")))

        finally:
            if connection:
                # close the open connection
                connection.close()


def create_follow_restriction_table(cursor):
    cursor.execute(SQL_CREATE_FOLLOW_RESTRICTION_TABLE)


def create_record_activity_table(cursor):
    cursor.execute(SQL_CREATE_RECORD_ACTIVITY_TABLE)


def create_profiles_table(cursor):
    cursor.execute(SQL_CREATE_PROFILE_TABLE)


def create_database_directories(address):
    db_dir = os.path.dirname(address)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)


def validate_database_file_address():
    address = Settings.database_location
    if not address.endswith(".db"):
        slash = "\\" if "\\" in address else "/"
        address = address if address.endswith(slash) else address + slash
        address += "instapy.db"
        Settings.database_location = address
    return address


def update_profile_settings(name, address, logger):
    try:
        conn = sqlite3.connect(address)
        with conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            profile = select_profile_by_username(cursor, name)

            if profile is None:
                profile = insert_profile(conn, cursor, name)

            Settings.update_settings_with_profile(dict(profile))

    except Exception as exc:
        logger.warning("Heeh! Error occured while getting a DB profile for '{}':\n\t{}".format(name, str(exc).encode("utf-8")))

    finally:
        if conn:
            # close the open connection
            conn.close()


def insert_profile(conn, cursor, name):
    cursor.execute(INSERT_INTO_PROFILE, (name,))
    # commit the latest changes
    conn.commit()
    # reselect the table after adding data to get the proper `id`
    profile = select_profile_by_username(cursor, name)
    return profile


def select_profile_by_username(cursor, name):
    cursor.execute(SELECT_FROM_PROFILE_WHERE_NAME, {"name": name})
    profile = cursor.fetchone()
    return profile



