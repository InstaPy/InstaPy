from sqlalchemy import Column, String

from instapy.database.model.base import Base, BasicEntity


class Profile(BasicEntity, Base):
    __tablename__ = 'profiles'
    name = Column(String(50), nullable=False)

    def __init__(self, name):
        self.name = name

