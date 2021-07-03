from __future__ import annotations

import logging
import configparser
from typing import List, Any

import cv2
from utils.datatypes import Line, Bound, Section, Source
from utils.aws import get_authenticated_client
from utils.cache import CacheManager

from data_loaders.data_loader_interface import DataLoaderInterface

import os
import json

from utils.aws import get_authenticated_client

class TextractImageLoader(DataLoaderInterface):
    '''Used AWS Textract to generates a set of lines and bounding boxes from an image'''

    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger) -> TextractImageLoader:
        '''Creates a TextractImageLoader using the passed configurationa and logger'''
        self.config = config
        self.logger = logger.getChild("txloader")
        self.cache = CacheManager(self.logger, config.get("default", "cache"), 'textract')

    @staticmethod
    def get_name() -> str:
        '''Returns a human readable name for this parser'''
        return "Textract Loader"

    @staticmethod
    def get_filetypes() -> List[str]:
        '''Returns list of file types accepted by this data loader'''
        return ["jpg", "png", "webp"]

    def load_data_from_file(self, filepath: str) -> Source:
        '''Takes a path to an image and returns a Section containing extracted lines of text for each page'''
        if not os.path.exists(filepath):
            self.logger.error("Image {} does not exist".format(filepath))

        response = self.__call_textract(filepath)
        pages = self.__response_to_lines(response)
        images = self.load_images_from_file(filepath)
        source = Source(
            filepath=filepath, 
            name=filepath.split(os.pathsep)[-1],
            pages=pages,
            images=images,
            num_pages=len(pages),
            authors=None,
            url=None
        )
        return source
        
    def load_images_from_file(self, filepath: str) -> List[Any]:
        '''Takes a path to an image and returns that image'''
        if not os.path.exists(filepath):
            self.logger.error("Image {} does not exist".format(filepath))

        return [cv2.imread(filepath)]

    def __response_to_lines(self, response: Any) -> List[Section]:
        if "Blocks" not in response:
            self.logger.error("No lines found in response")
            return []

        pages = [Section([]) for i in range(response["DocumentMetadata"]["Pages"])]
        for line in response["Blocks"]:
            if line["BlockType"] != "LINE":
                continue
            
            if "Page" not in line:
                page = 1
            else:
                page = line["Page"]

            b_box = Bound(**{k.lower():line["Geometry"]["BoundingBox"][k] for k in line["Geometry"]["BoundingBox"]})

            pages[page - 1].add_line(Line(id=line["Id"], text=line["Text"], bound=b_box, attributes=[]))

        for i,p in enumerate(pages):
            p.attributes = ["page_{}".format(i+1)]

        return pages


    def __load_from_directory(self, response_path: str) -> List[List[Line]]:
        with open(os.path.join(response_path, 'response.json'), 'r') as f:
            return json.load(f)


    def __call_textract(self, filepath: str) -> Any:
        '''Call AWS Textract services, or return cached response if it exists'''

        # Check if we've processed this image before
        cached_response = self.cache.check_cache(filepath)
        if cached_response:
            self.logger.info("Retrieving cached result for {}".format(filepath))
            return self.__load_from_directory(cached_response)
        
        # Read image
        with open(filepath, 'rb') as f:
            image = f.read()
        
        # Create AWS client
        self.logger.debug("Creating boto client")
        client = get_authenticated_client(self.config, self.logger,'textract')
        try:
            self.logger.info("Sending Textract request for {}".format(filepath))
            response = client.detect_document_text(
                Document={
                    'Bytes':image
                },
            )
        except Exception as e:
            self.logger.error(e)
            return []
        self.logger.debug("Received Textract response")

        self.cache.write_to_cache(filepath, image, response)
        return response

        

        