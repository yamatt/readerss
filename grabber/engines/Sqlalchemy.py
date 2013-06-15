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
        table = item_converter(table)
        if id:
            filters = {'id': id}
        return self.session.query(table).filter_by(**filters).first().__dict__
        
    def get_items(self, table, **filters):
        table = item_converter(table)
        rv =  map(lambda item: item.__dict__, self.session.query(table).filter_by(**filters).all())
        return rv
        
    def add_item(self, table, data):
        item_orm = item_converter(table, data)
        merged_item = self.session.merge(item_orm)
        self.session.add(merged_item)
        self.session.commit()
        
    def add_items(self, table, datas):
        items_orm = map(lambda item: item_converter(table, item), datas)
        merged_items = map(lambda item: self.session.merge(item), items_orm)
        for merged_item in merged_items:
            self.session.add(merged_item)
        self.session.commit()
        
    def remove_item(self, table, id=None, **filters):
        item = self.get_item(table, id, **filters)
        self.session.delete(item)
        
def item_converter(table, data=None):
    """
    Works out what model to use for the table and sorts out the data
    :param table:the table name
    :param data:the data item to enter in to the database
    """
    if table == SQLAFeed.TYPE:
        if data:
            return SQLAFeed(**data)
        else:
            return SQLAFeed
    elif table == SQLAEntry.TYPE:
        if data:
            return SQLAEntry(**data)
        else:
            return SQLAEntry
    else:
        raise Exception("Table type not found: {0}".format(table))
    

class SQLAFeed(Feed, Base):
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
    

class SQLAEntry(Entry, Base):
    __tablename__ = Entry.TYPE
    
    id = Column(String, primary_key=True)
    feed_id = Column(String, nullable=False) # needs relationship setting up
    title=Column(String)
    summary=Column(String)
    link=Column(String)
    updated=Column(DateTime(timezone=True))
    published=Column(DateTime(timezone=True))

DATABASE=SqlalchemyDB
