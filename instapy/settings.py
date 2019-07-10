"""
Global variables

By design, import no any other local module inside this file.
Vice verse, it'd produce circular dependent imports.
"""

from sys import platform
from os import environ as environmental_variables
from os.path import join as join_path
from os.path import exists as path_exists

from .xpath import read_xpath
from .event import Event


WORKSPACE = {"name": "InstaPy",
             "path": environmental_variables.get("INSTAPY_WORKSPACE")}
OS_ENV = ("windows" if platform == "win32"
          else "osx" if platform == "darwin"
          else "linux")


def localize_path(*args):
    """ Join given locations as an OS path """

    if WORKSPACE["path"]:
        path = join_path(WORKSPACE["path"], *args)
        return path

    else:
        return None


class Settings:
    """ Globally accessible settings throughout whole project """

    # locations
    log_location = localize_path("logs")
    database_location = localize_path("db", "instapy.db")
    specific_chromedriver = "chromedriver_{}".format(OS_ENV)
    chromedriver_location = localize_path("assets", specific_chromedriver)
    if (not chromedriver_location
            or not path_exists(chromedriver_location)):
        chromedriver_location = localize_path("assets", "chromedriver")

    # minimum supported version of chromedriver
    chromedriver_min_version = 2.36

    # set a logger cache outside the InstaPy object to avoid
    # re-instantiation issues
    loggers = {}
    logger = None

    # set current profile credentials for DB operations
    profile = {"id": None, "name": None}

    # hold live Quota Supervisor configuration for global usage
    QS_config = {}

    # specify either connected locally or through a proxy
    connection_type = None

    # store user-defined delay time to sleep after doing actions
    action_delays = {}

    # store configuration of text analytics
    meaningcloud_config = {}
    yandex_config = {}

    # store the parameter for global access
    show_logs = None

    # store what browser the user is using, if they are using firefox it is
    # true, chrome if false.
    use_firefox = None

    #inluxdb Settings
    host_influx = None
    port_influx = None
    user_influx = None
    password_influx = None
    db_influx  = None

    # state of instantiation of InstaPy
    InstaPy_is_running = False

    # This is where currently the pods server is hosted
    pods_server_endpoint = 'https://us-central1-instapy-pods.cloudfunctions.net'


class Storage:
    """ Globally accessible standalone storage """

    # store realtime record activity data
    record_activity = {}


class Selectors:
    """
    Store XPath, CSS, and other element selectors to be used at many places
    """

    likes_dialog_body_xpath = (
        read_xpath("class_selectors","likes_dialog_body_xpath"))
    likes_dialog_close_xpath = read_xpath("class_selectors", "likes_dialog_close_xpath")



class InfluxDBLog:
    """ InfluxDB Singleton Class """
    singleton = None
    client_influxDB = None

    def __new__(cls, *args, **kwargs):
        if not cls.singleton:
            cls.singleton = object.__new__(InfluxDBLog)
        return cls.singleton

    def __init__(self):
        if (self.client_influxDB or
                not Settings.host_influx or
                not Settings.port_influx or
                not Settings.user_influx or
                not Settings.password_influx or
                not Settings.db_influx
            ): return

        try:
            # only import when needed
            from influxdb import InfluxDBClient

            self.client_influxDB = InfluxDBClient(host = Settings.host_influx,
                                                    port = Settings.port_influx,
                                                    username = Settings.user_influx,
                                                    password = Settings.password_influx,
                                                    database = Settings.db_influx)
            self.client_influxDB.switch_database(Settings.db_influx)

            version = self.client_influxDB.ping()
            print('Using InfluxDB version: ' + str(version))
            self.register_callbacks()
        except Exception as e:
            self.client_influxDB = None
            print('Error connecting to InfluxDB!: ', str(e))
            # TODO throw some exception ?

    def addEntry(self, measurement, tag_name, tag_value, field1_name, field1_value, field2_name, field2_value):
        tags = {
            tag_name: tag_value
        }
        fields = {
            field1_name: field1_value,
            field2_name: field2_value
        }
        self.add(measurement, tags, fields)

    def add(self, measurement, tags, fields):
        if not self.client_influxDB: return

        json_body = [{
                "measurement": measurement,
                "tags": tags,
                "fields": fields
            }]
        self.client_influxDB.write_points(json_body)

    def switchDatabase(self, database):
        if not self.client_influxDB: return

        self.client_influxDB.switch_database(database)
        Settings.db_influx = database

    def register_callbacks(self):
        event = Event()
        event.add_callback(event.profile_data_updated.__name__, self.update_profile_data);

    def update_profile_data(self, username, followers_count, following_count):
        fields = {
            'followers_count': followers_count,
            'following_count': following_count
        }
        self.add('profile', { 'username': username }, fields)
