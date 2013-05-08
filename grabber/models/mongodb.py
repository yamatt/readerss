from pymongo import MongoClient
from json import loads as jsonsload

DATABASE=MongoDB

class MongoDB(object):
    """
    
    """
    def __init__(self, connection_string):
        """
        
        """
        connection_dict=jsonsload(connection_string)
        self.client = MongoClient(**connection_dict)
        self.database = self.client(connection_dict['database'])
        
    def get_item(self, collection, id=None):
        """
        
        """
        pass
        
    def get_items(self, collection, **filters):
        """
        
        """
        pass
        
    def add_item(self, collection, data):
        """
        
        """
        pass
        
