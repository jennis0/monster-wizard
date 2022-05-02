import configparser
import logging
import os
from tqdm import tqdm

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdffont import PDFCIDFont, PDFUnicodeNotDefined, PDFTrueTypeFont

from pdf2image import convert_from_path

import unicodedata

import cv2
import numpy as np
from binascii import b2a_hex

from data_loaders.data_loader_interface import DataLoaderInterface
from utils.datatypes import Line, Bound, Source, Section

from typing import List, Optional, TextIO, Union, Any

LIGATURE_MAP = {
	"\ufb00": "ff",
	"\ufb01": "fi",
	"\ufb02": "fl",
	"\ufb03": "ffi",
	"\ufb04": "ffl",
	"\ufb05": "ft",
	"\ufb06": "st",
}

FONT_OVERRIDES = {
	"Calibri": {
		332:"ft",
		415:"ti",
		425:"t",
		427:"t",
		976:'f',
		980:"st",
	},
	"Cambria": {
		332:"ft",
		415:"ti",
		425:"t",
		427:"t",
		976:'f',
		980:"st",
	},
	"AlegrayaSans-Regular": {
		143: "f",
		145: "fi",
		155: "f"
	}
}

import json

### PDFMiner has been found to have some issues with rendering ligatures in at least one 
### pdf I tested. Here we manually override the character processing function so we can
### easily inject our own stuff - without having to modify the base library
def override_render_char(self, matrix, font, fontsize, scaling, rise, cid, ncs=None,
					graphicstate=None, logger=None):
		try:
			text = font.to_unichr(cid)
			assert isinstance(text, str), str(type(text))
		except PDFUnicodeNotDefined:
			text = self.handle_undefined_char(font, cid)
		textwidth = font.char_width(cid)
		textdisp = font.char_disp(cid)

		err = False

		if isinstance(font, PDFTrueTypeFont) or isinstance(font, PDFCIDFont):
			font_title = font.basefont.split("-")[0]

			if text == "\x00":
				if font_title in FONT_OVERRIDES and cid in FONT_OVERRIDES[font_title]:
					logger.debug("Override {} for font {}".format(cid, font.basefont))
					text = FONT_OVERRIDES[font_title][cid]
				else:
					logger.error("Failed to override {} for font {}".format(cid, font))
					err = True

		else:
			if "\x00" in text:
				logger.warning("Non tt font {} failed to parse".format(font))

		if text in LIGATURE_MAP:
			logger.debug("Swapping for {}".format(LIGATURE_MAP[text]))
			text = LIGATURE_MAP[text]

		if '\x00' in text:
			logger.error("Found missing character {}".format(cid))

		#item = LTChar(matrix, font, fontsize, scaling, rise, text, textwidth,
		#			  textdisp, ncs, graphicstate)
		item = LTChar(matrix, font, fontsize, scaling, rise, text, textwidth,
					  textdisp)
		self.cur_item.add(item)

		return item.adv

def determine_image_type (stream):
	"""Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""
	stream_first_4_bytes = stream[:4]
	file_type = None
	bytes_as_hex = b2a_hex(stream_first_4_bytes).decode()
	if bytes_as_hex.startswith('ffd8'):
		file_type = 'jpeg'
	elif bytes_as_hex == '89504e47':
		file_type = 'png'
	elif bytes_as_hex == '47494638':
		file_type = 'gif'
	elif bytes_as_hex.startswith('424d'):
		file_type = 'bmp'
	elif bytes_as_hex.startswith("4949") or bytes_as_hex.startswith("4d4d"):
		file_type = "tiff"
	else:
		file_type = "unknown"
	return file_type

class PDFLoader(DataLoaderInterface):

	def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
		self.config = config
		self.logger = logger.getChild("pdf_loader")

	def get_name(self) -> str:
		return 'pdf_loader'

	def get_filetypes(self) -> List[str]:
		'''Returns a list of file types supported by this data loader'''
		return ["pdf"]

	def load_data_from_filepath(self, filepath: str) -> Source:

		if not os.path.exists(filepath):
			self.logger.error("File {} does not exist".format(filepath))
			return None

		with open(filepath, 'rb') as f:
			return self.load_data_from_file(f, filepath)

	def load_data_from_file(self, file: Any, filepath: Optional[str]="") -> Source:
		'''Reads file and extracts lines of texts. Returns one section per page'''

		parser = PDFParser(file)
		document = PDFDocument(parser)

		if not document.is_extractable:
			raise PDFTextExtractionNotAllowed
		
		rsrcmgr = PDFResourceManager()
		laparams = LAParams(all_texts=True)

		device = PDFPageAggregator(rsrcmgr, laparams=laparams)

		### Hacky monkey patching to handle missing CID entries for various fonts
		device.render_char = lambda *args, **kwargs: override_render_char(device, *args, **kwargs, logger=self.logger)

		interpreter = PDFPageInterpreter(rsrcmgr, device)   
		
		line_id = 0
		name=os.path.basename(filepath).split(".")[0]

		pages = []
		all_images = []
		for j, page in enumerate(tqdm(PDFPage.create_pages(document))):
			page_text = Section()
			interpreter.process_page(page)

			y_size = page.mediabox[3]
			x_size = page.mediabox[2]
			layout = device.get_result()

			lines = []
			images = []
			possible_images = []
			for lt in layout:
				ls, ims = self.__recursive_filter_to_lines_and_images(lt)
				lines += ls
				possible_images += ims

			for im in possible_images:
				try:
					data = im.stream.get_data()
					type = determine_image_type(data)
					if type != 'unknown':
						images.append(data)
				except:
					self.logger.debug("Failed to load image on page {}".format(j))

			all_images.append(images)
					

			for l in lines:
				new_lines = self.__layout_to_line(line_id, l, x_size, y_size, j)
				line_id += len(new_lines)

				for l in new_lines:
					page_text.add_line(l, sort=False)

			page_text.sort()
			pages.append(page_text)
		
		source = Source(
			filepath=filepath,
			name=name,
			num_pages = len(pages),
			pages = pages,
			page_images = None,
			images = all_images,
			authors = None,
			url = None
		)
		
		return source

	def __recursive_filter_to_lines_and_images(self, lt: Any) -> List[LTTextLine]:
		lines = []
		images = []
		if isinstance(lt, LTChar):
			return [], []

		if isinstance(lt, LTTextLine):
			lines.append(lt)
		# elif isinstance(lt, LTImage):
		# 	images.append(lt)

		elif hasattr(lt, "_objs"):
			for o in lt._objs:
				ls, ims = self.__recursive_filter_to_lines_and_images(o)

				### Handle duplicate lines caused by (e.g.) outlines
				for l in ls:
					if len(lines) == 0 or l.get_text() != lines[-1].get_text() or abs(l.y1 - lines[-1].y1) > 0.1:
						lines.append(l)

				images += ims

		return lines, images

	def __layout_to_line(self, line_id: str, lt: Union[LTTextBox, LTTextLine], x_size: int, y_size: int, page:int) -> List[Line]:
		'''Split TextBoxes into TextLines'''
		lines = []
		if isinstance(lt, LTTextBox):
			for obj in lt._objs:
				self.logger.debug("\t {} - {}".format(obj, type(obj)))
				if isinstance(obj, LTTextLine):
					lines += self.__layout_to_line(line_id, obj, x_size, y_size, page)
					line_id += 1
					
		elif isinstance(lt, LTTextLine):
			bound = Bound(lt.bbox[0] / x_size, (y_size - lt.bbox[1]) / y_size, 
						(lt.bbox[2] - lt.bbox[0]) / x_size, (lt.bbox[3] - lt.bbox[1])/y_size)

			annotations = []

			### Remove very small text
			size = 0
			skip = False
			for o in lt._objs:
				if isinstance(o, LTChar):
					if o.size < 6.1:
						skip = True
					elif o.size >= 20.:
						annotations.append("very_large")
					elif o.size >= 14.:
						annotations.append("large")

					size = o.size
					break
					
			if skip:
				return lines

			text = unicodedata.normalize('NFC', lt.get_text().strip())
			### Hacks to deal with some title being weirdly encoded
			text = text.replace("\t\r", " ")
			text = " ".join(text.split())
			escaped_text = ""

			### Replace some unicode character's with more common ones to make parsing easier
			text_replacements = {
				# Normalise minus signs/hyphens
				u"\u2013":"-",
				u"\u2014":"-",
				u"\u2212":"-",
				u"\u002D":"-",
				u"\uFE63":"-",
				u"\uFF0D":"-",
				# Normalise pluses
				u"\u002B":"+",
				u"\uFF0B":"+",
				# Normalise apostrophes
				u"\u2019":"'",
				# Remove Non-breaking spaces
				"\xad":"",
				# Replace Double-hyphen with hyphen
				"--":"-"
			}

			for t in text:
				if repr(t) in LIGATURE_MAP:
					escaped_text += LIGATURE_MAP[repr(t)]
				elif repr(t).find("\\uf") >= 0:
					try:
						escaped_text += bytearray.fromhex(repr(t)[5:-1]).decode()
					except:
						try:
							escaped_text += bytearray.fromhex(repr(t)[5:-1]).decode('windows-1252')
						except Exception as e:
							self.logger.error("Exception:", e)
				else:
					if t in text_replacements:
						escaped_text += text_replacements[t]
					else:
						escaped_text += t

			self.logger.debug(text.encode("utf-8"))
			self.logger.debug("{} SIZE={}, ESCAPED={}".format(text, size, escaped_text))

			### Sometimes the text will get duplicated within a single line. Check for this
			if len(escaped_text.strip()) % 2 == 0:
				split = int(len(escaped_text.strip()) / 2)
				if escaped_text.strip()[:split] == escaped_text.strip()[split:]:
					escaped_text = escaped_text.strip()[:split]

			if escaped_text.strip() == "":
				#self.logger.debug("Empty Text: ", lt)
				return lines

			lines.append(Line(line_id, escaped_text, bound, page, annotations))
		
		return lines