from instapy.database.dao.profile_dao import ProfileDAO
from instapy.database.engine.database import Database
from instapy.database_engine import initialize_database, set_up_profile

from instapy import Settings


def test_initialize_database():
    Settings.profile = {'id': None, 'name': 'myname'}
    Settings.database_location = ':memory:'

    initialize_database()

    dao = ProfileDAO(Database.instance)
    profile = dao.get_profile_by_name('myname')
    assert profile is None


def test_initialize_database_with_setup():
    Settings.profile = {'id': None, 'name': 'myname'}
    Settings.database_location = ':memory:'

    initialize_database()
    set_up_profile()

    dao = ProfileDAO(Database.instance)
    profile = dao.get_profile_by_name('myname')

    assert profile.id is 1
