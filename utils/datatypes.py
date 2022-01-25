from __future__ import annotations

import dataclasses
from typing import Dict, List, Any, Tuple, Optional
from enum import Enum
import io
import numpy as np

@dataclasses.dataclass
class Source:
    filepath: str
    name: str
    num_pages: int
    pages: List[Section]
    images: List[List[Any]]
    page_images: List[Any]
    authors: str
    url: str

    def __str__(self):
        return "<Source file={}, num_pages={}, num_images={}>".format(self.name, len(self.pages), len(self.images))

    def serialise(self) -> Tuple[bytes, Any]:
        '''Serialise the Source data into a tuple of raw byte data and structured json'''
        meta = {
			"source": self.name,
			"authors": self.authors,
			"url": self.url,
			"filepath": self.filepath,
			"num_pages": self.num_pages,
			"pages": [s.to_tuple() for s in self.pages],
		}

		### Write images to a compressed bytestream
        ims = {}
        if self.page_images:
            for i,im in enumerate(self.page_images):
                ims["page_{}".format(i)] = im

        if self.images:
            for i,images in enumerate(self.images):
                for j,im in enumerate(images):
                    ims["page_{}_image_{}".format(i, j)] = im

        stream = io.BytesIO()
        np.savez_compressed(stream, **ims)
        stream.seek(0)
        return [stream.read(), meta]

    @staticmethod
    def deserialise(images: bytes, data: Any) -> Source:
        '''Convert serialised data back into a source'''

        ### Load images and make sure we order them correctly
        stream = io.BytesIO(images)
        image_dict = np.load(stream)

        page_images = [None for i in range(int(data["num_pages"]))]
        loaded_images = [[] for i in range(int(data["num_pages"]))]

        for k in image_dict.keys():
            if "image" in k:
                parts = k.split("_")
                page = int(parts[1])
                image_num = int(parts[3])

                while len(loaded_images[page]) <= image_num:
                    loaded_images[page].append(None)
                
                loaded_images[page][image_num] = image_dict[k]
            else:
                page_images[int(k[5:])] = image_dict[k]

        ### Load 
        s = Source(
            name=data["source"],
            authors=data["authors"],
            url=data["url"],
            filepath=data["filepath"],
            num_pages = data["num_pages"],
            pages=[Section.from_tuple(s) for s in data["pages"]],
            page_images = page_images,
            images=loaded_images
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

    @staticmethod
    def from_dict(data: Dict[str, float]) -> Bound:
        return Bound(
            left=data["left"],
            top=data["top"],
            height=data["height"],
            width=data["width"]
        )

    def to_dict(self) -> Dict[str, float]:
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
    def from_tuple(tuple: List[Any]) -> Line:
        return Line(id=str(tuple[0]), text=tuple[1], bound=Bound.from_dict(tuple[2]), page=tuple[3], attributes=tuple[4])

    def to_tuple(self) -> List[Any]:
        return [self.id, self.text, self.bound.to_dict(), self.page, self.attributes]

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

    def to_tuple(self) -> List[Any]:
        lines = [l.to_tuple() for l in self.lines]
        bound = self.bound.to_dict()
        return [lines, bound, self.attributes, self.sort_order.value, self.page]

    @staticmethod
    def from_tuple(data: Any) -> Section:
        lines = [Line.from_tuple(l) for l in data[0]]
        ids = [l.id for l in lines]
        return Section(
            lines=lines,
            ids=ids,
            bound=Bound.from_dict(data[1]),
            attributes=data[2],
            sort_order=data[3],
            page=data[4] if len(data) > 4 else -1
        )
