from configparser import ConfigParser
from logging import Logger
import re

from utils.datatypes import Section, Line
from extractor import constants
from extractor.creature import Creature
from extractor.annotators import LineAnnotationTypes

from typing import Dict

from enum import IntEnum

class CreatureFactory():

    class ParserState(IntEnum):
        title = 0
        defence = 1
        abilities = 2
        traits = 3
        features = 4
        actions = 5

    def __init__(self, config: ConfigParser, logger: Logger):
        self.config = config
        self.logger = logger.getChild("parser")


    def __update_feature_block(self, creature: Creature, current_section : Section, line: Line, is_end=False):
        # Get first sentence from text to treat as a potential title
        parts = line.text.split('.')
        title = parts[0]
        has_colon = title.find(":")
        if has_colon > 0:
            title = title[:has_colon]

        ### Conditions for starting a new block
        #Easy case, new block
        new_block = len(current_section.lines) == 0
        #Check first sentence is less than 6 words (not including anything in brackets) and starts with a capital
        has_title = len(re.sub("\(.+?\)", "", title).split()) < 6  and title[0].isupper()\
             and title.split()[0].lower() not in constants.enum_values(constants.ABILITIES)\
             and len(parts) > 1 and parts[1] != ''


        #Check if we're in a spell list
        spell_list = False
        if len(current_section.lines) > 0 and "spellcasting" in current_section.lines[0].text.lower():
            if re.search("^\s*(at will|rest|daily|cantrip|1st|2nd|3rd|[4-9]th|[1-9]+\s*/\s*(day|long rest|short rest|encounter))", line.text, re.IGNORECASE) is not None:
                spell_list = True

        #Check if we're at the start of a new feature
        if not spell_list and (new_block or has_title or is_end):
            if len(current_section.lines) > 0:
                creature.add_feature(current_section)
                current_section = Section()
            current_section = Section([line])
        else:
            current_section.add_line(line)
            # if is_short:
            #     creature.add_feature(current_section)
            #     current_section = Section()

        return current_section


    def __update_action_block(self, creature: Creature, current_section: Section, line: Line, 
                                    action_type: constants.ACTION_TYPES, handled_action_block: Dict[constants.ACTION_TYPES, bool]):

        parts = line.text.split('.')
        title = parts[0]

        has_colon = title.find(":")
        if has_colon > 0:
            title = title[:has_colon]

        in_brackets = "(" in current_section.get_section_text() and ")" not in current_section.get_section_text()

        ### Conditions for starting a new block
        #Easy case, new block
        new_block = len(current_section.lines) == 0 
        #Check first sentence is less than 6 words (not including anything in brackets) and starts with a capital
        has_title = len(re.sub("\(.+?\)", "", title).split()) < 6  and title[0].isupper()\
             and title.split()[0].lower() not in constants.enum_values(constants.ABILITIES)\
             and len(parts) > 1 and parts[1] != ''

        #Is the start of an attack
        is_attack_start = "melee_attack" in line.attributes or "ranged_attack" in line.attributes

        #Handle recharges
        is_recharge = "recharge" in line.attributes

        #Handle a rare case where actions contain a table
        is_table = len(line.text) > 0 and line.text[0].isnumeric()

        #Check if we're at the start of a new feature
        if not is_table and not in_brackets and (new_block or has_title or is_attack_start or is_recharge):
            if len(current_section.lines) > 0:
                if not action_type in handled_action_block or handled_action_block[action_type]:
                    creature.add_action(current_section, action_type)
                else:
                    if action_type == constants.ACTION_TYPES.legendary:
                        creature.add_legendary_block(current_section)
                    if action_type == constants.ACTION_TYPES.lair:
                        creature.add_lair_block(current_section)
                    handled_action_block[action_type] = True
                current_section = Section()
        else:
            if is_table:
                current_section.lines[-1].text += "\n"
        
        current_section.add_line(line)

        return current_section, handled_action_block


    def statblock_to_creature(self, statblock: Section) -> Creature:

        cr = Creature(self.config, self.logger)
        state = CreatureFactory.ParserState.title

        current_section = Section()
        current_action_type = constants.ACTION_TYPES.action
        handled_action_block= {
            constants.ACTION_TYPES.legendary: False,
            constants.ACTION_TYPES.lair: False
        }

        # Guess the name for debugging purposes until we know it for sure
        name = statblock.lines[0].text

        i = -1
        while i < len(statblock.lines) - 1:
            i += 1
            line = statblock.lines[i]

            self.logger.info("{}: {} - {}".format(name, line.text, state))

            ### Advance state if we miss we have left our current state
            if state < CreatureFactory.ParserState.actions:
                if any(attr in LineAnnotationTypes.action_annotations for attr in line.attributes):

                    ### Finish up our current block
                    if len(current_section.lines) > 0:
                        if state == CreatureFactory.ParserState.traits:
                            cr.set_traits(current_section)
                        elif state == CreatureFactory.ParserState.features:
                            cr.add_feature(current_section)
                        current_section = Section([line])

                    state = CreatureFactory.ParserState.actions

                    if "action_header" in line.attributes:
                        current_action_type = constants.ACTION_TYPES.action
                        current_section = Section()
                        continue
                    elif "legendary_header" in line.attributes:
                        current_action_type = constants.ACTION_TYPES.legendary
                        current_section = Section()

            ### Check if line is simply an action block title
            if len(line.text) == 0:
                continue

            action_regex = re.compile("^({})\s+actions?$".format(constants.enum_values(constants.ACTION_TYPES)), re.IGNORECASE)
            if line.text[0].isupper() and action_regex.match(line.text[0]):

                if state == CreatureFactory.ParserState.features:
                    if len(current_section.lines) > 0:
                        cr.add_feature(current_section)
                        current_section = Section()
                    state = CreatureFactory.ParserState.actions
                
                elif state == CreatureFactory.ParserState.actions:
                    if len(current_section.lines) > 0:
                        cr.add_action(current_section, current_action_type)
                        current_section = Section()
                current_action_type = constants.ACTION_TYPES[at]
                handled_action_block[current_action_type] = False
                continue

            if state == CreatureFactory.ParserState.title:
                if "statblock_title" in line.attributes:
                    current_section.add_line(line)
                    continue
                if "race_type_header" in line.attributes:
                    current_section.add_line(line)

                cr.set_header(current_section)
                try:
                    name = cr.data["name"]
                except:
                    self.logger.warning("Failed to parse name in {}".format(current_section.get_section_text()))
                    return None
                current_section = Section()
                state = CreatureFactory.ParserState.defence
                continue

            if state == CreatureFactory.ParserState.defence:

                # Merge next lines in the header if they don't have attached tags
                j = 1
                while i+j < len(statblock.lines) - 1 and len(statblock.lines[i+j].attributes) == 0:
                    line = Line.merge([line, statblock.lines[i+j]])
                    j += 1
                i += j - 1

                if i == len(statblock.lines) - 1:
                    current_section.add_line(line)
                if "array_title" in line.attributes or "array_values" in line.attributes:
                    cr.set_defence(current_section)
                    state = CreatureFactory.ParserState.abilities
                    current_section = Section()
                else:
                    current_section.add_line(line)

            if state == CreatureFactory.ParserState.abilities:
                if "array_title" in line.attributes:
                    continue
                if "array_values" in line.attributes:
                    cr.set_abilities(Section([line]))
                    state = CreatureFactory.ParserState.traits    
                    continue
                else:
                    self.logger.warning("{}: Did not find attribute values, continuing to trait parsing.".format(name))
                    state = CreatureFactory.ParserState.traits

            if state == CreatureFactory.ParserState.traits:
                finished_traits = "cr" in current_section.get_line_attributes()
                if finished_traits:
                    cr.set_traits(current_section)
                    state = CreatureFactory.ParserState.features
                    current_section = Section()
                else:
                    #Don't want to add line if moving into features as that get's handled by the parser
                    #Also handle when there's no traits but we see a block title
                    if len(line.attributes) == 1 and "block_title" in line.attributes:
                        cr.set_traits(current_section)
                        state = CreatureFactory.ParserState.features
                        current_section = Section()
                    else:
                        current_section.add_line(line)

            if state == CreatureFactory.ParserState.features:
                # We have to manually check for proficiency as it tends to come after the CR
                if "proficiency" in current_section.get_line_attributes():
                    cr.set_proficiency(current_section.lines[0])
                    current_section = Section([line])
                    continue

                current_section = self.__update_feature_block(cr, current_section, line)

            if state == CreatureFactory.ParserState.actions:
                current_section, handled_action_block = self.__update_action_block(cr, current_section, line, 
                    current_action_type, handled_action_block)

        ### Finish up anything we've missed
        if not current_section.is_empty():
            if state == CreatureFactory.ParserState.defence:
                cr.set_defence(current_section)
            elif state == CreatureFactory.ParserState.traits:
                cr.set_traits(current_section)
            elif state == CreatureFactory.ParserState.features:
                cr.add_feature(current_section)
            elif state == CreatureFactory.ParserState.actions and current_action_type is not None:
                if current_action_type not in handled_action_block or handled_action_block[current_action_type]:
                    cr.add_action(current_section, current_action_type)
                else:
                    if current_action_type == constants.ACTION_TYPES.legendary:
                        cr.add_legendary_block(current_section)
                    if current_action_type == constants.ACTION_TYPES.lair:
                        cr.add_lair_block(current_section)

        if not cr.is_valid():
            return None

        return cr

