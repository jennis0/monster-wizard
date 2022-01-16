import configparser
import logging

from typing import List, Union
from utils.datatypes import Section

class StatblockBuilder(object):
    '''Statblock builder takes annotated line clusters and groups them into statblocks'''

    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("builder")

    def can_be_continuation(self, current_tags: List[str], new_tags: List[str]) -> bool:
        '''Check whether the statblock would make logical sense if we combined the two candidate statblocks 
        based on their contained parts'''

        if 'sb_skip' in new_tags:
            return False

        current_tags = [t for t in current_tags if t.startswith("sb_")]
        new_tags = [t for t in new_tags if t.startswith("sb_")]
        

        if len(current_tags) == 0:
            return False

        if len(new_tags) == 0:
            return False

        tag_index_mapping = {
            "sb_start":0,
            "sb_header":1,
            "sb_defence_block":2,
            "sb_array_title":3,
            "sb_array_value":4,
            "sb_flavour_block":5,
            "sb_action_block":6,
            "sb_legendary_action_block":7,
            "sb_lair_block":8,
            "sb_part":8,
            "sb_part_weak":8
        }

        last_tag = max(tag_index_mapping[t] if "sb_part" not in t else 0 for t in current_tags)
        next_tag = min(tag_index_mapping[t] for t in new_tags)

        ### Only allow lair actions if we've already seen legendary actions
        if "sb_lair_block" in new_tags\
             and ("sb_legendary_action_block" not in new_tags and "sb_legendary_action_block" not in current_tags):
             return False

        return next_tag >= last_tag

    def merge_statblocks(self, statblocks: List[Section]) -> List[Section]:
        merges = []
        used = []

        for i in range(len(statblocks)):
            s = statblocks[i]
            if i in used:
                continue

            if "sb_start" not in s.attributes:
                continue

            ### Allow backwards merging... this might be a terrible idea but it picks up
            ### lair actions formatted below a split block
            for j in range(len(statblocks)):
                if j <= i or j in used:
                    continue

                test_block = statblocks[j]

                #Ignore blocks in the same column
                if abs(s.bound.left - test_block.bound.left) < 0.1:
                    continue

                #Ignore blocks that don't make logical sense
                if not self.can_be_continuation(s.attributes, test_block.attributes):
                    continue

                statblocks[i].add_section(test_block, sort=False)
                used += [j, i]
                merges.append(statblocks[i])
                break

        for i in range(len(statblocks)):
            if i not in used:
                merges.append(statblocks[i])

        merges.sort(key = lambda x: x.bound.top)

        return merges

    def filter_statblocks(self, sbs: List[Section]) -> List[Section]:
        '''Remove any statblocks that do not make logical sense'''
        
        filtered_sb = []
        for sb in sbs:
            block_start = -1
            for line in sb.lines:
                if "statblock_title" in line.attributes:
                    block_start = line.bound.top
                    block_left = line.bound.left
                    break

            if block_start < 0:
                continue

            # Remove any lines significantly above the title in the same column
            # Long term - do this after 2nd columnisation to allow for misaligned statblocks
            filtered_lines = []
            for line in sb.lines:
                if line.bound.top - block_start > -0.02 or abs(line.bound.left - block_left) > 0.05:
                    filtered_lines.append(line)

            filtered_sb.append(Section(filtered_lines, attributes=sb.attributes))

        return filtered_sb



    def create_statblocks(self, columns: List[List[Section]]) -> Union[List[Section], List[Section]]:
        '''Create candidate statblocks from columns of clustered text'''
        self.logger.debug("Creating statblocks from {} columns of lines".format(len(columns)))
        for i,col in enumerate(columns):
            self.logger.debug("\tCol {} of len {}".format(i, len(col)))

        statblock_parts = []

        for col in columns:

            current_statblock = Section()

            for cluster in col:
                sb_parts = [a for a in cluster.attributes if a.startswith("sb_")]

                self.logger.debug("Lines - {}".format(" || ".join([l.text for l in cluster.lines])))
                self.logger.debug("L0 Attributes, Bound - {}, {}".format(cluster.lines[0].attributes, cluster.lines[0].bound))
                self.logger.debug("Attributes - {}".format(cluster.attributes))

                if 'sb_skip' in sb_parts:
                    continue

                #No statblock tags, so finish current statblock part, excluding this cluster
                if len(sb_parts) == 0:

                    if len(current_statblock) > 0:
                        statblock_parts.append(current_statblock)
                    current_statblock = Section()
                    continue

                #Otherwise - can this part be added to our existing statblock and still make sense?
                if self.can_be_continuation(current_statblock.attributes, sb_parts):
                    current_statblock.add_section(cluster)

                #If not - also start a new statblock
                else:
                    if len(current_statblock) > 0:
                        statblock_parts.append(current_statblock)
                    current_statblock = Section()
                    current_statblock.add_section(cluster)

            if len(current_statblock) > 0:
                statblock_parts.append(current_statblock)

        #Merge statblocks across columns
        merged_statblocks = self.merge_statblocks(statblock_parts)

        #Remove any flatblocks that are incomplete
        filtered_statblocks = self.filter_statblocks(merged_statblocks)        

        #Turn ununsed lines into 'background text'
        unused_lines = []
        for col in columns:
            for cluster in col:
                if len(cluster.lines) > 0:
                    l = cluster.lines[0]
                    found = False

                    ### Skip any clusters that are just page numbers
                    try:
                        x = int(cluster.get_section_text())
                        continue
                    except:
                        pass

                    for sb in filtered_statblocks:
                        if sb.get_line_by_id(l.id):
                            found = True
                            break
                    
                    if not found:
                        unused_lines.append(cluster)

        return filtered_statblocks, unused_lines