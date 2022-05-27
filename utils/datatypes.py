from __future__ import annotations
from base64 import b64decode, b64encode

import dataclasses
from typing import Dict, List, Any, Tuple, Optional
from enum import Enum
import io
from uuid import uuid4
import numpy as np

@dataclasses.dataclass
class Source:
    filepath: str
    name: str
    num_pages: int
    pages: List[Section]
    images: List[PDFImage]
    background_text: List[Section]
    statblocks: List[Dict[str, Any]]
    page_images: List[PDFImage]
    authors: str
    url: str

    def __str__(self):
        return "<Source file={}, num_pages={}, num_images={}>".format(self.name, len(self.pages), len(self.images))

    def serialise(self) -> Dict[str, Any]:
        '''Serialise the Source data into a tuple of raw byte data and structured json'''
        object = {
			"source": self.name,
			"authors": self.authors,
			"url": self.url,
			"filepath": self.filepath,
			"num_pages": self.num_pages,
			"pages": [s.serialise() for s in self.pages],
            "images": [i.serialise() for i in self.images],
            "background_text": [s.serialise() for s in self.background_text],
            "page_images": [i.serialise() for i in self.page_images],
            "statblocks": self.statblocks
		}
        return object

    @staticmethod
    def deserialise(object: Dict[str, Any]) -> Source:
        '''Convert serialised data back into a source'''
        s = Source(
            name=object["source"],
            authors=object["authors"],
            url=object["url"],
            filepath=object["filepath"],
            num_pages = object["num_pages"],
            pages=[Section.deserialise(s) for s in object["pages"]],
            images=[PDFImage.deserialise(i) for i in object["images"]],
            background_text=[Section.deserialise(s) for s in object["background_text"]],
            page_images = [PDFImage.deserialise(i) for i in object["page_images"]],
            statblocks=object["statblocks"]
        )
        return s


@dataclasses.dataclass
class Bound:
    left: float
    top: float
    width: float
    height: float

    def __str__(self):
        return f"Bound<{self.left}, {self.top}, {self.right()}, {self.bottom()}>"

    def right(self) -> float:
        '''Returns right edge of bounding box'''
        return self.left + self.width

    def bottom(self) -> float:
        '''Returns top of bounding box'''
        return self.top + self.height

    def center(self) -> Tuple[float, float]:
        return (self.left + 0.5*self.width, self.top+0.5*self.height)

    @staticmethod
    def overlap(b1, b2):
        x_overlap = max(0, min(b1.right(), b2.right()) - max(b1.left, b2.left))
        y_overlap = max(0, min(b1.bottom(), b2.bottom()) - max(b1.top, b2.top))
        return x_overlap * y_overlap

    @staticmethod
    def distance(b1, b2):
        return np.linalg.norm(b1.center(), b2.center())

    @staticmethod
    def deserialise(data: Dict[str, float]) -> Bound:
        return Bound(
            left=data["left"],
            top=data["top"],
            height=data["height"],
            width=data["width"]
        )

    def serialise(self) -> Dict[str, float]:
        return {
            "left":self.left,
            "top":self.top,
            "height":self.height,
            "width":self.width
        }

    @staticmethod
    def merge(bounds: List[Bound]) -> Bound:
        '''Merge a set of bounds into a single larger bound'''
        left = 10000000
        right = 0
        top = 10000000
        bottom = 0
        for b in bounds:
            if b.left < left:
                left = b.left
            if b.right() > right:
                right = b.right()
            if b.top < top:
                top = b.top
            if b.bottom() > bottom:
                bottom = b.bottom()

        return Bound(left=left, top=top, width=right-left, height=bottom-top)

@dataclasses.dataclass
class Line:
    '''Container class storing one or more lines of text alongside their attribues and bounding box'''
    id: str
    text: str
    bound: Bound
    page: int
    attributes: List[str]

    def __init__(self, text: str, bound: Bound, page: int, attributes: List[str], id:str):
        self.id = uuid4().hex if not id else id
        self.text = text
        self.bound = bound
        self.page = page
        self.attributes = attributes

    @staticmethod
    def merge(lines: List[Line], join_char=" ") -> Line:
        text = join_char.join(l.text for l in lines)
        bound = Bound.merge(l.bound for l in lines)
        attrib = []
        # Sort lines
        lines.sort(key=lambda l: l.bound.left)

        for l in lines:
            attrib += l.attributes
        return Line(id = lines[0].id, text=text, bound=bound, page=lines[0].page, attributes=attrib)

    @staticmethod
    def deserialise(object: Dict[str, Any]) -> Line:
        return Line(
            id=object["id"], 
            text=object["text"], 
            bound=Bound.deserialise(object["bound"]), 
            page=object["page"], 
            attributes=object["attributes"]
        )

    def serialise(self) -> List[Any]:
        return {"id":self.id, "text":self.text, "bound":self.bound.serialise(), "page":self.page, "attributes":self.attributes}

@dataclasses.dataclass
class PDFImage:
    id: str
    data: bytes
    bound:Bound
    page: int
    attributes: List[str]

    def __init__(self, data: str, bound: Bound, page: int, attributes: List[str], id:str=None):
        self.id = uuid4().hex if not id else id
        self.data = data
        self.bound = bound
        self.page = page
        self.attributes = attributes

    def serialise(self):
        return {"id":self.id, "data":self.data.decode("utf-8"), "page":self.page, "bound":self.bound.serialise(), "attributes":self.attributes}

    @staticmethod
    def deserialise(object: Dict[str, Any]):
        return PDFImage(
            id=object["id"], 
            data=object["data"].encode("utf-8"), 
            bound=Bound.deserialise(object["bound"]), 
            page=object["page"], 
            attributes=object["attributes"]
        )



class Section:
    '''Container holding multiple lines with a single bounding box'''

    class SortOrder(Enum):
        NoSort = 0
        Vertical = 1
        Horizontal = 2

    def __init__(self, lines: List[Line] = None, attributes: List[str] = None, 
            sort_order: Section.SortOrder=SortOrder.Vertical, 
            bound: Optional[Bound]=None, ids: Optional[List[str]]=None, page=-1):
        self.lines = lines if lines else []
        self.ids = ids if ids else {l.id: l for l in self.lines}
        self.bound = bound if bound else Bound.merge(l.bound for l in self.lines)
        self.page = page
        self.attributes = attributes if attributes else []
        self.sort_order = sort_order

        if self.page == -1 and len(self.lines) > 0:
            self.page = min([l.page for l in self.lines])

    def is_empty(self) -> bool:
        '''Returns true if this section contains no lines'''
        return len(self.lines) == 0

    def add_line(self, line: Line, sort: bool=True, sort_order: Section.SortOrder=None) -> None:
        '''Add a line to the section. Will dynamically update the bound'''
        #Ignore if this line is already present
        if line.id in self.ids:
            return

        self.lines.append(line)
        self.ids[line.id] = line
        self.bound = Bound.merge([self.bound, line.bound])

        if sort:
            self.sort(sort_order)

    def add_section(self, section: Section, sort: bool=True, sort_order: Section.SortOrder=None) -> None:
        '''Add all lines from another section to this one'''
        for line in section.lines:
            self.add_line(line, sort=False)
        self.attributes += section.attributes
        if sort:
            self.sort(sort_order=sort_order)

        if self.page == -1:
            self.page = section.page
        elif section.page != -1:
            self.page = min(self.page, section.page)

    def remove_line(self, line: Line) -> None:
        '''Delete a line from this section. Expensive!'''
        keep_lines = []
        for l in self.lines:
            if l.id != line.id:
                keep_lines.append(l)
        self.ids.pop(line.id)

        self.lines = keep_lines
        self.bound = Bound.merge([l.bound for l in self.lines])

    def sort(self, sort_order: Section.SortOrder=None) -> None:
        '''Sort lines within section'''
        if sort_order == None:
            sort_order = self.sort_order

        if sort_order == Section.SortOrder.Vertical:
            self.lines.sort(key=lambda x: x.bound.top + 100*self.page)
        elif sort_order == Section.SortOrder.Horizontal:
            self.lines.sort(key=lambda x: x.bound.left + 100*self.page)
        elif sort_order == Section.SortOrder.NoSort:
            pass

    def get_line_by_id(self, line_id: str) -> Optional[Line]:
        '''Returns a line by the line id'''
        if line_id in self.ids:
            return self.ids[line_id]
        else:
            return None

    def get_line_attributes(self) -> List[str]:
        '''Returns a list of all attributes attached to these lines'''
        attribs = []
        for l in self.lines:
            attribs += l.attributes
        return attribs

    def get_section_text(self, join_char="\n") -> str:
        '''Returns the total section text'''
        text = ""
        for i in range(len(self.lines)):
            if len(self.lines[i].text) > 0 and self.lines[i].text[-1] == "-":
                text += self.lines[i].text[:-1]
            else:
                text += self.lines[i].text + join_char
        return text

    def __contains__(self, line: Line) -> bool:
        return line.id in self.ids

    def __len__(self) -> int:
        return len(self.lines)

    def serialise(self) -> List[Any]:
        return {"lines":[l.serialise() for l in self.lines], 
                "bound":self.bound.serialise(), 
                "attributes":self.attributes, 
                "sort":self.sort_order.value, 
                "page":self.page
        }

    @staticmethod
    def deserialise(object: Dict[str, Any]) -> Section:
        lines = [Line.deserialise(l) for l in object["lines"]]
        ids = [l.id for l in lines]
        return Section(
            lines=lines,
            ids=ids,
            bound=Bound.deserialise(object["bound"]),
            attributes=object["attributes"],
            sort_order=Section.SortOrder(object["sort"]),
            page=object["page"]
        )
