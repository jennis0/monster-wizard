import os
import json
from configparser import ConfigParser
from logging import Logger
from typing import Any, List, Dict

from outputs.writer_interface import WriterInterface
from outputs.creature_printer import pretty_format_creature

from utils.datatypes import Source
from utils.config import get_config
import sys

class PrintWriter(WriterInterface):
    '''Write creature schema into a simple text file'''

    def __init__(self, config: ConfigParser, logger: Logger, append: bool=False):
        self.logger = logger.getChild("default_out")
        self.config = config
        self.append = append

    @staticmethod
    def get_long_name() -> str:
        '''Returns a human readable name for this output writer'''
        return "Text Writer"

    @staticmethod
    def get_name() -> str:
        '''Returns a human readable name for this output writer'''
        return "text"

    @staticmethod
    def get_filetype() -> str:
        '''Returns the output filetype of this writer'''
        return "txt"

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

    def write_pdf2vtt(self, out_filename: str, pdf2vtt_data: List[Any], append: bool=None) -> bool:
        '''Writes the information from the existing pdf2vttdata into a human readable text file'''

        ### Apply configuration overrides
        if append is None:
            append = self.append

        with open(pdf2vtt_data, 'r') as f:
            data = json.load(f)

        ret = True
        for source in data:
            source_data = data['source']
            s = Source(
                source_data['title'], source_data['title'], source_data['num_pages']  if 'num_pages' in source_data else None
                , None, None, None, source_data['authors'] if 'authors' in source_data else None
            )

            ret &= self.write(out_filename, s, source['creatures'], append)

        return ret        


    def write(self, filename: str, source: Source, creatures: List[Any], append: bool=None) -> bool:
        '''Writes the creatures to the specified file. If append is set to true, creatures will be inserted into the existing file. Returns True if write is successful'''

        ### Apply configuration overrides
        if append is None:
            append = self.append


        ### Ensure we're writing something with the correct filetype
        if not filename.endswith(PrintWriter.get_filetype()):
            filename = ".".join(filename.split(".")[:-1]) + PrintWriter.get_filetype()

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
            with open(filename, 'r') as f:
                data = json.load(f)

        pretty_name = PrintWriter.prettify_name(source.name)

        text = f"Creatures from '{pretty_name}'\n----------------------------------------------------------\n----------------------------------------------------------\n"
         
        for creature in creatures:
            text += pretty_format_creature(creature) + "\n"

        with open(filename, 'w') as f:
            f.write(text)

        return True

if __name__ == "__main__":
    f = sys.argv[1]
    f_o = sys.argv[2]
    pw = PrintWriter(get_config({}), Logger(), False)
    with open(f, 'r') as fr:
        pw.write_pdf2vtt(f, json.load(fr))
