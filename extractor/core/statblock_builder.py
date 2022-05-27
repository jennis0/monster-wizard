import configparser
import logging
from typing import List, Union

from ..utils.datatypes import Section

class StatblockBuilder(object):
    '''Statblock builder takes annotated line clusters and groups them into statblocks'''

    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("builder")

    def can_be_continuation(self, current_section: Section, new_section: Section) -> bool:
        '''Check whether the statblock would make logical sense if we combined the two candidate statblocks 
        based on their contained parts'''

        current_tags = [a for a in current_section.attributes if a.startswith('sb_')]
        new_tags = [a for a in new_section.attributes if a.startswith('sb_')]

        self.logger.debug(f"Current Tags: {current_tags}, Proposed Tags: {new_tags}")

        if 'sb_skip' in new_tags:
            return False

        #Needs to be stronger than a weak sb part to link across pages
        if new_section.page > current_section.page and set(new_tags) == set(['sb_part_weak']):
            return False

        current_tags = [t for t in current_tags if t.startswith("sb_")]
        new_tags = [t for t in new_tags if t.startswith("sb_")]
        
        if len(current_tags) == 0:
            return False

        if len(new_tags) == 0:
            return False

        if "sb_skip" in new_tags or "sb_skip" in current_tags:
            return False

        tag_index_mapping = {
            "sb_start":0,
            "sb_header":1,
            "sb_defence_block":2,
            "sb_array_title":3,
            "sb_array_value":4,
            "sb_flavour_block":5,
            "sb_feature_block":6,
            "sb_action_block":7,
            "sb_reaction_block":8,
            "sb_legendary_action_block":9,
            "sb_lair_block":10,
            "sb_part":10,
            "sb_part_weak":10
        }

        last_tag = max(tag_index_mapping[t] if "sb_part" not in t else -1 for t in current_tags)
        next_tag = min(tag_index_mapping[t] for t in new_tags)

        ### Only allow lair actions if we've already seen legendary actions
        if "sb_lair_block" in new_tags\
             and ("sb_legendary_action_block" not in new_tags and "sb_legendary_action_block" not in current_tags):
             return False

        ### If the only thing in the current section is parts and the next cluster is a new statblock
        ### Then they shouldn't be clustered together
        if last_tag == -1 and next_tag == 0:
            return False

        return next_tag >= last_tag

    def merge_statblocks(self, statblocks: List[Section]) -> List[Section]:
        merges = []

        used = set()
        used_base = set()

        self.logger.debug("CLUSTERING CROSS-COLUMN STATBLOCKS")
       
        #Track the names of current statblocks
        for i in range(len(statblocks)):

            if i in used:
                continue

            s = statblocks[i]
            if "sb_start" not in s.attributes:
                self.logger.debug(f"Not start: {s.lines[0]} - {s.attributes}")
                continue

            if "sb_skip" in s.attributes:
                self.logger.debug(f"Skip: {s.lines[0]} - {s.attributes}")
                continue

            self.logger.debug(f"Building: {s.lines[0]} - {s.attributes}")

            last_page = s.page
            last_col = i

            mid_stats = []

            ### Iterate over next blocks looking for remaining statblock pieces
            for j in range(i+1, min(i+6, len(statblocks))):

                test_block = statblocks[j]

                if j in used:
                    continue

                self.logger.debug(f"Trying to add: {test_block.lines[0]} - {test_block.attributes}")

                #If a new statblock starts on a new page, assume we've finished the last one
                if "sb_start" in test_block.attributes:
                    #Store name of any new statblock we see
                    if "col_end" in test_block.attributes:
                        mid_stats.append(test_block.lines[0].text.lower().strip())
                    if test_block.page > s.page:
                        self.logger.debug("Reached new statblock on new page. Do consider any more")
                        break
                    continue
                else:
                    #If the name of a statblock is present, assume it is not part of the current one
                    # and no future ones are
                    if "col_start" in test_block.attributes:
                        end = False
                        for l in test_block.lines:
                            for ms in mid_stats:
                                if not ms in l.text.lower():
                                    continue
                                end = True
                                break
                            if end:
                                break
                        if end:
                            self.logger.debug("Found continuous statblock over column break")
                            break

                #Only allow a split over a page boundry if it is the next statblock piece
                if (j-last_col) > 1 and test_block.page > last_page:
                    self.logger.debug("Failed: Page Gap")
                    continue

                #Ignore blocks in the same column
                if test_block.page == s.page and abs(s.bound.left - test_block.bound.left) < 0.1:
                    self.logger.debug("Failed: Same Column")
                    continue

                #Ignore blocks that don't make logical sense
                if not self.can_be_continuation(s, test_block):
                    self.logger.debug("Failed: Not a continuation")
                    continue

                #We combine the statblock and note that these are used
                self.logger.debug("Merged")
                statblocks[i].add_section(test_block, sort=False)
                last_page = test_block.page
                last_col = j
                used.update([i,j])
                used_base.add(i)

        for i in range(len(statblocks)):
            if i in used_base:
                merges.append(statblocks[i])

        for i in range(len(statblocks)):
            if i not in used:
                merges.append(statblocks[i])

        merges.sort(key = lambda x: -x.page * 100 -  x.bound.top)

        # for m in merges:
        #     for l in m.lines:
        #         print(l)
        #     print("==============================================")

        return merges

    def filter_statblocks(self, sbs: List[Section]) -> List[Section]:
        
        filtered_sb = []
        for sb in sbs:
            block_start = -1
            for line in sb.lines:
                if "statblock_title" in line.attributes:
                    block_start = line.bound.top
                    block_left = line.bound.left
                    start_page = line.page
                    break

            if block_start < 0:
                continue

            # Remove any lines significantly above the title in the same column
            # Long term - do this after 2nd columnisation to allow for misaligned statblocks
            filtered_lines = []
            for line in sb.lines:
                if line.page != start_page or (line.bound.top - block_start) > -0.02 or abs(line.bound.left - block_left) > 0.05:
                    filtered_lines.append(line)

            filtered_sb.append(Section(filtered_lines, attributes=sb.attributes, sort_order=Section.SortOrder.NoSort))

        # return sbs

        return filtered_sb



    def create_statblocks(self, columns: List[List[Section]]) -> Union[List[Section], List[Section]]:
        '''Create candidate statblocks from columns of clustered text'''
        self.logger.debug("Creating statblocks from {} columns of lines".format(len(columns)))
        for i,col in enumerate(columns):
            self.logger.debug("\tCol {} of len {}".format(i, len(col)))

        statblock_parts = []
        for col in columns:

            current_statblock = Section(sort_order=Section.SortOrder.NoSort)

            for cluster in col:
                sb_parts = [a for a in cluster.attributes if a.startswith("sb_")]

                self.logger.debug("Lines - {}".format(" || ".join([l.text for l in cluster.lines])))
                self.logger.debug("Attributes - {}".format(cluster.attributes))

                #No statblock tags, so finish current statblock part, excluding this cluster
                if len(sb_parts) == 0:
                    if len(current_statblock) > 0:
                        statblock_parts.append(current_statblock)
                    current_statblock = Section()
                    self.logger.debug("Starting new cluster")
                    continue

                #Otherwise - can this part be added to our existing statblock and still make sense?
                if self.can_be_continuation(current_statblock, cluster):
                    self.logger.debug("Adding to cluster")
                    current_statblock.add_section(cluster)

                #If not - also start a new statblock
                else:
                    if len(current_statblock) > 0:
                        statblock_parts.append(current_statblock)
                    self.logger.debug("Not a continuation, starting new cluster")
                    current_statblock = Section()
                    current_statblock.add_section(cluster)

            if len(current_statblock) > 0:
                statblock_parts.append(current_statblock)

        #Merge statblocks across columns
        merged_statblocks = self.merge_statblocks(statblock_parts)

        #Remove any statblocks that are incomplete
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