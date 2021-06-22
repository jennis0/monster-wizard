import abc
from typing import List

from utils.datatypes import Source

class DataLoaderInterface(object):

    @staticmethod
    @abc.abstractmethod
    def get_filetypes() -> List[str]:
        '''Returns a list of file types supported by this data loader'''
        raise NotImplementedError('users must define a list of supported filetypes.')

    @abc.abstractmethod
    def load_data_from_file(self, filepath: str) -> Source:
        '''Reads file and extracts lines of texts. Returns one section per page'''
        raise NotImplementedError("userers must define a function to load data from a file.")