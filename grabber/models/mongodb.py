from pymongo import MongoClient
from json import loads as jsonsload

DATABASE=MongoDB

class MongoDB(object):
    """
    The monogdb access implementation.
    """
    def __init__(self, connection_string):
        """
        Sets up connection to mongo database.
        :param connection_string: the string (as a json type in this
        case) that represents how to connect to the database server
        """
        connection_dict=jsonsload(connection_string)
        self.client = MongoClient(**connection_dict)
        self.database = self.client(connection_dict['database'])
        
    def get_item(self, collection, id):
        """
        Retrieve an item from the database.
        :param collection:the type of data to retrieve
        :param id:the unique identifier of the item to retrieve
        """
        pass
        
    def get_items(self, collection, **filters):
        """
        Similar to `get_item` but it returns more than one item and can
        also have a filter applied to specify the data to return
        :param collection:the type of data to retrieve
        :param filters:a dict of data to filter on.
        """
        pass
        
    def add_item(self, collection, data):
        """
        Adds data to the database.
        :param collection:the type of data to retrieve
        :param data:the data to add to the database.
        """
        pass
        
    def add_items(self, collection, data):
        """
        Similar to `add_item` but uses an array to do a bulk write.
        :param collection:the type of data to retrieve
        :param data:an array of data to write.
        """
        self.add_item(collection, data)
