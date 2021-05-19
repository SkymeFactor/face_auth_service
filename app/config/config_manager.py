"""
"""
import json

class JSONDataWrapper():
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)
    
    # In case of non-existent attributes will return None
    def __getattr__(self, attribute: str):
        return None


class ConfigLoader():
    def loadJSON(self, filename: str):
        json_data = json.load(open(filename, 'r'), object_hook=JSONDataWrapper)
        return json_data
