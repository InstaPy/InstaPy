"""Module only used to log the number of followers to a file"""
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
import os
import sqlite3
import sys

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
        with open('./logs/' + login + '_followedPool.csv', 'a+') as followPool:
            followPool.write(followed + ",\n")
    except BaseException as e:
        print("log_followed_pool error \n", str(e))

def log_likes(self, insta_name, link):
    """Saves this like in sqlite-db"""
    conn = sqlite3.connect(self.db_path)
    cur = conn.cursor()
    cur.execute(''' INSERT INTO likes(liked, insta_user, insta_name, link) VALUES(datetime('now'),?,?,?) ''', (self.username,insta_name,link,) )
    conn.commit()
    check_likes(self)

def check_likes(self):
    """check likes in sqlite-db"""
    conn = sqlite3.connect(self.db_path)
    cur = conn.cursor()
    #-- check daily limit
    likes = cur.execute("SELECT COUNT(*) counting FROM likes WHERE insta_user = '"+ self.username +"' AND date(liked) = date('now')").fetchone()
    print likes[0]
    print self.limit_likes_daily
    if int(likes[0]) > int(self.limit_likes_daily):
        print "Enough likes for today - EXIT"
        self.aborting = True
    #-- check hourly limit
    likes = cur.execute("SELECT COUNT(*) counting FROM likes WHERE insta_user = '"+ self.username +"' AND date(liked) = date('now') AND strftime('%H','now') = strftime('%H', liked)").fetchone()
    print likes[0]
    print self.limit_likes_hourly
    if int(likes[0]) > int(self.limit_likes_hourly):
        print "Enough likes for the hour - EXIT"
        self.aborting = True

def log_comments(self, insta_name, link, comment=""):
    """Saves this comment in sqlite-db"""
    conn = sqlite3.connect(self.db_path)
    cur = conn.cursor()
    cur.execute(''' INSERT INTO comments(commented, insta_user, insta_name, link, comment) VALUES(datetime('now'),?,?,?,?) ''', (self.username,insta_name,link,comment,) )
    conn.commit()
    #check_comments(self)

def init_log_writer(self):
    """Initialize instapy db"""
    self.db_path = './db/instapy_' + self.username + '.db'
    db_is_new = not os.path.exists(self.db_path)
    conn = sqlite3.connect(self.db_path)
    with open('./db/instapy.schema', 'rt') as f:
        schema = f.read()
    conn.executescript(schema)
    check_likes(self)
