from __future__ import annotations

from typing import Optional, Any
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
                self.index = json.dump(self.index, f)


    def check_cache(self, filename: str) -> Optional[str]:
        '''Checks if a request has previously been made for this file. Returns
        a path to the stored response if found, otherwise returns None'''
        id = self.__filename_to_id(filename)
        if id in self.index:
            return self.index[id]

        else:
            return None

    def write_to_cache(self, filename: str, request: bytes, response: Any):
        '''Writes the request and response into a local cache'''

        # Make a folder in the cache
        id = self.__filename_to_id(filename)
        self.logger.debug("Writing request for file {} to cache in {}".format(filename, id))

        path = os.path.join(self.cache_dir, id)
        if not os.path.exists(path):
            os.makedirs(path)

        ending = filename.split(".")[-1]

        # Write the request
        with open(os.path.join(path, "file.{}".format(ending)), 'wb') as f:
            f.write(request)

        #Write the response
        with open(os.path.join(path, "response.json"), 'w') as f:
            json.dump(response, f)

        self.index[id] = path
        self.__write_index()
        
