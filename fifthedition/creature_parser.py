from configparser import ConfigParser
from logging import Logger
import re

from utils.datatypes import Section, Line
from fifthedition import constants
from fifthedition.creature import Creature
from fifthedition.annotators import LineAnnotationTypes

from enum import IntEnum

class CreatureParser():

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
            if re.match("(at will|rest|daily|cantrip|1st|2nd|3rd|[4-9]th)", line.text, re.IGNORECASE):
                spell_list = True

        #Does the line finish early (aka end of paragraph). Ignore this for spell blocks
        #is_short = len(current_section.lines) > 0 and (line.bound.width < current_section.bound.width * 0.8) and not spell_list
        #print(line.text, spell_list, new_block, has_title, is_end)

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
                                    action_type: constants.ACTION_TYPES, handled_action_block: bool):

        parts = line.text.split('.')
        title = parts[0]

        has_colon = title.find(":")
        if has_colon > 0:
            title = title[:has_colon]

        ### Conditions for starting a new block
        #Easy case, new block
        new_block = len(current_section.lines) == 0 
        #Check first sentence is less than 6 words (not including anything in brackets) and starts with a capital
        has_title = len(re.sub("\(.+?\)", "", title).split()) < 6  and title[0].isupper() and title.split()[0].lower() not in constants.enum_values(constants.ABILITIES)

        #Is the start of an attack
        is_attack_start = "melee_attack" in line.attributes or "ranged_attack" in line.attributes

        #Handle a rare case where actions contain a table
        is_table = len(line.text) > 0 and line.text[0].isnumeric()

        #Check if we're at the start of a new feature
        if not is_table and (new_block or has_title or is_attack_start):
            if len(current_section.lines) > 0:
                if handled_action_block or action_type != constants.ACTION_TYPES.legendary:
                    creature.add_action(current_section, action_type)
                else:
                    creature.add_legendary_block(current_section)
                    handled_action_block = True
                current_section = Section()
        else:
            if is_table:
                current_section.lines[-1].text += "\n"
        
        current_section.add_line(line)

        return current_section, handled_action_block


    def statblock_to_creature(self, statblock: Section) -> Creature:

        cr = Creature(self.config, self.logger)
        state = CreatureParser.ParserState.title

        current_section = Section()
        current_action_type = None
        handled_action_block=False

        i = -1
        while i < len(statblock.lines) - 1:
            i += 1
            line = statblock.lines[i]

            self.logger.debug(line.text, state)

            ### Advance state if we miss we have left our current state
            if state < CreatureParser.ParserState.actions:
                if any(attr in LineAnnotationTypes.action_annotations for attr in line.attributes):

                    ### Finish up our current block
                    if len(current_section.lines) > 0:
                        if state == CreatureParser.ParserState.traits:
                            cr.set_traits(current_section)
                        elif state == CreatureParser.ParserState.features:
                            cr.add_feature(current_section)
                        current_section = Section([line])

                    state = CreatureParser.ParserState.actions

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

            if line.text[0].isupper() and len(line.text.split()) < 3 and \
                line.text.split()[0].lower().strip().removesuffix("s") in constants.enum_values(constants.ACTION_TYPES):
                at = line.text.split()[0].lower().strip().removesuffix("s")

                if state == CreatureParser.ParserState.features:
                    if len(current_section.lines) > 0:
                        cr.add_feature(current_section)
                        current_section = Section()
                    state = CreatureParser.ParserState.actions
                
                elif state == CreatureParser.ParserState.actions:
                    if len(current_section.lines) > 0:
                        cr.add_action(current_section, current_action_type)
                        current_section = Section()
                current_action_type = constants.ACTION_TYPES[at]
                handled_action_block = False
                continue

            if state == CreatureParser.ParserState.title:
                if "statblock_title" in line.attributes:
                    current_section.add_line(line)
                    continue
                if "race_type_header" in line.attributes:
                    current_section.add_line(line)

                cr.set_header(current_section)
                current_section = Section()
                state = CreatureParser.ParserState.defence
                continue

            if state == CreatureParser.ParserState.defence:

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
                    state = CreatureParser.ParserState.abilities
                    current_section = Section()
                else:
                    current_section.add_line(line)

            if state == CreatureParser.ParserState.abilities:
                if "array_title" in line.attributes:
                    continue
                if "array_values" in line.attributes:
                    cr.set_abilities(Section([line]))
                    state = CreatureParser.ParserState.traits    
                    continue
                else:
                    self.logger.warning("Did not find attribute values, continuing to trait parsing.")
                    state = CreatureParser.ParserState.traits

            if state == CreatureParser.ParserState.traits:
                finished_traits = "cr" in current_section.get_line_attributes()
                if finished_traits:
                    cr.set_traits(current_section)
                    state = CreatureParser.ParserState.features
                    current_section = Section()
                else:
                    #Don't want to add line if moving into features as that get's handled by the parser
                    current_section.add_line(line)

            if state == CreatureParser.ParserState.features:
                # We have to manually check for proficiency as it tends to come after the CR
                if "proficiency" in current_section.get_line_attributes():
                    cr.set_proficiency(current_section.lines[0])
                    current_section = Section([line])
                    continue

                current_section = self.__update_feature_block(cr, current_section, line)

            if state == CreatureParser.ParserState.actions:
                current_section, handled_action_block = self.__update_action_block(cr, current_section, line, 
                    current_action_type, handled_action_block)

        if len(current_section.lines) > 0 and state == CreatureParser.ParserState.defence:
            cr.set_defence(current_section)

        if not current_section.is_empty() and state == CreatureParser.ParserState.traits:
            cr.set_traits(current_section)

        if len(current_section.lines) > 0 and current_action_type is not None:
            cr.add_action(current_section, current_action_type)

        return cr

