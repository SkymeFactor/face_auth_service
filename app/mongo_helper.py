import pymongo
import sys

class Mongo(pymongo.MongoClient):
    def __init__(self, database, collection, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.database = self[database]
        self.collection = self.database[collection]

    def read_profiles(self, filter: str):
        pass
    
    def create_profile(self, username: str):
        pass

    def update_profile(self, username: str):
        self.collection.update_one({"username": username}, {"username": username})
    
    def delete_profile(self, username: str):
        self.collection.delete_one({"username": username})
    
    def get_user(self, username):
        return {
            '_id': 1,
            'username': 'user',
            'password': 'password',
            'client_id': 1,
            'client_secret': '0ac571b77820e75a93ff5c8e5d7b8df096421f31',
            'trusted_domain': 'http://192.168.0.13:8000'
        }