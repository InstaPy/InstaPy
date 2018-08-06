from sqlalchemy import create_engine


class Database:

    class __Database:
        def __init__(self, address):
            self.__address = address
            self.engine = create_engine("sqlite:///%s" % address, echo=False)  # change to True to debug

        def __str__(self):
            return repr(self) + self.__address

    instance = None

    def __new__(cls, address):
        if not Database.instance:
            Database.instance = Database.__Database(address)
        return Database.instance
