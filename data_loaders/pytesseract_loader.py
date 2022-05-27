from __future__ import annotations

import logging
import configparser
from typing import List, Any

from PIL import Image
import pytesseract as pyt

from utils.datatypes import Line, Bound, Section, Source

from uuid import uuid4

from data_loaders.data_loader_interface import DataLoaderInterface

import os


class TesseractLoader(DataLoaderInterface):
    '''Used Google's Tesseract to generates a set of lines and bounding boxes from an image'''

    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger) -> TesseractLoader:
        '''Creates a TextractImageLoader using the passed configurationa and logger'''
        self.config = config
        self.logger = logger.getChild("txloader")

        print("In tesseract loader")

    def get_name(self) -> str:
        '''Returns a human readable name for this parser'''
        return "textract"

    def get_filetypes(self) -> List[str]:
        '''Returns list of file types accepted by this data loader'''
        return ["jpg", "png", "webp"]

    def load_data_from_file(self, filepath: str) -> Source:
        '''Takes a path to an image and returns a Section containing extracted lines of text for each page'''
        if not os.path.exists(filepath):
            self.logger.error("Image {} does not exist".format(filepath))

        print("Loading from Tesseract")

        images = self.__load_images_from_file(filepath)
        pages = self.__extract_text(images)
        source = Source(
            filepath=filepath, 
            name=filepath.split(os.pathsep)[-1],
            pages=pages,
            page_images=images,
            images = None,
            num_pages=len(pages),
            authors=None,
            url=None
        )

        return source
        
    def __load_images_from_file(self, filepath: str) -> List[Any]:
        '''Takes a path to an image or folder of images and returns that image'''
        if not os.path.exists(filepath):
            self.logger.error("Image {} does not exist".format(filepath))

        images = []
        if os.path.isdir(filepath):
            for im_file in os.listdir(filepath):
                try:
                    images.append(Image.open(os.path.join(filepath, im_file)))
                except:
                    self.logger.error(f"Failed to open image file {os.path.join(filepath, im_file)}")
        else:
            try:
                images.append(Image.open(filepath))
            except:
                self.logger.error(f"Failed to open image file {filepath}")
        
        return images

    def __extract_text(self, images: List[Image.Image]) -> List[Section]:
        '''Use Tesseract to extract lines and bounding boxes'''
        lines = []
        for im in images:
            image_lines = {}
            boxes = pyt.image_to_data(im, lang='eng', output_type=pyt.Output.DICT)
            n_boxes = len(boxes["left"])
            for i in range(n_boxes):
                bound = Bound(boxes['left'][i], 
                    boxes['top'][i], 
                    boxes["width"][i],
                    boxes['height'][i]
                )

                id = "{}.{}.{}.{}".format(boxes["page_num"][i], boxes["block_num"][i],boxes["par_num"][i],boxes["line_num"][i])
                if id in image_lines:    
                    image_lines[id] = Line.merge([image_lines[id], Line(boxes["text"][i], bound, [])])
                else:
                    image_lines[id] = Line(boxes["text"][i], bound, [])
            
            line_nums = list(image_lines.keys())
            line_nums.sort()
            lines.append(Section([image_lines[k] for k in line_nums]))

        print(lines)
        return lines
        

        