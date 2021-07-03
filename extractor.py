from fifthedition.creature_schema import CreatureSchema
from preprocessing.columniser import Columniser
from data_loaders.data_loader_interface import DataLoaderInterface

from configparser import ConfigParser
from logging import Logger
from typing import Tuple, Union, Dict, List, Any

from utils.datatypes import Section, Source
from utils.drawing import drawBoundingBoxes

from preprocessing.columniser import Columniser
from preprocessing.clusterer import Clusterer

from fifthedition.annotators import LineAnnotator, SectionAnnotator
from fifthedition.statblock_builder import StatblockBuilder
from fifthedition.creature_parser import CreatureParser

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
        self.override_author = config.get("source", "author", fallback=None)
        self.override_url = config.get("source", "url", fallback=None)

    def register_data_loader(self, data_loader : DataLoaderInterface) -> bool:
        '''Register this data loader. Returns True if registration is successful'''
        supported_file_types = data_loader.get_filetypes()
        dl = data_loader(self.config, self.logger)

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

    def load_data(self, filepath: str) -> Union[Source, None]:
        '''Attempt to load the file in the pass path. Returns the data if loaded'''
        ft = filepath.split(".")[-1]

        if ft not in self.loaders_by_filetype:
            self.logger.error("No data loader implemented for filetype '{}'. Failed to load {}".format(ft, filepath))
            return None

        try:
            loader = self.loaders_by_filetype[ft]
            source = loader.load_data_from_file(filepath)
            self.logger.info("Loaded file {}".format(filepath))
            data = source
        except Exception as e:
            self.logger.exception(e)
            self.logger.error("Failed to load file {}")
            return None

        return data

    def get_loaded_files(self):
        return [list(self.data.keys())]

    def parse(self, filepath: str, output_file: str=None, draw_lines=False, draw_columns=False, draw_statblocks=False, draw_clusters=False, draw_final_columns=False) \
            -> Tuple[Dict[int, List[Any]], Dict[int, List[Section]]]:
        '''Load data from the file and try to find the statblocks. Use the draw options to show individual parts of the statblock discovery pipeline. Set output file
        to a filename to write using the selected writer.'''

        draw = draw_lines or draw_columns or draw_statblocks or draw_clusters

        data = self.load_data(filepath)

        ### Override provided metadata with user input
        if self.override_title:
            data.name = self.override_title
        if self.override_author:
            data.author = self.override_author
        if self.override_url:
            data.url = self.override_url

        if not data:
            self.logger.error("Failed to load {}".format(filepath))
            return None
        cp = CreatureParser(self.config, self.logger)

        self.logger.info("Loading {}".format(data.name))
        statblocks = {}
        parsed_statblocks = {}
        for i, page_data in enumerate(data.pages):

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
            statblocks[i] = self.statblock_generator.create_statblocks(clusters)

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
                drawBoundingBoxes(data.images[i], boxes, colours)

            # Parse the creatures
            if len(columned_statblocks) > 0:
                parsed_statblocks[i] = []
                for sb in columned_statblocks:
                    parsed_statblocks[i].append(cp.statblock_to_creature(sb))

        # Write data to file
        if output_file is not None:
            self.logger.info("Writing to file {}".format(output_file))
            creatures = []
            for page in parsed_statblocks:
                creatures += parsed_statblocks[page]

            writer = self.writers_by_name[self.writer]
            writer.write(output_file, data, creatures)
        else:
            self.logger.info("Not writing as no output file specified")

        return parsed_statblocks, statblocks
