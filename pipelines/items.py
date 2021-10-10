from configparser import ConfigParser
from logging import Logger

from utils.datatypes import Line
from typing import List

import re
from enum import Enum, auto

class ItemTypes (Enum):
    Armor = auto()
    Potion = auto()
    Ring = auto()
    Rod = auto()
    Scroll = auto()
    Staff = auto()
    Wand = auto()
    Weapon = auto()
    Wondrous = auto()

class ItemRarities (Enum):
    Common = auto()
    Uncommon = auto()
    Rare = auto()
    Very_Rare = auto()
    Legendary = auto()
    Artifact = auto()
    Varies = auto()
    Unknown = auto()


class ItemAnnotator(object):
    '''Annotates lines with attributes used when parsing items'''

    def __init__(self, config: ConfigParser, logger: Logger):
        self.config = config
        self.logger = logger.getChild("itemanno")

        self.__compile_regexes()

    def __compile_regexes(self):
        '''Pregenerate regexes used for annotating lines'''

        ### Pregenerate Regexes
        race_type_str = "^\s*({})\s*({})?,?\s*({})?".format(
            "|".join(constants.enum_values(constants.SIZES)),
            "|".join(constants.enum_values(constants.CREATURE_TYPES)), 
            "|".join(constants.enum_values(constants.ALIGNMENTS)))
        self.race_type_regex =  re.compile(race_type_str, re.IGNORECASE)

        signatures_strs = [
                ("Challenge \d+", "cr"),
                ("\d+d\d+", "dice_roll"),
                ("Senses\s[\w\s]+\d+\s*ft", "senses"),
                ("Damage\sImmunities", "dam_immunities"),
                ("Damage\sResistances", "resistances"),
                ("Damage\sVulnerabilities", "vulnerabilities"),
                ("Condition\sImmunities", "con_immunities"),
                ("^Armor Class\s\d+", "ac"),
                ("^Hit Points\s\d+", "hp"),
                ("^Speed\s\d+\s*ft", "speed"),
                ("^Melee\sWeapon\sAttack:", "melee_attack"),
                ("^Ranged\sWeapon\sAttack:", "ranged_attack"),
                ("DC\s\d+\s", "check"),
                ("\d+/(day|minute|hour)", "counter"),
                ("^skills\s.*[+-]\d", "skills"),
                ("^Legendary Action", "legendary_action_title"),
                ("^Actions", "action_title"),
                ("Costs \d+ actions", "legendary_action_cost"),
                ("Recharge \d+-\d+", "recharge"),
                ("^STR\s+DEX\s+CON\s+INT\s+WIS\s+CHA", "array_title"),
                ("(\d+\s*\([+-]?\d+\)\s+){2,6}", "array_values"),
                ("^Languages?", "languages"),
                ("^Saves\s+", "saves"),
                ("^Saving Throws\s+", "saves"),
                ("^Senses\s+", "senses"),
                ("^(1st|2nd|3rd|[4-9]th)\s*level\s*\([0-9]+\s*slots\)?:", "spellcasting"),
                ("^Cantrip (\(at will\))?", "spellcasting"),
                ("Proficiency Bonus", "proficiency"),
                ("Hit Dice", "hitdice"),
                ("^Actions$", "action_header"),
                ("^Legendary Actions$", "legendary_header"),
                ("^Mythic Actions$", "mythic_header"),
                ("^Lair Actions$", "lair_header")
            ]
        self.signatures = []
        for ss in signatures_strs:
            self.signatures.append((re.compile(ss[0], re.IGNORECASE), ss[1]))

    def annotate(self, lines: List[Line]) -> List[Line]:
        '''Applies annotations to passed lines based on their content, and lines directly before/after them'''

        for i,line in enumerate(lines):

            if self.__is_race_type_string(line):
                line.attributes.append("race_type_header")
                j = i - 1
                while j >= 0:
                    if lines[j].text.strip() != "":
                        if abs(lines[j].bound.left - lines[i].bound.left) < 0.05:
                            if lines[j].bound.bottom() - lines[i].bound.top < 0.05:
                                lines[j].attributes.append("statblock_title")
                                break
                    j -= 1
                
            for r, tag in self.signatures:                
                matches = r.findall(line.text.strip())
                if len(matches) > 0:
                    line.attributes.append(tag)

            if "." in line.text and line.text[0].isupper() and len(line.text.split('.')[0].split()) < 5:
                line.attributes.append("block_title")

            # If it is large text we've not otherwise accounted for, it's probably actual text so we want
            # to skip it. Note this attribute comes from the text loading stage
            if line.attributes == ["very_large"]:
                line.attributes.append("text_title")

            print(line, line.attributes)

        return lines

class LineAnnotationTypes:
    defence_annotations = [
        "hp",
        "ac",
        "speed"
    ]

    trait_annotations = [
        "languages",
        "saves",
        "skills",
        "challenge",
        "senses",
        "dam_immunities",
        "resistances",
        "vulnerabilities",
        "con_immunities",
        "cr"
    ]

    action_annotations = [
        "action_header",
        "action_title",
        "melee_attack",
        "ranged_attack",
    ]

    legendary_annotations = [
        "legendary_action_title",
        "legendary_action_cost",
        "legendary_header"
    ]

    mythic_annotations = [
        "mythic_header"
    ]

    lair_annotations = [
        "lair_header"
    ]

    generic_annotations = [
        "dice_roll",
        "check",
        "recharge",
        "counter",
        "spellcasting"
    ]

    weak_generic_annotations = [
        "block_title"
    ]

    #These are annotations we are certain are NOT part of a statblock
    anti_annotations = [
        "text_title"
    ]

class SectionAnnotator(object):

    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("clusanno")

        self.logger.debug("Configured SectionAnnotator")

    def annotate(self, sections: List[Section]) -> List[Section]:

        self.logger.debug("Annotating {} Sections".format(len(sections)))
        for c in sections:
            line_annotations = c.get_line_attributes()

            if "statblock_title" in line_annotations:
                c.attributes.append("sb_start")

            if "race_type_header" in line_annotations:
                c.attributes.append("sb_header")

            for df in LineAnnotationTypes.defence_annotations:
                if df in line_annotations:
                    c.attributes.append("sb_defence_block")
                    break

            if "array_title" in line_annotations:
                c.attributes.append("sb_array_title")

            if "array_values" in line_annotations:
                c.attributes.append("sb_array_value")

            for df in LineAnnotationTypes.trait_annotations:
                if df in line_annotations:
                    c.attributes.append("sb_flavour_block")
                    break

            for af in LineAnnotationTypes.action_annotations:
                if af in line_annotations:
                    c.attributes.append("sb_action_block")
                    break

            for lf in LineAnnotationTypes.legendary_annotations:
                if lf in line_annotations:
                    c.attributes.append("sb_legendary_action_block")
                    break

            for gf in LineAnnotationTypes.generic_annotations:
                if gf in line_annotations:
                    c.attributes.append("sb_part")

            for gf in LineAnnotationTypes.anti_annotations:
                if gf in line_annotations:
                    c.attributes.append("skip")

            num_generic = 0
            for la in line_annotations:
                if la in LineAnnotationTypes.weak_generic_annotations:
                    num_generic += 1
            if num_generic > 0.1 * len(c.lines):
                c.attributes.append("sb_part_weak")
            
        #Add some annotations to mark the start and end of each column
        sections[0].attributes.append("col_start")
        sections[-1].attributes.append("col_end")
        return sections
