import os
from dataclasses import dataclass
from typing import Any, List
from PIL import Image

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter, resolve1
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar, LTImage, LTFigure, LTAnno
from pdfminer.pdffont import PDFCIDFont, PDFUnicodeNotDefined, PDFTrueTypeFont


class ImageStore:

    def __init__(self):
        self.images = []
        self.hashes = {}

    def add(self, image: Image) -> int:
        self.images.append(Image)
        return len(self.images) - 1

    def get(self, key: int) -> Image:
        return self.images[key]


class Font:
    def __init__(self, title: str, size: int):
        self.font = title
        self.size = size

        parts = title.split("-")
        if len(parts) == 2:
            self.family = parts[0]    
            self.bold = 'bd' in parts[1] or 'bold' in parts[1] or 'semibold' in parts[1]
            self.italic = 'italic' in parts[1]
        else:
            self.family = title
            self.bold = False
            self.italic = False

class FontStore:

    def __init__(self):
        self.fonts = []

    def add(self, font:Font) -> int:
        try:
            result = self.fonts.index(font)
            return result
        except ValueError:
            self.fonts.append(font)
            return len(self.fonts) - 1

    def get(self, key: int) -> Font:
        return self.fonts[key]
        
        

@dataclass
class Page:
    pagenumber: int
    text: List[Any]
    images: List[int]

@dataclass
class Document:
    title: str
    author: str
    pages: List[Page]
    images: ImageStore
    fonts: FontStore


class DocumentParser:

    def __init__(self, config):
        self.config = config

    def __create_page_iterator(self, config: Any, document: PDFDocument):


    def parse(self, filepath: os.PathLike):

