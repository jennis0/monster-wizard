from __future__ import annotations

from typing import Optional, Any, Tuple
import os
import json
import logging
import hashlib
import base64

class CacheManager(object):

    def __init__(self, logger: logging.Logger, cache_dir: str, name: str) -> CacheManager:
        '''Returns a request cache, the name is used to
        differentiate between multiple caches in the same directory'''

        self.cache_dir = cache_dir
        self.logger = logger.getChild("cache")
        self.name = name
        self.index = {}

        if not os.path.exists(cache_dir):
            self.logger.debug("Creating cache directory {}".format(cache_dir))
            os.makedirs(cache_dir)

        self.index_path = os.path.join(cache_dir, "{}_index.json".format(self.name))
        self.__load_index()

    def __filename_to_id(self, filename: str) -> str:
        '''Generates a unique foldername based on the full filepath.'''
        tag = "-".join(filename.split(os.sep)[-1].split(".")[:-1])
        id = hashlib.sha1(filename.strip().encode('utf8') + self.name.strip().encode("utf8")).hexdigest()[:24]
        return "{}_{}".format(tag, id)

    def __load_index(self):
        if os.path.exists(self.index_path):
            with open(self.index_path, 'r') as f:
                self.index = json.load(f)

    def __write_index(self):
        with open(self.index_path, 'w') as f:
                json.dump(self.index, f)

    def __get_cache_path(self, filename: str) -> Optional[str]:
        '''Get the path where this file is cached'''
        id = self.__filename_to_id(filename)
        if id in self.index:
            return self.index[id]
        else:
            return None

    def check_cache(self, filename: str) -> bool:
        '''Checks if a request has previously been made for this file. Returns
        true if found'''
        return self.__get_cache_path(filename) is not None

    def write(self, filename: str, json_data: Optional[Any]=None):
        '''Writes a bytestream and json data into a local cache'''

        if not json_data:
            self.logger.warning("Must have at least some data to cache")
            return

        # Make a folder in the cache
        id = self.__filename_to_id(filename)
        self.logger.debug("Writing request for file {} to cache in {}".format(filename, id))

        path = os.path.join(self.cache_dir, id)
        if not os.path.exists(path):
            os.makedirs(path)

        #Write the structured data
        if json_data:
            with open(os.path.join(path, "json.cache"), 'w') as f:
                json.dump(json_data, f)

        self.index[id] = path
        self.__write_index()

    def read(self, filename: str) -> Tuple[bytes, Any]:
        '''Returns the stored byte file and json file for the cached file'''
        cache_dir = self.__get_cache_path(filename)
        if not cache_dir:
            self.logger.warning("Tried to read non-existant cache entry for {}".format(filename))

        json_path = os.path.join(cache_dir, "json.cache")

        if os.path.exists(json_path):
            with open(os.path.join(cache_dir, "json.cache"), 'r') as f:
                json_data = json.load(f)
        else:
            json_data = None

        if not json_data:
            self.logger.warning("Cache directory for {} exists but contains no data.".format(filename))
            return None

        return json_data

        
        
