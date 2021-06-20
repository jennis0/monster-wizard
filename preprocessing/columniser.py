import configparser
import logging

from typing import List

from utils.datatypes import Line, Bound

class Columniser(object):
    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        self.left_offset_leeway = config.get("columniser", "left_leeway", fallback=5)
        self.right_offset_leeway = config.get("columniser", "right_leeway", fallback=30)
        self.max_vertical_gap = config.get("columniser", "max_vertical_gap", fallback=50)

    def __split_lines_into_columns(self, lines: List[Line]) -> List[List[Line]]:
        '''Map lines into columns based on their top left point'''
        columns = []
        column_bounds = []

        for line in lines:
            placed=False
            for i,cb in enumerate(column_bounds):
                dist = line.bound.left - cb.left
                # Does the line start within a reasonable distance of the column start point?
                if dist > -self.left_offset_leeway and dist < self.right_offset_leeway:
                    
                    # # Is the line within a reasonable vertical distance?
                    # if abs(line.bound.top - cb.bottom()) < self.max_vertical_gap:

                    # Yes? Well append the line to the column
                    columns[i].append(line)
                    placed=True
                    column_bounds[i] = Bound.merge([cb, line.bound])
                    break

            # No matching columns? Create a new one
            if not placed:
                columns.append([line])
                column_bounds.append(line.bound)

        #Sort columns into left->right order
        columns = [[c, Bound.merge([l.bound for l in c])] for c in columns]
        columns.sort(key=lambda x: x[1].bound.left)

        return columns

    def __merge_contained_columns(self, columns: List[List[Line]]) -> List[List[Line]]:
        '''Merge columns that are contained within another'''
        ignore_columns = []
        for i,col1 in enumerate(columns):
            if i in ignore_columns:
                continue
            for j,col2 in enumerate(columns):
                if i == j or j in ignore_columns:
                    continue
                #Check if bound of the column is within another (use left offset to allow for minor variations)
                if col2[1].left > col1[1].left - self.left_offset_leeway:
                    if col2[1].right < col2[1].right + self.left_offset_leeway:
                        col1[0] += col2[0]
                        col1[1].bound = Bound.merge(col1[1], col2[1])
                        ignore_columns.append(j)

        columns = [c for i,c in enumerate(columns) if i not in ignore_columns]

        #Sort lines within a column vertically
        for c in columns:
            c[0].sort(key = lambda x: x.bound.top)

        return columns


    def find_columns(self, lines: List[Line]) -> List[List[Line]]:
        '''Splits lines into columns based on the starting point of lines'''
 
        columns = self.__split_lines_into_columns(lines)
        columns = self.__merge_contained_columns(columns)

        #Merge lines on the same line
        for j,c in enumerate(columns):
            new_lines = []
            current_lines = [c[0][0]]
            for i in range(1, len(c[0])):
                first_bottom = current_lines[0][1]["top"] + current_lines[0][1]["height"]
                candidate_bottom = c[0][i][1]["top"] + c[0][i][1]["height"]
                if (c[0][i][1]["top"] >= current_lines[0][1]["top"] - 5):
                    if (candidate_bottom <= first_bottom + 5):
                        current_lines.append(c[0][i])
                        continue

                if len(current_lines) < 2:
                    new_lines.append(current_lines[0])
                else:
                    current_lines.sort(key=lambda x: x[1]["left"])
                    merge = True
                    for k in range(1, len(current_lines) - 1):
                        if abs(current_lines[k][1]["left"] - (current_lines[k-1][1]["left"] + current_lines[k-1][1]["width"])) > 50:
                            merge = False
                            break
                    if merge:
                        new_lines.append(self.merge_lines(current_lines, join_char=" "))
                        current_lines = []
                    else:
                        new_lines += current_lines
                current_lines = [c[0][i]]

            if len(current_lines) < 2:
                new_lines.append(current_lines[0])
            else:
                current_lines.sort(key=lambda x: x[1]["left"])
                merge = True
                for k in range(1, len(current_lines) - 1):
                    if abs(current_lines[k][1]["left"] - current_lines[k-1][1]["left"]) > 200:
                        merge = False
                        break
                if merge:
                    new_lines.append(self.merge_lines(current_lines, join_char="\t"))
                else:
                    new_lines += current_lines

            columns[j][0] = new_lines

        for col in columns:
            to_old_format = lambda x: [x.text[0], {'left':x.bound.left, 'top':x.bound.top, 'width':x.bound.width, 'height':x.bound.height}]
            col[0] = [to_old_format(l) for l in col[0]]

        return columns