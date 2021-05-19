from .iconnection import IConnection
import pymongo

class MongoDBConnection(IConnection):
    def __init__(self, mongo_server_uri: str, database: str, collection: str):
        self.client = pymongo.MongoClient(mongo_server_uri)
        self.connection = self.client[database][collection]
    
    # Create data
    def insert(self, data: dict):
        _id = self.connection.insert_one(data)
        return _id

    # Read data
    def find(self, query: dict):
        '''
        returns: (list) Array of dictionaries containing requested data.
        '''
        data = [obj for obj in self.connection.find(query)]
        return data

    # Update data
    def update(self, query: dict, data: dict):
        _num = self.connection.update_many(query, data)
        return _num
    
    # Delete data
    def delete(self, query: dict):
        _num = self.connection.delete_many(query)
        return _num

