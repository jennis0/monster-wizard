import configparser
import logging
import re
from typing import List

from ..utils.datatypes import Line, Section

class Columniser(object):
    '''Take a set of text lines and try to figure out whether they should be arranged in columns'''
    
    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        self.left_offset_leeway = config.get("columniser", "left_leeway", fallback=0.01)
        self.right_offset_leeway = config.get("columniser", "right_leeway", fallback=0.15)
        self.max_vertical_gap = config.get("columniser", "max_vertical_gap", fallback=0.05)
        self.max_horizontal_gap = config.get("columniser", "max_horizontal_gap", fallback=0.1)
        self.merge_leeway = config.get('columniser', 'merge_leeway', fallback=0.1)
        self.fuzzyness = config.get("columniser", "fuzzyness", fallback=0.01)

        self.logger = logger.getChild("columniser")

        self.logger.debug("Configure columniser with parameters:")
        self.logger.debug("\tleft_offset_leeway={}".format(self.left_offset_leeway))
        self.logger.debug("\tright_offset_leeway={}".format(self.right_offset_leeway))
        self.logger.debug("\tmax_vertical_gap={}".format(self.max_vertical_gap))
        self.logger.debug("\tfuzzyness={}".format(self.fuzzyness))

    def __split_lines_into_columns(self, lines: List[Line]) -> List[Section]:
        '''Map lines into columns based on their top left point'''
        
        columns = []#[Section([lines[0]])]

        for line in lines:
            self.logger.debug(line)
            self.logger.debug(columns)

            #Filter out anything that approaches page width - is there a better way to do this to handle single column content?
            if line.bound.width > 0.7:
                self.logger.debug(f"Throwing away line {line} due to width")
                continue

            placed=False

            ### First try to line up start of line with an existing column
            for i,cb in enumerate(columns):
                dist = line.bound.left - cb.bound.left
                # Does the line start within a reasonable distance of the column start point?
                if dist > -self.left_offset_leeway and dist < self.right_offset_leeway:
                    if abs(line.bound.top - cb.bound.bottom()) < self.max_horizontal_gap:

                        # Yes? Well append the line to the column
                        columns[i].add_line(line, sort=False)
                        placed=True
                        break
            
            if placed:
                continue

            ### If this fails, does the line fit within another column?
            for i,cb in enumerate(columns):
                dist = line.bound.left - cb.bound.left
                rdist = line.bound.right() - cb.bound.right()
                if dist > -self.left_offset_leeway and rdist < self.left_offset_leeway:
                    if abs(line.bound.top - cb.bound.bottom()) < self.max_horizontal_gap:

                        # Yes? Well append the line to the column
                        columns[i].add_line(line, sort=False)
                        placed=True
                        break

            # No matching columns? Create a new one
            if not placed:
                columns.append(Section([line], sort_order=Section.SortOrder.Vertical))

        #Sort column lines into top->bottom and columns into left->right order
        for c in columns:
            c.sort()

        columns.sort(key=lambda x: x.bound.left)

        return columns

    def __merge_contained_columns(self, columns: List[Section]) -> List[Section]:
        '''Merge columns that are contained within another'''
        ignore_columns = []
        for i,col1 in enumerate(columns):
            if i in ignore_columns:
                continue
            for j,col2 in enumerate(columns):
                if i == j or j in ignore_columns:
                    continue
                #Check if bound of the column is within another (use left offset to allow for minor variations)
                if col2.bound.left > col1.bound.left - self.merge_leeway:
                    if col2.bound.right() < col1.bound.right() + self.merge_leeway:
                        col1.add_section(col2, sort=False) 
                        ignore_columns.append(j)

        columns = [c for i,c in enumerate(columns) if i not in ignore_columns]

        #Sort lines within a column vertically
        for c in columns:
            c.sort()

        return columns


    def __merge_split_lines(self, column: Section) -> Section:
        '''Combines lines within a column that are on the same horizontal line'''
        new_column = Section([])
        candidate_lines = [column.lines[0]]

        for i in range(1, len(column.lines)):
            line = column.lines[i]
            first_bottom = candidate_lines[0].bound.bottom()
            first_top = candidate_lines[0].bound.top
            first_height = candidate_lines[0].bound.height
            candidate_bottom = line.bound.bottom()
            candidate_top = line.bound.top

            # Is the tested line aligned with the first
            if (candidate_top >= first_top - self.fuzzyness):
                if (candidate_bottom <= first_bottom + self.fuzzyness):
                    if (abs(line.bound.height - first_height)/first_height < 0.1):
                        candidate_lines.append(line)
                        # Continue looking for more aligned lines
                        continue

            # Current line is not aligned so merge previous ones
            for l in self.__attempt_to_merge_lines(candidate_lines):
                new_column.add_line(l)

            candidate_lines = [column.lines[i]]

        # Handle final iteration of loop
        for l in self.__attempt_to_merge_lines(candidate_lines):
            new_column.add_line(l)

        return new_column

    def __attempt_to_merge_lines(self, candidates: List[Line]) -> List[Line]:
        '''Merge candidate lines into a single line, provided they are close enough'''
        candidates.sort(key=lambda x: x.bound.left)

        if len(candidates) == 0:
            return []

        if len(candidates) == 1:
            return candidates

        is_array_value = re.compile("^(\d+\s*|\(\s*[+\-–]\d+\)\s*){1,12}$", re.IGNORECASE)
        is_array_title = re.compile("^((?:(str|wis|con|int|dex|cha)\s*){1,6})$", re.IGNORECASE)


        merged = []
        to_merge = [candidates[0]]
        in_title = is_array_title.match(candidates[0].text.strip()) is not None
        in_value = is_array_value.match(candidates[0].text.strip()) is not None

        for i in range(1, len(candidates)):
            l = candidates[i]

            #Hack to avoid merging titles
            array_title = is_array_title.match(l.text.strip()) is not None
            array_value = is_array_value.match(l.text.strip()) is not None

            #Entering a title or value string so merge anything remaining
            if not in_title and not in_value and (array_title or array_value):
                merged.append(Line.merge(to_merge))
                to_merge = [l]
                in_title = array_title
                in_value = array_value
                continue
            #Still within a title or value string
            elif (in_title and array_title) or (in_value and array_value):
                to_merge.append(l)
                continue
            #Exiting a title or value string
            elif (in_title and not array_title) or (in_value and not array_value):
                merged.append(Line.merge(to_merge))
                to_merge = [l]
                in_title = array_title
                in_value = array_value
                continue
     
            #Don't want to merge if there is a large horizontal gap between the lines (could be missed columns)
            # if l.bound.left - to_merge[-1].bound.right() > self.max_horizontal_gap:
            #     merged.append(Line.merge(to_merge))
            #     to_merge = [l]
            # else:
            #     to_merge.append(l)

            merged.append(Line.merge(to_merge))
            to_merge = [l]

        if len(to_merge) > 0:
            merged.append(Line.merge(to_merge))

        return merged

    def find_columns(self, lines: List[Line]) -> List[Section]:
        '''Splits lines into columns based on the starting point of lines'''
        self.logger.debug("Received {} lines".format(len(lines)))
 
        columns = self.__split_lines_into_columns(lines)
        self.logger.debug("columns")
        self.logger.debug("Initial pass found {} columns".format(len(columns)))
        if self.logger.level <= logging.DEBUG:
            for i, c in enumerate(columns):
                self.logger.debug("\tCol {}: Length {}".format(i, len(c)))

        columns = self.__merge_contained_columns(columns)

        self.logger.debug("{} columns remain after column merging".format(len(columns)))

        #Merge lines on the same line
        for i,c in enumerate(columns):
            pre_len = len(c)
            columns[i] = self.__merge_split_lines(c)
            self.logger.debug("\tCol {}: {} -> {} lines after merging".format(i, pre_len, len(columns[i])))

        return columns