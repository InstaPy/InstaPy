""" Global variables """
import os
from sys import platform as p_os
from chromedriver_py import binary_path




BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OS_ENV = "windows" if p_os=="win32" else "osx" if p_os=="darwin" else "linux"



class Settings:
    """ Globally accessible settings throughout whole project """
    log_location = os.path.join(BASE_DIR, 'logs')
    database_location = os.path.join(BASE_DIR, 'db', 'instapy.db')
    specific_chromedriver = "chromedriver_{}".format(OS_ENV)
    chromedriver_location = os.path.join(BASE_DIR, "assets", specific_chromedriver)
    if not os.path.exists(chromedriver_location):
        chromedriver_location = binary_path 

    chromedriver_min_version = 2.36
    # set a logger cache outside the InstaPy object to avoid re-instantiation issues
    loggers = {}
    logger = None
    # set current profile credentials for DB operations
    profile = {"id":None, "name":None}
    # hold live Quota Supervisor configuration for global usage
    QS_config = {}
    # specify either connected locally or through a proxy
    connection_type = None



class Storage:
    """ Globally accessible standalone storage """
    # store realtime record activity data
    record_activity = {}



