import configparser
import io
import logging
from optparse import Option
import os
import traceback
import base64
from uuid import uuid4
from matplotlib import pyplot as plt
from tqdm import tqdm

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter, resolve1
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar, LTImage, LTFigure
from pdfminer.converter import PDFPageAggregator
from pdfminer.image import ImageWriter
from pdfminer.pdffont import PDFCIDFont, PDFUnicodeNotDefined, PDFTrueTypeFont

from PIL import Image, ImageCms

from pdf2image import convert_from_bytes

import unicodedata

import cv2
import numpy as np
from binascii import b2a_hex

from ..data_loaders.data_loader_interface import DataLoaderInterface
from ..utils.datatypes import Line, Bound, PDFImage, Source, Section

from typing import List, Optional, Union, Any, Tuple

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

def fixed_get_filters(self) -> List[Tuple[Any, Any]]:
        filters = self.get_any(("F", "Filter"))
        params = self.get_any(("DP", "DecodeParms", "FDecodeParms"), {})
        if not filters:
            return []
        if not isinstance(filters, list):
            filters = [filters]
        if not isinstance(params, list):
            # Make sure the parameters list is the same as filters.
            params = [params] * len(filters)
        # resolve filter if possible
        _filters = []
        for fltr in filters:
            if hasattr(fltr, "resolve"):
                fltr = fltr.resolve()
                try:
                    fltr = fltr[0]
                except:
                    pass
            _filters.append(fltr)
        # return list solves https://github.com/pdfminer/pdfminer.six/issues/15
        return list(zip(_filters, params))



### Convert a PIL image into a base64-encoded WebP image.
def image_to_webp_b64(image: Image) -> bytes:
		buffer = io.BytesIO()
		image.save(buffer, format="WEBP")
		return base64.b64encode(buffer.getvalue())

def handle_raw_image(image: LTImage) -> Image:
	"""Save an image without encoding, just bytes. Modified from https://github.com/pdfminer/pdfminer.six/blob/master/pdfminer/image.py"""
	width, height = image.srcsize
	channels = len(image.stream.get_data()) / width / height / (image.bits / 8)

	mode = "RGB"
	if image.bits == 1:
		mode = "1"
	elif image.bits == 8 and channels == 1:
		mode = "L"
	elif image.bits == 8 and channels == 3:
		mode = "RGB"
	elif image.bits == 8 and channels == 4:
		mode = "CMYK"

	img = Image.frombytes(mode, image.srcsize, image.stream.get_data(), "raw")
	return img

def convert_lt_to_pil(img: LTImage, logger: logging.Logger):
	### Handle bug caused by some FlatDecodes not being resolved correctly
	img.stream.get_filters = lambda: fixed_get_filters(img.stream)
	filters = img.stream.get_filters()
	logger.debug(f"Found image with filters {filters}")
	if filters[-1][0].name == "FlateDecode":
		return handle_raw_image(img)
	else:
		#image_type = determine_image_type(image_data)
		image_data = img.stream.get_data()
		return Image.open(io.BytesIO(image_data))	

def handle_lt_image(im: LTImage, logger:logging.Logger) -> Optional[bytes]:
	created_image = convert_lt_to_pil(im, logger)
	transparency_mask = im.stream.get_any(["SMask"])
	if transparency_mask is not None:
		transparency_mask = transparency_mask.resolve()
		if transparency_mask:
			try:
				transparency_mask = LTImage(uuid4(), transparency_mask, im.bbox)
				mask_image = convert_lt_to_pil(transparency_mask, logger)
				mask_image = mask_image.resize(size=(created_image.width, created_image.height))
				created_image.putalpha(mask_image)
			except:
				logger.warning("Failed to create transparency mask")
				pass

	return image_to_webp_b64(created_image)
	

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

		item = LTChar(matrix, font, fontsize, scaling, rise, text, textwidth,
					  textdisp, ncs, graphicstate)
		# item = LTChar(matrix, font, fontsize, scaling, rise, text, textwidth,
		# 			  textdisp)
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
	elif bytes_as_hex.startswith("52494646"):
		file_type = "webp"
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

	def load_data_from_filepath(self, filepath: str, state:Optional[Any] = None) -> Source:

		if not os.path.exists(filepath):
			self.logger.error("File {} does not exist".format(filepath))
			return None

		with open(filepath, 'rb') as f:
			return self.load_data_from_file(f, filepath, state=state)

	def load_data_from_file(self, file: Any, filepath: Optional[str]="", state: Optional[Any]=None) -> Source:
		'''Reads file and extracts lines of texts. Returns one section per page'''

		parser = PDFParser(file)
		document = PDFDocument(parser)

		title = None
		author = None
		if len(document.info) > 0:
			if "Title" in document.info:
				title = document.info["Title"]
			if "Author" in document.info:
				author = document.info["Author"]

		if not document.is_extractable:
			raise PDFTextExtractionNotAllowed
		
		rsrcmgr = PDFResourceManager()
		laparams = LAParams(all_texts=True)

		device = PDFPageAggregator(rsrcmgr, laparams=laparams)

		### Hacky monkey patching to handle missing CID entries for various fonts
		device.render_char = lambda *args, **kwargs: override_render_char(device, *args, **kwargs, logger=self.logger)

		interpreter = PDFPageInterpreter(rsrcmgr, device)   
		
		line_id = 0
		name= title if title else os.path.basename(filepath).split(".")[0]
		authors = [author]

		pages = []
		images = []
		num_pages = resolve1(document.catalog['Pages'])['Count']
		for j, page in enumerate(tqdm(PDFPage.create_pages(document))):

			if state:
				state["progress"] = [j, num_pages]

			page_text = Section()
			interpreter.process_page(page)

			y_size = page.mediabox[3]
			x_size = page.mediabox[2]
			layout = device.get_result()

			lines = []
			possible_images = []
			for lt in layout:
				ls, ims = self.__recursive_filter_to_lines_and_images(lt)
				lines += ls
				possible_images += ims

			for im in possible_images:
				try:
					image_data = handle_lt_image(im, self.logger)
					if image_data:
						images.append(
							PDFImage(
								data=image_data,
								bound=self.__bbox_to_bound(im.bbox, x_size, y_size),
								page=j+1,
								attributes=[]
							)
						)
				except Exception as e:
					traceback.print_exc()
					self.logger.warning("Failed to load image on page {} with error {}".format(j+1, e))			

			for l in lines:
				new_lines = self.__layout_to_line(line_id, l, x_size, y_size, j+1)
				line_id += len(new_lines)

				for l in new_lines:
					page_text.add_line(l, sort=False)

			page_text.sort()
			pages.append(page_text)
		
		#Get frontpage
		file.seek(0)
		frontpage_data = convert_from_bytes(file.read(), size=1080, single_file=True)
		img_str = image_to_webp_b64(frontpage_data[0])
		frontpage = PDFImage(
			img_str, 
			Bound(0, 0, 1, 1),
			page=0,
			attributes=[]
		)

		self.apply_size_labels(pages)

		source = Source(
			filepath=filepath,
			name=name,
			num_pages = len(pages),
			pages = pages,
			page_images = [frontpage],
			images = images,
			authors = authors,
			background_text=[],
			statblocks=[],
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
		elif isinstance(lt, LTImage):
			images.append(lt)

		if hasattr(lt, "_objs"):
			for o in lt._objs:
				ls, ims = self.__recursive_filter_to_lines_and_images(o)

				### Handle duplicate lines caused by (e.g.) outlines
				for l in ls:
					if len(lines) == 0 or l.get_text() != lines[-1].get_text() or abs(l.y1 - lines[-1].y1) > 0.1:
						lines.append(l)

				images += ims

		return lines, images

	def __bbox_to_bound(self, bbox, x_size, y_size):
		return Bound(bbox[0] / x_size, (y_size - bbox[3]) / y_size, 
						min(1., (bbox[2] - bbox[0]) / x_size), min(1.,(bbox[3] - bbox[1])/y_size))

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
			bound = self.__bbox_to_bound(lt.bbox, x_size, y_size)

			annotations = []

			### Remove very small text
			size = 0
			skip = False
			for o in lt._objs:
				if isinstance(o, LTChar):
					annotations.append(f"size:{round(o.size)}")
					if o.size < 6.1:
						skip = True
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

			lines.append(Line(text=escaped_text, bound=bound, page=page, attributes=annotations, id=line_id))
		
		return lines

	def apply_size_labels(self, pages):
		line_sizes = []
		for p in pages:
			for l in p.lines:
				for a in l.attributes:
					vals = a.split(":")
					if vals[0] == "size":
						line_sizes.append(round(float(vals[1])))
		
		font_range = np.linspace(0, 30, 31)
		x = np.histogram(line_sizes, font_range, density=True)[0]
		standard = np.argmax(x)
		large_boundry = -1
		vl_boundry = -1
		for i in range(standard, 30):
			if x[i] <= 0.01 and x[i-1] >= 0.01:
				if large_boundry < 0:
					large_boundry = font_range[i]
				else:
					vl_boundry = font_range[i]
					break

		self.logger.debug(f"Set font size range to Standard={font_range[standard]}, Large={large_boundry}, Very Large={vl_boundry}")

		for p in pages:
			for l in p.lines:
				for a in l.attributes:
					vals = a.split(":")
					if vals[0] == "size":
						if float(vals[1]) > large_boundry:
							l.attributes.append("large")
						if (float(vals[1])) > vl_boundry:
							l.attributes.append("very_large")
