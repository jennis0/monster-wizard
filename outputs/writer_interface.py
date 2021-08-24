import abc
from typing import List, Any

from extractor.creature_schema import CreatureSchema
from utils.datatypes import Source

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