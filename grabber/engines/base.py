from models.model import Feed, Entry

class BaseDB(object):
    """
    The base implementation of the database interface.
    """
    
    TABLES = [
        Feed,
        Entry
    ]
    
    def __init__(self, connection_string):
        """
        Sets up connection to mongo database.
        :param connection_string: the string (as a json type in this
        case) that represents how to connect to the database server
        """
        raise NotImplementedError()
        
    def setup_database(self):
        """
        Sets up database tables if need be.
        """
        raise NotImplementedError()
        
    def get_item(self, collection, id=None, **filters):
        """
        Retrieve an item from the database.
        :param collection:the type of data to retrieve
        :param id:the unique identifier of the item to retrieve
        :param filters:a dictionary of items to match on.
        """
        raise NotImplementedError()
        
    def get_items(self, collection, **filters):
        """
        Similar to `get_item` but it returns more than one item and can
        also have a filter applied to specify the data to return
        :param collection:the type of data to retrieve
        :param id:the unique identifier of the item to retrieve
        :param filters:a dictionary of items to match on.
        """
        raise NotImplementedError()
        
    def add_item(self, collection, data):
        """
        Adds data to the database.
        :param collection:the type of data to retrieve
        :param data:the data to add to the database.
        """
        raise NotImplementedError()
        
    def remove_item(self, collection, id=None, **filters):
        """
        Delete items from collection.
        :param collection:the type of data to select
        :param id:the unique identifier of the item to retrieve
        :param filters:a dictionary of items to match on.
        """
        raise NotImplementedError()

DATABASE=BaseDB
