""" Global variables """
import os
from sys import platform as p_os
import platform



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OS_ENV = "windows" if p_os=="win32" else "osx" if p_os=="darwin" else "linux"



class Settings:
    """ Globally accessible settings throughout whole project """
    log_location = os.path.join(BASE_DIR, 'logs')
    database_location = os.path.join(BASE_DIR, 'db', 'instapy.db')
    assets_location = os.path.join(BASE_DIR, "assets")

    # chromedriver file
    specific_chromedriver = "chromedriver"
    if platform.system() == "Windows":
        specific_chromedriver += ".exe"

    chromedriver_location = os.path.join(BASE_DIR, "assets", specific_chromedriver)
    # fallback, could be deleted
    if not os.path.exists(chromedriver_location):
        chromedriver_location = "chromedriver"

    chromedriver_desired_version = "latest"

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



