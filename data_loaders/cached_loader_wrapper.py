from configparser import ConfigParser
from logging import Logger

from typing import List

from data_loaders.data_loader_interface import DataLoaderInterface
from utils.cache import CacheManager
from utils.datatypes import Source


class CachedLoaderWrapper(DataLoaderInterface):

    def __init__(self, config: ConfigParser, logger: Logger, loader: DataLoaderInterface):
        self.use_cache = config.getboolean("default", "use_cache", fallback=True)
        self.flush_cache = config.getboolean("default", "flush_cache", fallback=False)
        self.logger = logger.getChild("loader_cache")
        self.loader = loader(config, logger)
        self.cache = CacheManager(logger, config.get("default", "cache", fallback='.cache'), name=self.loader.get_name())

    def get_name(self) -> str:
        return self.loader.get_name()

    def get_filetypes(self) -> List[str]:
        '''Returns a list of file types supported by this data loader'''
        return self.loader.get_filetypes()

    def load_data_from_file(self, filepath: str) -> Source:
        '''Reads file and extracts lines of texts. Returns one section per page'''
        if not self.use_cache:
            return self.loader.load_data_from_file(filepath)

        if not self.flush_cache and self.cache.check_cache(filepath):
            data, json = self.cache.read(filepath)
            if not data and not json:
                self.logger.warning("Found cache dir for {} but it contained no files. Falling back".format(filepath))
            else:
                return Source.deserialise(data, json)
        
        source = self.loader.load_data_from_file(filepath)

        self.logger.debug("Writing {} to cache".format(filepath))
        self.cache.write(filepath, *source.serialise())

        return source
        
