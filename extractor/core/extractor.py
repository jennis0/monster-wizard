import os
from configparser import ConfigParser
from logging import Logger
from typing import Tuple, Dict, List, Any, Optional
import traceback

from enum import Enum, auto

from ..data_loaders.cached_loader_wrapper import CachedLoaderWrapper
from ..data_loaders.data_loader_interface import DataLoaderInterface
from ..outputs.writer_interface import WriterInterface
from ..utils.datatypes import Source
from ..preprocessing.columniser import Columniser
from ..preprocessing.clusterer import Clusterer

from .annotators import LineAnnotator, SectionAnnotator
from .statblock_builder import StatblockBuilder
from .creature_factory import CreatureFactory
from .enrichments import Enrichments


         
class StatblockExtractor(object):

    class JobState(Enum):
        file_upload = auto()
        text_extraction = auto()
        finding_statblock_text = auto()
        joining_partial_statblocks = auto()
        processing_statblocks = auto()
        finished = auto()
        error = auto()


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


    def load_data(self, file_or_filepath: Any, filename:Optional[str]=None, filetype:Optional[str]=None, state:Optional[Any]=None) -> List[Source]:
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
                    source = loader.load_data_from_filepath(f, state=state)
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
                    source = loader.load_data_from_file(f, filename, state=state)
                    self.logger.info("Loaded file {}".format(f))
                    sources.append(source)
                except Exception as e:
                    self.logger.exception(e)
                    self.logger.error(f"Failed to load file {f}")
                    return None

        return sources



    def parse_multiple(self, filepaths: List[str], pages: List[List[int]]=None) \
            -> Dict[str, Tuple[Source, List[Dict[str, Any]]]]:
        '''Load data from the file and try to find the statblocks. Set output file
        to a filename to write using the selected writer.'''

        parsed_sources = {}

        if pages == None:
            pages = [None for i in range(len(filepaths))]

        for f,ps in zip(filepaths, pages):
            source, errors = self.parse(f, filename=f, pages=ps)
            if not source:
                self.logger.debug(f"Failed to parse {f}")
                continue
            source.name = self.config.get("source", "title", fallback=source.name)
            parsed_sources[source.name] = (source, errors)

        return parsed_sources


    def parse(
            self, 
            file_or_filepath: Any, 
            filename: Optional[str] = None, 
            filetype:str=None, 
            pages:Optional[List[int]]=None, 
            extract_images: bool=True,
            state:Optional[Dict[str,Any]] = {
                "state":JobState.text_extraction, "progress":[-1,1], "errors":[]},
            
        ) -> Tuple[Source, Dict[str, Any]]:
        
        self.logger.info("Loading {}".format(filename))
        state["state"] = StatblockExtractor.JobState.text_extraction
        try:
            sources = self.load_data(file_or_filepath, filename, filetype, state=state)
        except:
            pass
        
        if not sources or len(sources) == 0:
            err_message = f"Failed to load {filename}"
            self.logger.error(err_message)
            state["errors"].append(err_message)
            state["state"] = StatblockExtractor.JobState.error
            return None, state["errors"]

        source = sources[0]
        self.logger.debug("Found {} page{}".format(source.num_pages, 's' if source.num_pages > 1 else ''))

        final_clusters = []
        page_count = len(source.pages)

        state["state"] = StatblockExtractor.JobState.finding_statblock_text
        for page, page_data in enumerate(source.pages):
            self.logger.debug("Processing {} lines".format(len(page_data.lines)))
            self.logger.debug(page_data.lines)

            state["progress"] = [page, page_count]

            if pages and page+1 not in pages:
                self.logger.debug("Skipping page")
                continue
            
            ### Parse lines into columns
            try:
                columns = self.columniser.find_columns(page_data.lines)

                ### Generate line annotations
                for col in columns:
                    self.line_annotator.annotate(col.lines)
            except:
                err_message = "Crashed during line processing"
                state["errors"].append(err_message)
                self.logger.debug(traceback.format_exc())
                return None, state["errors"]

            if self.config.get("default", "debug"):
                self.logger.debug("Annotated Lines")
                for c in columns:
                    self.logger.debug("COLUMN START")
                    self.logger.debug(f"Has {len(c.lines)} lines")
                    for l in c.lines:
                        self.logger.debug(l)
                    self.logger.debug("COLUMN END")
                    
            ### Parse columns into sections
            try:
                ### Combine lines into clusters
                clusters = []
                for col in columns:
                    clusters.append(self.clusterer.cluster(col.lines))

                for col in clusters:
                    for clus in col:
                        clus.page = clus.lines[0].page if len(clus.lines) > 0 else page+1

                ### Combine line annotations into cluster annotations
                for col in clusters:
                    self.cluster_annotator.annotate(col)
                    final_clusters.append(col)
                    for cl in final_clusters[-1]:
                        cl.page = cl.lines[0].page if len(cl.lines) > 0 else page+1
            except:
                err_message = "Crashed during line clustering"
                state["errors"].append(err_message)
                self.logger.debug(traceback.format_exc())
                traceback.print_exc()
                return None, state["errors"]

        ### Generate statblocks from clusters
        state["state"] = StatblockExtractor.JobState.joining_partial_statblocks
        state["progress"] = [-1,1]
        try:
            statblocks,background = self.statblock_generator.create_statblocks(final_clusters)
            source.background_text=background
        except:
            err_message = "Crashed statblock creation"
            state["errors"].append(err_message)
            self.logger.debug(traceback.format_exc())
            return None, state["errors"]



        ### Turn statblock text into formatted statblock
        cf = CreatureFactory(self.config, self.logger)
        parsed_statblocks = []
        statblock_count = len(statblocks)
        state["state"] = StatblockExtractor.JobState.processing_statblocks
        state["progress"] = [0,statblock_count]

        try:
            for page,sb in enumerate(statblocks):
                statblock = None
                try:
                    statblock = cf.statblock_to_creature(sb, source, sb.page)
                except Exception as e:
                    traceback.print_stack()
                    print()
                    traceback.print_exc()
                    state["errors"].append([sb.lines[0].text, "Failed to parse: " + str(e)])
                if statblock:
                    parsed_statblocks.append(statblock)
            
                state["progress"] = [page, statblock_count]
        except:
            err_message = "Crashed statblock processing"
            state["errors"].append(err_message)
            self.logger.debug(traceback.format_exc())
            return None

        source.statblocks=parsed_statblocks
        self.enrichments.filter_and_associate_backgrounds(source)
        self.enrichments.filter_and_associate_images(source)

        state["progress"] = [1,1]

        return source, state["errors"]

    def write_to_file(self, output_file: str, source: Source, parsed_statblocks: Dict[str, List[Any]]):
            # Write data to file
            self.logger.info("Writing to file {}".format(output_file))
            creatures = []

            for s in parsed_statblocks:
                creatures += parsed_statblocks[s]
            
            self.writer.write(output_file, source, creatures)
            self.writer.append = True #Always append any additional creatures after the first
