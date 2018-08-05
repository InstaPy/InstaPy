from sqlalchemy import Column, Integer, DateTime

from instapy.database.model.base import HasProfileIdAsPK, Base


class RecordActivity(Base, HasProfileIdAsPK):
    __tablename__ = 'recordActivity'
    likes = Column(Integer, nullable=False)
    comments = Column(Integer, nullable=False)
    follows = Column(Integer, nullable=False)
    unfollows = Column(Integer, nullable=False)
    server_calls = Column(Integer, nullable=False)
    created = Column(DateTime, nullable=False)

