from sqlalchemy.orm import sessionmaker, scoped_session

from instapy.database.dao.profile_dao import ProfileDAO
from instapy.database.engine.database import Database
from instapy.database.model.base import Base
from instapy.database.model.profile import Profile
from .settings import Settings


def get_database():
    _id = Settings.profile["id"]
    address = Settings.database_location
    return address, _id


def initialize_database():
    Database(Settings.database_location)
    Base.metadata.create_all(Database.instance.engine)


def set_up_profile():
    profile_dao = ProfileDAO(Database.instance)
    profile = profile_dao.get_profile_by_name(Settings.profile['name'])
    if profile is None:
        profile = profile_dao.insert(Profile(Settings.profile['name']))

    Settings.update_settings_with_profile(profile)

