from sqlalchemy import Integer, Column, String

from instapy.database.model.base import Base, HasProfile, BasicEntity


class FollowRestriction(BasicEntity, HasProfile, Base):
    __tablename__ = 'followRestriction'
    username = Column(String(50), nullable=False)
    times = Column(Integer, nullable=False)
