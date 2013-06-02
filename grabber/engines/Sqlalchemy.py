from engines.base import BaseDB
from models.model import Feed, Entry
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class SqlalchemyDB(BaseDB):
    """
    The SQLAlchemy access implementation.
    """
    
    def setup_database(self):
        Base.metadata.create_all(self.engine)
    
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        Session = sessionmaker(self.engine)
        self.session = Session()
        
    def get_item(self, table, id=None, **filters):
        table = table_converter(table)
        if id:
            filters = {'id': id}
        return session.query(table).filter_by(**filters).first().__dict__.values()
        
    def get_items(self, table, **filters):
        table = table_converter(table)
        rv =  map(lambda item: item.__dict__.values(), self.session.query(table).filter_by(**filters).all())
        return rv
        
    def add_item(self, table, data):
        item_orm = table_converter(table, data)
        self.session.add(item_orm)
        self.session.commit()
        
    def remove_item(self, table, id=None, **filters):
        item = self.get_item(table, id, **filters)
        self.session.delete(item)
        
def table_converter(table, data=None):
    """
    Works out what model to use for the table and sorts out the data
    :param table:the table name
    :param data:the data item to enter in to the database
    """
    if table == SQLAFeed.TYPE:
        if data:
            return SQLAFeed(*data.to_database().values())
        else:
            return SQLAFeed
    elif table == SQLAEntry.TYPE:
        if data:
            return SQLAEntry(*data.to_database().values())
        else:
            return SQLAEntry
    else:
        raise Exception("Table type not found")
    

class SQLAFeed(Base, Feed):
    __tablename__ = Feed.TYPE
    
    id = Column(String, primary_key=True)
    url = Column(String)
    title = Column(String)
    subtitle = Column(String)
    updated = Column(DateTime(timezone=True))
    published = Column(DateTime(timezone=True))
    link = Column(String)
    last_accessed = Column(DateTime(timezone=True))
    minimum_wait = Column(Integer)
    errors = Column(Integer)

class SQLAEntry(Base, Entry):
    __tablename__ = Entry.TYPE
    
    id = Column(String, primary_key=True)
    feed_id = Column(String) # needs relationship setting up
    title=Column(String)
    summary=Column(String)
    link=Column(String)
    updated=Column(DateTime(timezone=True))
    published=Column(DateTime(timezone=True))

DATABASE=SqlalchemyDB
