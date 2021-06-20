from __future__ import annotations

import dataclasses
from typing import List

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
    text: List(str)
    bound: Bound
    attributes: List[str]

    def text_str(self, join_char: str=' ') -> str:
        '''Return the lines of text as a single piece of text with "join_char" between them'''
        return join_char.join(self.text)

    @staticmethod
    def merge(lines: List[Line]) -> Line:
        '''Merge a list of lines into a single line'''
        text = []
        bounds = []
        attribs = []
        for l in lines:
            text.append(l.text)
            attribs += l.attributes
            bounds.append(l.bound)

        return Line(text=text, bound=Bound.merge(bounds), attributes=attribs)

