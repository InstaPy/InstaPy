import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings:
    log_location = os.path.join(BASE_DIR, 'logs')
    database_location = os.path.join(BASE_DIR, 'db', 'instapy.db')
    chromedriver_location = os.path.join(BASE_DIR, 'assets', 'chromedriver')
    log_profile_statistic = True
