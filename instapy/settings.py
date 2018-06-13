import os


#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#BASE_DIR="/home/instapy-log/"

BASE_DIR="/Users/cbardas/instapy-log/"


class Settings:
    log_location = os.path.join(BASE_DIR+'campaign', 'logs')
    database_location = os.path.join(BASE_DIR, 'db', 'instapy.db')
    chromedriver_location = os.path.join(BASE_DIR, 'assets', 'chromedriver')
    chromedriver_min_version = 2.36
    # Set a logger cache outside the InstaPy object to avoid re-instantiation issues
    loggers = {}
    logger = None
