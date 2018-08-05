from sqlalchemy.orm import Session

from instapy.database.dao import DAO
from instapy.database.model.profile import Profile


class ProfileDAO(DAO):

    def __init__(self, database):
        super(ProfileDAO, self).__init__(database)

    def insert(self, profile):
        session = self.get_session()
        session.add(profile)
        session.commit()
        return profile

    def get_profile_by_name(self, name):
        session = self.get_session()
        return session.query(Profile).filter(Profile.name == name).first()
