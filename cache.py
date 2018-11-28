import requests
import json
from datetime import datetime

class Cache:
    def __init__(self, filename):
        """Load cache from disk, if present"""
        self.filename = filename
        try:
            with open(self.filename, 'r') as cache_file:
                cache_json = cache_file.read()
                self.cache_diction = json.loads(cache_json)
        except:
            self.cache_diction = {}

    def _save_to_disk(self):
        """Save cache to disk"""
        with open(self.filename, 'w') as cache_file:
            cache_json = json.dumps(self.cache_diction)
            cache_file.write(cache_json)

    def get(self, identifier):
        """If unique identifier exists in the cache, return the data associated with it, else return None"""
        identifier = identifier.upper() 
        if identifier in self.cache_diction:            
            data = self.cache_diction[identifier]
        else:
            data = None
        return data

    def set(self, identifier, data):
        """Add identifier and its associated data to the cache, and save the cache as json"""
        identifier = identifier.upper() 
        self.cache_diction[identifier] = data
        self._save_to_disk()


