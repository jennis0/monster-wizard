import abc
from typing import List, Any
import json

from ..utils.datatypes import Source

class WriterInterface(object):

    @staticmethod
    @abc.abstractmethod
    def get_long_name() -> str:
        '''Returns a human readable name for this output writer'''
        raise NotImplementedError("users must define a function to return the name")
    
    @staticmethod
    @abc.abstractmethod
    def get_name() -> str:
        '''Returns an internal name to be used for this writer'''
        raise NotImplementedError("users must define a function to return the name")

    @staticmethod
    @abc.abstractmethod
    def get_filetype() -> str:
        '''Returns the default filetype written by this writer'''
        raise NotImplementedError('users must define the default filetype.')

    @abc.abstractmethod
    def write(self, filename: str, source: Source, creatures: List[Any], append: bool=None) -> bool:
        '''Writes the creatures to the specified file. If append is set to true, creatures will be inserted into the existing file. Returns True if write is successful'''
        raise NotImplementedError("users must define a function to write to a file.")

    def write_pdf2vtt(self, out_filename: str, pdf2vtt_data: List[Any], append: bool=None) -> bool:
        '''Converts from an existing pdf2vtt file into the writer format'''

        ### Apply configuration overrides
        if append is None:
            append = super().append

        with open(pdf2vtt_data, 'r') as f:
            data = json.load(f)

        ret = True
        for source in data:
            source_data = data['source']
            s = Source(
                source_data['title'], source_data['title'], source_data['num_pages']  if 'num_pages' in source_data else None
                , None, None, None, source_data['authors'] if 'authors' in source_data else None
            )

            ret &= super().write(out_filename, s, source['creatures'], append)

        return ret        