from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship

Base = declarative_base()


class BasicEntity:
    id = Column(Integer, primary_key=True)


class HasProfileIdAsPK(object):
    @declared_attr
    def profile_id(cls):
        return Column(Integer, ForeignKey('profiles.id'), primary_key=True)

    @declared_attr
    def profile(cls):
        return relationship("Profile")


class HasProfile(object):
    @declared_attr
    def profile_id(cls):
        return Column(Integer, ForeignKey('profiles.id'))

    @declared_attr
    def profile(cls):
        return relationship("Profile")
