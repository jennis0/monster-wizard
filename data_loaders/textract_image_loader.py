from __future__ import annotations

import logging
import configparser
from typing import List, Any
from utils.datatypes import Line, Bound
from utils.aws import get_authenticated_client
from utils.cache import CacheManager

import os
import json

from utils.aws import get_authenticated_client

class TextractImageLoader(object):
    '''Used AWS Textract to generates a set of lines and bounding boxes from an image'''

    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger) -> TextractImageLoader:
        '''Creates a TextractImageLoader using the passed configurationa and logger'''
        self.config = config
        self.logger = logger.getChild("txloader")
        self.cache = CacheManager(self.logger, config.get("default", "cache"), 'textract')

    def image_to_lines(self, image_path: str) -> List[List[Line]]:
        '''Takes a path to an image and returns a list of extracted lines of text for each page'''
        if not os.path.exists(image_path):
            self.logger.error("Image {} does not exist".format(image_path))

        response = self.__call_textract(image_path)
        lines = self.__response_to_lines(response)

        self.logger.info(lines)
        
        return lines

    def __response_to_lines(self, response: Any) -> List[List[Line]]:
        if "Blocks" not in response:
            self.logger.error("No lines found in response")
            return []

        pages = [[] for i in range(response["DocumentMetadata"]["Pages"])]
        for line in response["Blocks"]:
            if line["BlockType"] != "LINE":
                continue
            
            if "Page" not in line:
                page = 1
            else:
                page = line["Page"]

            b_box = Bound(**{k.lower():line["Geometry"]["BoundingBox"][k] for k in line["Geometry"]["BoundingBox"]})

            pages[page - 1].append(Line([line["Text"]], b_box, []))

        return pages


    def __load_from_directory(self, response_path: str) -> List[List[Line]]:
        with open(os.path.join(response_path, 'response.json'), 'r') as f:
            return json.load(f)


    def __call_textract(self, image_path: str) -> Any:
        '''Call AWS Textract services, or return cached response if it exists'''

        # Check if we've processed this image before
        cached_response = self.cache.check_cache(image_path)
        if cached_response:
            self.logger.info("Retrieving cached result for {}".format(image_path))
            return self.__load_from_directory(cached_response)
        
        # Read image
        with open(image_path, 'rb') as f:
            image = f.read()
        
        # Create AWS client
        self.logger.debug("Creating boto client")
        client = get_authenticated_client(self.config, self.logger,'textract')
        try:
            self.logger.info("Sending Textract request for {}".format(image_path))
            response = client.detect_document_text(
                Document={
                    'Bytes':image
                },
            )
        except Exception as e:
            self.logger.error(e)
            return []
        self.logger.debug("Received Textract response")

        self.cache.write_to_cache(image_path, image, response)
        return response

        

        