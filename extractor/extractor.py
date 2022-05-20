from ctypes import Union
import os
from fastapi import File, UploadFile
from configparser import ConfigParser
from logging import Logger
from typing import Tuple, Dict, List, Any, Optional
import traceback

from data_loaders.cached_loader_wrapper import CachedLoaderWrapper
from data_loaders.data_loader_interface import DataLoaderInterface
from extractor.enrichments import Enrichments

from utils.datatypes import Section, Source

from preprocessing.columniser import Columniser
from preprocessing.clusterer import Clusterer

from extractor.annotators import LineAnnotator, SectionAnnotator
from extractor.statblock_builder import StatblockBuilder
from extractor.creature_factory import CreatureFactory

from outputs.writer_interface import WriterInterface
         
class StatblockExtractor(object):

    def __init__(self, config: ConfigParser, logger: Logger):

        self.config = config
        self.logger = logger

        self.loaders_by_filetype = {}
        self.writers_by_name = {}
        self.writer = ''

        self.columniser = Columniser(config, logger)
        self.line_annotator = LineAnnotator(config, logger)
        self.clusterer = Clusterer(config, logger)
        self.cluster_annotator = SectionAnnotator(config, logger)
        self.statblock_generator = StatblockBuilder(config, logger)
        self.enrichments = Enrichments(config, logger)

        self.line_colour = (120, 0, 0, 120)
        self.column_colour = (0, 120, 0, 120)
        self.hierarchy_colour = (0, 0, 120, 120)
        self.statblock_colour = (200, 50, 50, 250) 

        self.override_title = config.get("source", "title", fallback=None)
        self.override_authors = config.get("source", "authors", fallback=None)
        self.override_url = config.get("source", "url", fallback=None)

        if self.override_authors:
            self.override_authors = self.override_authors.split(",")

    def register_data_loader(self, data_loader : DataLoaderInterface) -> bool:
        '''Register this data loader. Returns True if registration is successful'''

        dl = CachedLoaderWrapper(self.config, self.logger, data_loader)

        supported_file_types = dl.get_filetypes()

        for ft in supported_file_types:
            if ft in self.loaders_by_filetype:
                self.logger.error("Cannot register multiple data loaders for the same filetype. Type {} from {} conflicts with {}".format(
                    ft, type(data_loader.__name__), 
                    type(self.loaders_by_filetype[ft]).__name__))
                return False

            self.loaders_by_filetype[ft] = dl
        return True

    def register_output_writer(self, writer: WriterInterface, **kwargs) -> bool:
        '''Registers an output writer. Passes kwargs through to the writer'''
        self.writers_by_name[writer.get_name()] = writer(self.config, self.logger, **kwargs)

    def select_writer(self, writer: str) -> bool:
        '''Select an output writer, returns True if successful'''
        if writer not in self.writers_by_name:
            self.logger.error("No Output Writer named {} registered".format(writer))
            return False

        self.writer = self.writers_by_name[writer]


    def load_data(self, file_or_filepath: Any, filename:Optional[str]=None, filetype:Optional[str]=None) -> List[Source]:
        '''Attempt to load the files in the passed path. Returns the data if loaded'''

        files_to_process = [file_or_filepath]
        sources = []

        while len(files_to_process) > 0:
            f = files_to_process.pop(0)

            ### Handle filenames
            if isinstance(f, str):
                if os.path.isdir(f):
                    files_to_process += [os.path.join(f, fp) for fp in os.listdir(f)]
                    continue

                if not filetype:
                    filetype = f.split(".")[-1]

                if filetype not in self.loaders_by_filetype:
                    self.logger.error("No data loader implemented for filetype '{}'. Failed to load {}".format(filetype, f))
                    return None

                try:
                    loader = self.loaders_by_filetype[filetype]
                    source = loader.load_data_from_filepath(f)
                    self.logger.info("Loaded file {}".format(f))
                    sources.append(source)
                except Exception as e:
                    self.logger.exception(e)
                    self.logger.error(f"Failed to load file {f}")
                    return None
            
            ### Handle actual files being passed
            else:
                if filetype is None:
                    self.logger.error("Failed to specify filetype.")

                if filetype not in self.loaders_by_filetype:
                    self.logger.error("No data loader implemented for filetype '{}'. Failed to load {}".format(filetype, f))
                    return None

                try:
                    loader = self.loaders_by_filetype[filetype]
                    source = loader.load_data_from_file(f, filename)
                    self.logger.info("Loaded file {}".format(f))
                    sources.append(source)
                except Exception as e:
                    self.logger.exception(e)
                    self.logger.error(f"Failed to load file {f}")
                    return None

        return sources



    def parse(self, filepaths: List[str], pages: List[int]=None) \
            -> Tuple[Dict[str, Tuple[Source, Dict[str, List[Any]]]], Dict[int, List[Section]]]:
        '''Load data from the file and try to find the statblocks. Set output file
        to a filename to write using the selected writer.'''

        finished_ps = {}
        for f in filepaths:
            state = {}
            statblocks, source = self.file_to_statblocks(f, f, pages, state)
            creatures, errors = self.statblocks_to_creatures(source, statblocks, state)

            print(creatures)

            finished_ps[source.name] = (source, creatures, statblocks, errors)

        return finished_ps


    def file_to_statblocks(self, file: Any, filename: str, filetype:str, pages:Optional[List[int]]=None, state:Optional[Any] = None) -> Tuple[List[Section], Source]:
        sources = self.load_data(file, filename, filetype)
        if not sources or len(sources) == 0:
            self.logger.error("Failed to load {}".format(filename))
        source = sources[0]

        self.logger.info("Loading {}".format(source.name))
        self.logger.debug("Found {} page{}".format(source.num_pages, 's' if source.num_pages > 1 else ''))

        final_clusters = []

        count = len(source.pages)
        for i, page_data in enumerate(source.pages):
            if state:
                state["progress"] = [i, count]
            if pages and i+1 not in pages:
                continue
            
            self.logger.debug("Processing {} lines".format(len(page_data.lines)))

            ### Parse data into sections
            columns = self.columniser.find_columns(page_data.lines)

            ### Generate line annotations
            for col in columns:
                self.line_annotator.annotate(col.lines)

            if self.config.get("default", "debug"):
                self.logger.debug("Annotated Lines")
                for c in columns:
                    self.logger.debug("COLUMN START")
                    self.logger.debug(f"Has {len(c.lines)} lines")
                    for l in c.lines:
                        self.logger.debug(l)
                    self.logger.debug("COLUMN END")
                    
            ### Combine lines into clusters
            clusters = []
            for col in columns:
                clusters.append(self.clusterer.cluster(col.lines))

            for col in clusters:
                for clus in col:
                    clus.page = i+1

            ### Combine line annotations into cluster annotations
            for col in clusters:
                self.cluster_annotator.annotate(col)
                final_clusters.append(col)
                for cl in final_clusters[-1]:
                    cl.page = i+1

        ### Generate statblocks from clusters
        statblocks,background = self.statblock_generator.create_statblocks(final_clusters)

        for b in background:
            print(b.get_section_text())

        return statblocks, source


    def statblocks_to_creatures(self, source, statblocks: List[Section], state :Optional[Any] = None) -> List[Any]:
        
        cf = CreatureFactory(self.config, self.logger)
        parsed_creatures = []
        errors = []

        count = len(statblocks)
        if state:
            state["progress"] = [0,count]

        for i,sb in enumerate(statblocks):
            creature = None
            try:
                creature = cf.statblock_to_creature(sb)
            except Exception as e:
                traceback.print_stack()
                print()
                traceback.print_exc()
                errors.append([sb.lines[0].text, "Failed to parse: " + str(e)])
            if creature:
                creature.set_source(source.name, sb.page+1)
                parsed_creatures.append(creature)
            if state:
                state["progress"] = [i,count]

        return parsed_creatures, errors

    def write_to_file(self, output_file: str, source: Source, parsed_statblocks: Dict[str, List[Any]]):
            # Write data to file
            self.logger.info("Writing to file {}".format(output_file))
            creatures = []

            print(parsed_statblocks)

            for s in parsed_statblocks:
                creatures += parsed_statblocks[s]
            
            self.writer.write(output_file, source, creatures)
            self.writer.append = True #Always append any additional creatures after the first
