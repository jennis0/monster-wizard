import configparser
import re
import numpy as np
import logging
import configparser
from typing import List, Tuple

import extractor.constants as constants
from extractor.creature import Creature
from utils.datatypes import Bound, Line, Section

class Enrichments(object):
    '''Applies a variety of algorithms to provide additional information to the parsed statblocks'''
    
    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("imagepicker")

    def associated_images(statblocks: List[Creature], images: List[Tuple[Bound, bytes]]):

        ### If we have a title page, assume they might use a double page layout
        has_title_page = statblocks[0].section.lines[0].page > 1
        image_links = {}

        for sb in statblocks:
            lines = sb.section.lines
            pages = list(set([l.page for l in lines]))
            candidate_images = []
            for p in pages:
                if len(images[p]) > 0:
                    candidate_images += images[p]

            #If we are only on a single page, image might be page on either side. Assume double spread layout
            p_min = min(pages)
            p_max = max(pages)
            if p_min == p_max and has_title_page:
                #Even number, assume left hand page
                if p_min % 2 == 0 and p_min + 1 < len(images):
                    candidate_images += images[p_min+1]
                elif p_min - 1 > 0:
                    candidate_images += images[p_min-1]

