from pymongo import MongoClient
from bson.objectid import ObjectId
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
        
    def get_item(self, collection, id=None, **filters):
        """
        Retrieve an item from the database.
        :param collection:the type of data to retrieve
        :param id:the unique identifier of the item to retrieve
        :param filters:a dictionary of items to match on.
        """
        if id:
            filters = {'_id': ObjectId(id)}
        return self.database[collection].find_one(filters)
        
    def get_items(self, collection, **filters):
        """
        Similar to `get_item` but it returns more than one item and can
        also have a filter applied to specify the data to return
        :param collection:the type of data to retrieve
        :param id:the unique identifier of the item to retrieve
        :param filters:a dictionary of items to match on.
        """
        return self.database[collection].find(filters)
        
    def add_item(self, collection, data):
        """
        Adds data to the database.
        :param collection:the type of data to retrieve
        :param data:the data to add to the database.
        """
        o_id = self.database[collection].insert(data)
        return str(o_id)
        
    def add_items(self, collection, data):
        """
        Similar to `add_item` but uses an array to do a bulk write.
        :param collection:the type of data to retrieve
        :param data:an array of data to write.
        """
        o_ids = self.database[collection].insert(data)
        return map(lambda o_id: str(o_id), o_ids)
        
    def remove_item(self, collection, id=None, **filters):
        """
        Delete items from collection.
        :param collection:the type of data to select
        :param id:the unique identifier of the item to retrieve
        :param filters:a dictionary of items to match on.
        """
        if id:
            filters = {'_id': ObjectId(id)}
        self.database[collection].remove(filters)
