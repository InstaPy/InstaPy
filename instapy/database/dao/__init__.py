from sqlalchemy.orm import Session


class DAO:
    def __init__(self, database):
        self.database = database

    def get_session(self):
        return Session(self.database.engine)