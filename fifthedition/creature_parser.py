from configparser import ConfigParser
from logging import Logger

from utils.datatypes import Section, Line
from fifthedition import constants
from fifthedition.creature_2 import Creature2
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


    def statblock_to_creature(self, statblock: Section) -> Creature2:

        cr = Creature2(self.config, self.logger)
        state = CreatureParser.ParserState.title

        current_section = Section()
        current_action_type = None

        i = -1
        while i < len(statblock.lines) - 1:
            i += 1
            line = statblock.lines[i]

            ### Advance state if we miss we have left our current state
            if state < CreatureParser.ParserState.actions:
                if any(attr in LineAnnotationTypes.action_annotations for attr in line.attributes):
                    state = CreatureParser.ParserState.actions
                    
                    if len(current_section.lines) > 0:
                        cr.set_traits(current_section)
                        current_section = Section([line])



            if line.text.lower() in constants.enum_values(constants.ACTION_TYPES):
                current_action_type = constants.ACTION_TYPES[line.text.lower()]

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

                # Wait until line is not a defence attribute before parsing whole block
                is_defence = any([attr in LineAnnotationTypes.defence_annotations for attr in line.attributes])
                if i == len(statblock.lines) - 1:
                    current_section.add_line(line)
                    is_defence = False
                if not is_defence:
                    cr.set_defence(current_section)
                    state = CreatureParser.ParserState.abilities
                    current_section = Section([line])
                else:
                    current_section.add_line(line)

            if state == CreatureParser.ParserState.abilities:
                if "array_title" in line.attributes:
                    current_section = Section()
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
                current_section.add_line(line)

            if state == CreatureParser.ParserState.features:
                # We have to manually check for proficiency as it tends to come after the CR
                if "proficiency" in current_section.get_line_attributes():
                    cr.set_proficiency(current_section.lines[0])
                    current_section = Section([line])
                    continue

            #     current_section, state = self.__update_feature_block(current_section, line)

            # if state == CreatureParser.ParserState.actions:
            #     current_section, state = self.__update_action_block(current_section, line)

        return cr

