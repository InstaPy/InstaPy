import os

from instapy.database.dao import ProfileDAO
from instapy.database.engine import Database
from instapy.database.model import Profile, Base
from .settings import Settings


def get_database():
    _id = Settings.profile["id"]
    address = Settings.database_location
    return address, _id


def initialize_database():
    address = Settings.database_location
    create_database_directories(address)
    Database(address)
    Base.metadata.create_all(bind=Database.instance.engine)


def set_up_profile():
    profile_dao = ProfileDAO(Database.instance)
    profile = profile_dao.get_profile_by_name(Settings.profile['name'])
    if profile is None:
        profile = profile_dao.insert(Profile(Settings.profile['name']))

    Settings.update_settings_with_profile(profile)


def create_database_directories(address):
    db_dir = os.path.dirname(address)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
