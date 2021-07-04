import configparser
import logging
import os
import io

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
# From PDFInterpreter import both PDFResourceManager and PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
# Import this to raise exception whenever text extraction from PDF is not allowed
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar
from pdfminer.converter import PDFPageAggregator

from pdf2image import convert_from_path

import unicodedata

import cv2
import numpy as np

from data_loaders.data_loader_interface import DataLoaderInterface
from utils.datatypes import Line, Bound, Source, Section
from utils.cache import CacheManager

from typing import List, Union, Any, Optional


class PDFLoader(DataLoaderInterface):

	def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
		self.config = config
		self.logger = logger.getChild("pdf_loader")
		self.cache = CacheManager(self.logger, config.get("default", "cache"), 'pdf')


	@staticmethod
	def get_filetypes() -> List[str]:
		'''Returns a list of file types supported by this data loader'''
		return ["pdf"]

	def load_data_from_file(self, filepath: str) -> Source:
		'''Reads file and extracts lines of texts. Returns one section per page'''

		if not os.path.exists(filepath):
			self.logger.error("File {} does not exist".format(filepath))
			return None

		# Check if we've processed this image before
		cached_response = self.__load_from_cache(filepath)
		if cached_response:
			self.logger.info("Retrieving cached result for {}".format(filepath))
			return cached_response

		with open(filepath, 'rb') as f:
			parser = PDFParser(f)
			document = PDFDocument(parser)

			if not document.is_extractable:
				raise PDFTextExtractionNotAllowed
			
			rsrcmgr = PDFResourceManager()
			laparams = LAParams(all_texts=True)

			device = PDFPageAggregator(rsrcmgr, laparams=laparams)
			interpreter = PDFPageInterpreter(rsrcmgr, device)   

			line_id = 0

			# Ok now that we have everything to process a pdf document, lets process it page by page
			pages = []
			for page in PDFPage.create_pages(document):
				page_text = Section()
				# As the interpreter processes the page stored in PDFDocument object
				interpreter.process_page(page)
				y_size = page.mediabox[3]
				x_size = page.mediabox[2]
				# The device renders the layout from interpreter
				layout = device.get_result()

				lines = []
				for lt in layout:
					lines += self.__recursive_filter_to_lines(lt)

				for l in lines:
					new_lines = self.__layout_to_line(line_id, l, x_size, y_size)
					line_id += len(new_lines)

					for l in new_lines:
						page_text.add_line(l, sort=False)

				page_text.sort()
				pages.append(page_text)
						
			#get pages as images
			images = convert_from_path(filepath)
			#convert to cv2
			images = [cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR) for im in images]
			
			source = Source(
				filepath=filepath,
				name=filepath.split(os.pathsep)[-1],
				num_pages = len(pages),
				pages = pages,
				images = images,
				authors = None,
				url = None
			)

			self.__cache_result(source)
			
			return source

	def __recursive_filter_to_lines(self, lt: Any) -> List[LTTextLine]:
		lines = []
		if isinstance(lt, LTChar):
			return []

		if isinstance(lt, LTTextLine):
			lines.append(lt)
		else:
			if hasattr(lt, "_objs"):
				for o in lt._objs:
					lines += self.__recursive_filter_to_lines(o)
		return lines

	def __layout_to_line(self, line_id: str, lt: Union[LTTextBox, LTTextLine], x_size: int, y_size: int) -> List[Line]:
		'''Split TextBoxes into TextLines'''
		lines = []
		if isinstance(lt, LTTextBox):
			for obj in lt._objs:
				if isinstance(obj, LTTextLine):
					lines += self.__layout_to_line(line_id, obj, x_size, y_size)
					line_id += 1
					
		elif isinstance(lt, LTTextLine):
			bound = Bound(lt.bbox[0] / x_size, (y_size - lt.bbox[1]) / y_size, 
						(lt.bbox[2] - lt.bbox[0]) / x_size, (lt.bbox[3] - lt.bbox[1])/y_size)


			text = unicodedata.normalize('NFD', lt.get_text().strip())
			### Hack to deal with some title being weirdly encoded
			escaped_text = ""
			for t in text:
				if repr(t).find("\\uf") >= 0:
					escaped_text += bytearray.fromhex(repr(t)[5:-1]).decode()
				else:
					escaped_text += t

			lines.append(Line(line_id, escaped_text, bound, []))
		
		return lines

	def __load_from_cache(self, filepath: str) -> Optional[Source]:
		'''Loads the parsed data from the cache folder'''
		if self.cache.check_cache(filepath):
			self.logger.info("Loading PDF {} from cache".format(filepath))
			byte_data, json_data = self.cache.read(filepath)
			source = Source.deserialise(byte_data, json_data)
			return source
		return None
			

	def __cache_result(self, source: Source):
		byte_data, json_data = source.serialise()
		self.cache.write(source.filepath, byte_data, json_data)
