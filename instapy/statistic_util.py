import csv
import datetime
import os
import re
import sqlite3

from .settings import Settings


class Profilestatistic:

    def log_statistic_user_follower(username, follower):
        conn = sqlite3.connect(Settings.database_location)
        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # Upgrade schema
            try:
                cur.execute('SELECT * FROM profile_statistics LIMIT 1;')
            except:
                # table not exists
                cur.execute("CREATE TABLE profile_statistics (username TEXT,follower INTEGER,created datetime);")
                pass

            cur.execute("SELECT * FROM profile_statistics WHERE created == date('now') AND username == ?", (username,))
            data = cur.fetchone()
            if data is None:
                # create a new record for the new day
                cur.execute("INSERT INTO profile_statistics (username,follower,created) VALUES (?,?, date('now'))", [username, follower])
            else:
                sql = ("UPDATE profile_statistics set follower = ?"
                       "WHERE created == date('now') AND username == ?")
                cur.execute(sql, [follower,username])
                # commit
            conn.commit()
