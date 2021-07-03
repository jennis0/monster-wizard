from __future__ import annotations

import dataclasses
from typing import Dict, List, Any, Tuple
from enum import Enum

@dataclasses.dataclass
class Source:
    filepath: str
    name: str
    num_pages: int
    pages: List[Section]
    images: List[Any]
    authors: str
    url: str

@dataclasses.dataclass
class Bound:
    left: float
    top: float
    width: float
    height: float

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
    attributes: List[str]

    @staticmethod
    def merge(lines: List[Line], join_char=" ") -> Line:
        text = join_char.join(l.text for l in lines)
        bound = Bound.merge(l.bound for l in lines)
        attrib = []
        for l in lines:
            attrib += l.attributes
        return Line(id = lines[0].id, text=text, bound=bound, attributes=attrib)

    @staticmethod
    def from_tuple(tuple: List[Any]) -> Line:
        return Line(id="aaaaaaaaaaaaaaaaaaaa", text=tuple[0], bound=Bound.from_dict(tuple[1]), attributes=tuple[2])

    def to_tuple(self) -> List[Any]:
        return [self.text, self.bound.to_dict(), self.attributes]

class Section:
    '''Container holding multiple lines with a single bounding box'''

    class SortOrder(Enum):
        Vertical = 1
        Horizontal = 2

    def __init__(self, lines: List[Line] = None, attributes: List[str] = None, sort_order: Section.SortOrder=SortOrder.Vertical):
        self.lines = lines if lines else []
        self.ids = {l.id: l for l in self.lines}
        self.bound = Bound.merge(l.bound for l in self.lines)
        self.attributes = attributes if attributes else []
        self.sort_order = sort_order

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
            self.lines.sort(key=lambda x: x.bound.top)
        elif sort_order == Section.SortOrder.Horizontal:
            self.lines.sort(key=lambda x: x.bound.left)

    def get_line_by_id(self, line_id: str) -> Line:
        '''Returns a line by the line id'''
        return self.ids[line_id]

    def get_line_attributes(self) -> List[str]:
        '''Returns a list of all attributes attached to these lines'''
        attribs = []
        for l in self.lines:
            attribs += l.attributes
        return attribs

    def get_section_text(self, join_char="\n") -> str:
        '''Returns the total section text'''
        return join_char.join(l.text for l in self.lines)

    def __contains__(self, line: Line) -> bool:
        return line.id in self.ids

    def __len__(self) -> int:
        return len(self.lines)

