from datetime import datetime

from sqlalchemy.orm import Session

from instapy.database.model import RecordActivity, Profile


class DAO:
    def __init__(self, database):
        self.database = database

    def get_session(self):
        return Session(self.database.engine)


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


class RecordActivityDAO(DAO):

    def __init__(self, database):
        super(RecordActivityDAO, self).__init__(database)

    def insert(self, record_activity):
        session = self.get_session()
        session.add(record_activity)
        session.commit()
        return record_activity

    def update(self, record_activity):
        record_activity.created = datetime.utcnow()
        session = self.get_session()
        session.merge(record_activity)
        session.commit()
        return record_activity

    def get_by_profile_id_and_created_today(self, profile_id):
        session = self.get_session()
        return session.query(RecordActivity)\
            .filter(RecordActivity.profile_id == profile_id)\
            .filter(RecordActivity.created == datetime.utcnow().date())\
            .first()

    def get_by_profile_id(self, profile_id):
        session = self.get_session()
        return session.query(RecordActivity)\
            .filter(RecordActivity.profile_id == profile_id)\
            .all()
