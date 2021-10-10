import os

from data_loaders.cached_loader_wrapper import CachedLoaderWrapper
from extractor.creature_schema import CreatureSchema
from preprocessing.columniser import Columniser
from data_loaders.data_loader_interface import DataLoaderInterface

from configparser import ConfigParser
from logging import Logger
from typing import Tuple, Dict, List, Any

from utils.datatypes import Section, Source
from utils.drawing import drawBoundingBoxes

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

        self.data = None
        self.statblocks = {}

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

        self.writer = writer

    def load_data(self, filepath: str) -> List[Source]:
        '''Attempt to load the files in the passed path. Returns the data if loaded'''

        files_to_process = [filepath]
        sources = []
        while len(files_to_process) > 0:
            f = files_to_process.pop(0)
            if os.path.isdir(f):
                files_to_process += [os.path.join(f, fp) for fp in os.listdir(f)]
                continue

            ft = f.split(".")[-1]

            if ft not in self.loaders_by_filetype:
                self.logger.error("No data loader implemented for filetype '{}'. Failed to load {}".format(ft, f))
                return None

            try:
                loader = self.loaders_by_filetype[ft]
                source = loader.load_data_from_file(f)
                self.logger.info("Loaded file {}".format(f))
                sources.append(source)
            except Exception as e:
                self.logger.exception(e)
                self.logger.error("Failed to load file {}")
                return None

        return sources

    def get_loaded_files(self):
        return [list(self.data.keys())]

    def parse(self, filepath: str, output_file: str=None, pages: List[int]=None, draw_lines=False, draw_columns=False, draw_statblocks=False, draw_clusters=False, draw_final_columns=False) \
            -> Tuple[Dict[int, List[Any]], Dict[int, List[Section]]]:
        '''Load data from the file and try to find the statblocks. Use the draw options to show individual parts of the statblock discovery pipeline. Set output file
        to a filename to write using the selected writer.'''

        draw = draw_lines or draw_columns or draw_statblocks or draw_clusters

        sources = self.load_data(filepath)

        finished_ps = []
        finished_sb = []
        for source in sources:

            if not source:
                self.logger.error("Failed to load {}".format(filepath))
                return None
            cp = CreatureFactory(self.config, self.logger)

            self.logger.info("Loading {}".format(source.name))
            self.logger.debug("Found {} page{}".format(source.num_pages, 's' if source.num_pages > 1 else ''))

            ### Override provided metadata with user input
            if self.override_title:
                source.name = self.override_title
            if self.override_authors:
                source.authors = self.override_authors
            if self.override_url:
                source.url = self.override_url
            
            statblocks = {}
            parsed_statblocks = {}
            for i, page_data in enumerate(source.pages):
                if pages and i not in pages:
                    continue
                
                self.logger.debug("Processing {} lines".format(len(page_data.lines)))

                boxes = []
                colours = []

                if draw_lines:
                    boxes += [x for x in page_data.lines]
                    colours += [self.line_colour for i in range(len(page_data.lines))]

                    ### Parse data into sections
                columns = self.columniser.find_columns(page_data.lines)

                if draw_columns:
                    boxes += [x for x in columns]
                    colours += [self.column_colour for i in range(len(columns))]

                ### Generate line annotations
                for col in columns:
                    self.line_annotator.annotate(col.lines)

                ### Combine lines into clusters
                clusters = []
                for col in columns:
                    clusters.append(self.clusterer.cluster(col.lines))

                if draw_clusters:
                    for col in clusters:
                        boxes += [x for x in col]
                        colours += [self.hierarchy_colour for i in range(len(col))]

                ### Combine line annotations into cluster annotations
                for col in clusters:
                    self.cluster_annotator.annotate(col)

                ### Generate statblocks from clusters
                statblocks[i],background = self.statblock_generator.create_statblocks(clusters)
                
                if draw_statblocks:
                    boxes += [s for s in statblocks[i]]
                    colours += [self.statblock_colour for i in range(len(statblocks[i]))]
                
                # ### Recalculate columns within statblocks
                columned_statblocks = []
                if len(statblocks) > 0:
                    for sb in statblocks[i]:
                        new_sb = Section()
                        cols = self.columniser.find_columns(sb.lines)
                        for c in cols:
                            new_sb.add_section(c, sort=False)
                        columned_statblocks.append(new_sb)

                        if draw_final_columns:
                            boxes += [x for x in cols]
                            colours += [self.column_colour for i in range(len(cols))]

                statblocks[i] = columned_statblocks

                if draw:
                    drawBoundingBoxes(source.page_images[i], boxes, colours)

                # Parse the creatures
                if len(statblocks[i]) > 0:
                    parsed_statblocks[i] = []
                    for sb in statblocks[i]:
                        cr = cp.statblock_to_creature(sb)
                        if cr:
                            cr.add_background(background)
                            parsed_statblocks[i].append(cr)

            self.logger.info("Found {} statblocks".format(sum(len(parsed_statblocks[k]) for k in parsed_statblocks)))

            # Write data to file
            if output_file is not None:
                self.logger.info("Writing to file {}".format(output_file))
                creatures = []
                for page in parsed_statblocks:
                    creatures += parsed_statblocks[page]

                writer = self.writers_by_name[self.writer]
                writer.write(output_file, source, creatures)
                writer.append = True #Always append any additional creatures after the first
            else:
                self.logger.info("Not writing as no output file specified")

            finished_ps.append(parsed_statblocks)
            finished_sb.append(statblocks)

        return finished_ps, finished_sb

