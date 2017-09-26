"""Module only used to log the number of followers to a file"""
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
import os
import sqlite3
import const

def log_follower_num(browser, username):
    """Prints and logs the current number of followers to
    a seperate file"""
    browser.get('https://www.instagram.com/' + username)

    followed_by = browser.execute_script("return window._sharedData.entry_data.ProfilePage[0].user.followed_by.count")

    with open('./logs/followerNum.txt', 'a') as numFile:
        numFile.write('{:%Y-%m-%d %H:%M} {}\n'.format(datetime.now(), followed_by or 0))


def log_followed_pool(login, followed):
    """Prints and logs the followed to
    a seperate file"""
    try:
        with open('./logs/' + login + '_followedPool.csv', 'a') as followPool:
            followPool.write(followed + ",\n")
    except BaseException as e:
        print("log_followed_pool error \n", str(e))

def log_likes(self, insta_name, link):
    """Saves this like in sqlite-db"""
    conn = sqlite3.connect('./db/instapy.db')
    cur = conn.cursor()
    cur.execute(''' INSERT INTO likes(liked, insta_user, insta_name, link) VALUES(date('now'),?,?,?) ''', (self.username,insta_name,link,) )
    conn.commit()
    likes = cur.execute("SELECT COUNT(*) counting FROM likes WHERE insta_user = '"+ self.username +"' AND liked = date('now')").fetchone()
    if likes[0] > self.limit_likes:
        print "Enough likes for today - EXIT"
        sys.exit(0)

def init_log_writer():
    """Initialize instapy db"""
    db_path = './db/instapy'
    db_is_new = not os.path.exists(db_path + '.db')
    conn = sqlite3.connect(db_path + '.db')
    if db_is_new:
        print('Creating schema in: ' + db_path + '.db')
        with open(db_path + '.schema', 'rt') as f:
            schema = f.read()
        conn.executescript(schema)
