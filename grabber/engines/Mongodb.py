from engines.base import BaseDB
from pymongo import MongoClient
from bson.objectid import ObjectId
from json import loads as jsonsload

DATABASE=MongoDB

class MongoDB(BaseDB):
    """
    The monogdb access implementation.
    """
        
    def __init__(self, connection_string):
        connection_dict=jsonsload(connection_string)
        self.client = MongoClient(**connection_dict)
        self.database = self.client(connection_dict['database'])
    
    def setup_database(self):
        pass
        
    def get_item(self, collection, id=None, **filters):
        if id:
            filters = {'id': id}
        return self.database[collection].find_one(filters)
        
    def get_items(self, collection, **filters):
        return self.database[collection].find(filters)
        
    def add_item(self, collection, data):
        self.database[collection].insert(data.to_database())
        
    def remove_item(self, collection, id=None, **filters):
        if id:
            filters = {'id': id}
        self.database[collection].remove(filters)
