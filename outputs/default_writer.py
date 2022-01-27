import os
import json
from schema import Schema, Optional
from configparser import ConfigParser
from logging import Logger
from typing import Any, List

from utils.datatypes import Source
from extractor.creature_schema import CreatureSchema
from outputs.writer_interface import WriterInterface



OutSchema = Schema(
    [{
        "title": str,
        Optional("authors"): [str],
        Optional("url"): str,
        "creatures": [CreatureSchema]
    }]
)

class DefaultWriter(WriterInterface):
    '''Write creature schema in PDF2VTTs internal format'''

    def __init__(self, config: ConfigParser, logger: Logger, append: bool=False):
        self.logger = logger.getChild("default_out")
        self.config = config
        self.append = append

    @staticmethod
    def get_long_name() -> str:
        '''Returns a human readable name for this output writer'''
        return "Internal"

    @staticmethod
    def get_name() -> str:
        '''Returns a human readable name for this output writer'''
        return "internal"

    @staticmethod
    def get_filetype() -> str:
        '''Returns the output filetype of this writer'''
        return "json"

    @staticmethod
    def prettify_name(s: str) -> str:
        '''Turn a filepath into a nicer name'''
        file = os.path.basename(s).split('.')[0]
        file.replace("_", " ")
        words = file.split(" ")
        stop_words = ["of","and","the","in","a","an"]

        capped_words = [w[0].upper() + w[1:] for w in words if w not in stop_words and len(w) > 1]
        capped_words[0] = capped_words[0][0].upper() + capped_words[0][1:]
        return " ".join(capped_words)

    def write(self, filename: str, source: Source, creatures: List[Any], append: bool=None) -> bool:
        '''Writes the creatures to the specified file. If append is set to true, creatures will be inserted into the existing file. Returns True if write is successful'''

        ### Apply configuration overrides
        if append is None:
            append = self.append

        ### Ensure we're writing something with the correct filetype
        if not filename.endswith(DefaultWriter.get_filetype()):
            filename = ".".join(filename.split(".")[:-1]) + "." + DefaultWriter.get_filetype()

        make_file = False
        if not os.path.exists(filename) or not append:
            make_file = True
            self.logger.debug("Writing new file")
        elif not os.path.isfile(filename):
            self.logger.error("Output file is a directory. Can't write")
            return False


        if make_file:
            data = []
        else:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

        pretty_name = DefaultWriter.prettify_name(source.name)

        source_data = {
            'title': pretty_name,
        }

        if source.num_pages > 0:
            source_data['pages'] = source.num_pages
        if source.url is not None:
            source_data['url'] = source.url
        if source.authors is not None and len(source.authors) > 0:
            source_data['authors'] = source.authors

        written = False
        for source_entry in data:
            if source_entry['source']["title"] == pretty_name:
                source_entry["creatures"] += [c.to_json() for c in creatures]
                source_entry['source'] = source_data
                written = True
                self.logger.debug("Appending creatures to existing source")
                break
        
        if not written:
            self.logger.debug("Making new source entry")
            data.append(
                {
                    "source": source_data,
                    'title': source_data['title'],
                    "creatures": [c.to_json() for c in creatures]
                }
            )
            if source.authors is not None:
                data[-1]["authors"] = source.authors
            if source.url is not None:
                data[-1]["url"] = source.url

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        return True


