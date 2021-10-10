from typing import List, Any, Optional  
import random
import string
import json
from logging import Logger
from configparser import ConfigParser
import os


class CompendiumGenerator(object):

    def __init__(self, logger: Logger, config: ConfigParser):
        self.logger = logger
        self.config = config

    def generate_unique_id(self):
        '''Returns a 16 character alphanumeric identifier'''
        return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))


    def to_compendium_format(self, data: List[Any]) -> str:
        '''Packs the list of objects into a foundry compatible compendium format'''

        self.logger.debug("Beginning to pack {} items".format(len(data)))

        success = 0
        compendium_string = ""
        for d in data:
            try:
                if "_id" in d:
                    s = d
                else:
                    s = {"_id":self.generate_unique_id(), **d}
                s = json.dumps(s)
                compendium_string += s + "\n"
                success += 1
            except Exception as e:
                self.logger.warning("Failed to pack object {}. Error {}".format(data, e))
        
        self.logger.debug("Sucessfully packed {} items".format(success))
        return compendium_string

    def from_compendium_format(self, compendium_string: str) -> List[Any]:
        '''Unpacks the raw compendium text into a python data structure'''
        lines = compendium_string.split("\n")
        unpacked = []
        for l in lines:
            try:
                unpacked.append(json.loads(l))
            except Exception as e:
                self.logger.warning("Failed to unpack compendium line: {}".format(l))
                self.logger.warning(e)

        return unpacked

    def from_compendium(self, file: os.PathLike) -> Optional[List[Any]]:
        if not os.path.exists(file) or os.path.isdir(file):
            self.logger.error("File {} does not exist".format(file))

        with open(file) as f:
            return self.from_compendium_format(f.read())