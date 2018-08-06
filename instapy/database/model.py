from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship

Base = declarative_base()


class BasicEntity:
    id = Column(Integer, primary_key=True)


class HasProfile(object):
    @declared_attr
    def profile_id(cls):
        return Column(Integer, ForeignKey('profiles.id'))

    @declared_attr
    def profile(cls):
        return relationship("Profile")


class FollowRestriction(BasicEntity, HasProfile, Base):
    __tablename__ = 'followRestriction'
    username = Column(String(50), nullable=False)
    times = Column(Integer, nullable=False)


class RecordActivity(BasicEntity, HasProfile, Base):
    __tablename__ = 'recordActivity'
    likes = Column(Integer, nullable=False)
    comments = Column(Integer, nullable=False)
    follows = Column(Integer, nullable=False)
    unfollows = Column(Integer, nullable=False)
    server_calls = Column(Integer, nullable=False)
    created = Column(Date, nullable=False)

    def __init__(self, profile_id):
        self.likes = 0
        self.comments = 0
        self.follows = 0
        self.unfollows = 0
        self.server_calls = 0
        self.created = datetime.today()
        self.profile_id = profile_id


class Profile(BasicEntity, Base):
    __tablename__ = 'profiles'
    name = Column(String(50), nullable=False)

    def __init__(self, name):
        self.name = name
