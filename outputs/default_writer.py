import os
import json
from schema import Schema, Optional
from configparser import ConfigParser
from logging import Logger
from typing import Any, List

from utils.datatypes import Source
from fifthedition.creature_schema import CreatureSchema
from outputs.writer_interface import WriterInterface



OutSchema = Schema(
    [{
        "title": str,
        Optional("author"): str,
        Optional("url"): str,
        "creatures": [CreatureSchema]
    }]
)

class DefaultWriter(WriterInterface):
    '''Write creature schema in their default (internal) format'''

    def __init__(self, config: ConfigParser, logger: Logger, append: bool=False):
        self.logger = logger.getChild("default_out")
        self.config = config
        self.append = append

    @staticmethod
    def get_long_name() -> str:
        '''Returns a human readable name for this output writer'''
        return "Default"

    @staticmethod
    def get_name() -> str:
        '''Returns a human readable name for this output writer'''
        return "default"

    @staticmethod
    def get_filetype() -> str:
        '''Returns the output filetype of this writer'''
        return ".json"

    def write(self, filename: str, source: Source, creatures: List[Any], append: bool=None) -> bool:
        '''Writes the creatures to the specified file. If append is set to true, creatures will be inserted into the existing file. Returns True if write is successful'''

        ### Apply configuration overrides
        if append is None:
            append = self.append


        ### Ensure we're writing something with the correct filetype
        if not filename.endswith(DefaultWriter.get_filetype()):
            filename = ".".join(filename.split(".")[:-1]) + DefaultWriter.get_filetype()

        if not os.path.exists(filename) or append:
            make_file = True
            self.logger.debug("Writing new file")
        elif not os.path.isfile(filename):
            self.logger.error("Output file is a directory. Can't write")
            return False

        with open(filename, 'r') as f:
            if make_file:
                data = []
            else:
                data = json.load(f)

        written = False
        for source_entry in data:
            if source_entry["title"] == source.name:
                source_entry["creatures"] += creatures
                written = True
                self.logger.debug("Appending creatures to existing source")
                break
        
        if not written:
            self.logger.debug("Making new source entry")
            data.append(
                {
                    "title": source.name,
                    "creatures": [c.to_json() for c in creatures]
                }
            )
            if source.author is not None:
                data[-1]["author"] = source.author
            if source.url is not None:
                data[-1]["url"] = source.url

        with open(filename, 'w') as f:
            json.dump(data, f)

        return True


