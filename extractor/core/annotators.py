import configparser
import re
import numpy as np
import logging
import configparser
from typing import List

from . import constants
from ..utils.datatypes import Line, Section

class LineAnnotator(object):
    '''The LineAnnotator is pretty self-explantatory, we apply relatively noisy labels to individual lines that can 
    then be used by later processing stages to assign traits to paragraphs/line collections'''

    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("lineanno")
        # self.standard_height = config.getfloat("line_annotator", "line_height", fallback=0.04)

        # self.logger.debug("Configured LineAnnotator with config:")
        # self.logger.debug("\tStandard Height={}".format(self.standard_height))

        self.__compile_regexes()

    banned_words = [
        "town",
        "settlement",
        "stone fort",
        "cave system",
        "true form",
        "prone",
        "restrained",
        "attack",
        "DC",
        "grappled",
        "hit points",
        "shifts back",
        "target",
        "armor",
        "such as a",
        "comfortably"
    ]

    def __is_race_type_string(self, line: Line) -> bool:

        #If it's anything else, skip
        attrs = [a for a in line.attributes if a != 'large' and a != 'very_large' and "size" not in a]
        if len(attrs) > 0:
            return False
           
        text = line.text.strip()
        sizes = self.size_regex.findall(text)
        types = self.type_regex.findall(text)
        alignments = self.alignment_regex.findall(text)
        swarm = " swarm " in text.lower()

        # Must have at least size
        if len(sizes) == 0:
            return False

        # First word must be capitilised and a size
        words = [l.strip() for l in line.text.split() if l.strip()]
        if words[0].lower() != sizes[0].lower() or words[0][0].upper() != words[0][0]:
            return False

        # Size must be capitilised
        if sizes[0][0] != sizes[0][0].upper():
            return False

        # It should either be short or contain multiple pieces of info
        words = len(text.split(" "))
        if words > 12 or (words > 6 and len(sizes) + len(types) + len(alignments) + (1 if swarm else 0) < 2): #Either short text or it contains at least two of creature type, size and alignment
            return False

        for b in LineAnnotator.banned_words:
            if b in line.text.lower():
                return False

        return True

    def __compile_regexes(self):
        '''Pregenerate regexes used for annotating lines'''

        ### Pregenerate Regexes
        self.size_regex = re.compile(f"({'|'.join(constants.enum_values(constants.SIZES))})[\s,]", re.IGNORECASE)
        self.type_regex = re.compile(f"({'|'.join(constants.enum_values(constants.CREATURE_TYPES))})[\s,]", re.IGNORECASE)
        self.alignment_regex = re.compile(f"({'|'.join(constants.enum_values(constants.ALIGNMENTS))})[\s,]", re.IGNORECASE)

        signatures_strs = [
            ("Challenge \d+", "cr"),
            ("\d+d\d+", "dice_roll"),
            ("Senses\s[\w\s]+\d+\s*ft", "senses"),
            ("Damage\s[iI]mmunities", "dam_immunities"),
            ("Damage\s[rR]esistances", "resistances"),
            ("Damage\s[vV]ulnerabilities", "vulnerabilities"),
            ("Condition\sImmunities", "con_immunities"),
            ("^Armor Class\s\d+", "ac"),
            ("^Hit Points\s\d+", "hp"),
            ("^Speed\s\d+\s*ft", "speed"),
            ("Melee\sWeapon\sAttack:", "melee_attack"),
            ("Melee: [+-]\d+ to hit", 'melee_attack'),
            ("Ranged: [+-]\d+ to hit", 'ranged_attack'),
            ("Ranged\sWeapon\sAttack:", "ranged_attack"),
            ('Melee\sSpell\sAttack:', 'melee_attack'),
            ('Ranged\sSpell\sAttack:', 'ranged_attack'),
            ("DC\s\d+\s", "check"),
            ("\d+/(day|minute|hour)", "counter"),
            ("^[Ss]kills\s.*[+-]\d", "skills"),
            ("^Legendary Action", "legendary_action_title"),
            ("Recharge \d+-\d+", "recharge"),
            ("(\d+\s*\([+-−]\d+\)\s*){2,6}", "array_values"),
            ("^Languages?", "languages"),
            ("^[sS]aves\s+", "saves"),
            ("^Saving [tT]hrows\s+", "saves"),
            ("^Senses\s+", "senses"),
            ("^(1st|2nd|3rd|[4-9]th)\s*level\s*\([0-9]+\s*slots\)?:", "spellcasting"),
            ("^[cC]antrip (\(at will\))?", "spellcasting"),
            ("^([sS]pellcasting|[iI]nnate [sS]pellcasting).", 'spellcasting'),
            ("Proficiency Bonus", "proficiency"),
            ("Hit [dD]ice", "hitdice"),
            ("Hit.\s*\d+\s*\(\d+", 'in_attack'),
            (".\s*Hit:", "in_attack"),
            ("to hit, reach \d+ ft.", 'in_attack'),
            ("^Multiattack.", "multiattack"),
            ]

        uncased_signatures = [
            ("^STR\s+DEX\s+CON\s+INT\s+WIS\s+CHA", "array_title"),
            ("^Actions?$", "action_header"),
            ("^Legendary Actions?$", "legendary_header"),
            ("^Mythic Actions?$", "mythic_header"),
            ("^Lair Actions?$", "lair_header"),
            ("^\s*Reactions?\s*$", 'reaction_header'),
            ("recharges?\s*after\s*a\s*(short|short or long|long)\s*(?:rest)?", 'recharge'),
            ("proofreader", 'proofreader'),
            ("^Credits$", 'credits'),
            ("on a failed save or half", "save_to_halve"),
            ("costs\s*\d+\s*actions", 'legendary_action_cost'),
            ("\([a-zA-Z]+\s+form\s+only\).", 'form_restriction'),
            ("^[a-zA-Z\s]+\(\s*\d+\s*/\s*[a-zA-Z\s]+\s*\)\s*.", 'use_count'),
            ("[\d+][-\s]*(foot|ft\.?)\s*(cube|cone|line|sphere)", "template")
        ]
    
        self.signatures = []
        for ss in signatures_strs:
            self.signatures.append((re.compile(ss[0]), ss[1]))
        for ss in uncased_signatures:
            self.signatures.append((re.compile(ss[0], re.IGNORECASE), ss[1]))

    def annotate(self, lines: List[Line]) -> List[Line]:
        '''Applies annotations to passed lines based on their content, and lines directly before/after them'''

        for i,line in enumerate(lines):
                
            for r, tag in self.signatures:                
                matches = r.findall(line.text.strip())
                if len(matches) > 0:
                    line.attributes.append(tag)

            if self.__is_race_type_string(line):
                line.attributes.append("race_type_header")
                j = i - 1
                while j >= 0:
                    if lines[j].text.strip() != "":
                        if abs(lines[j].bound.left - lines[i].bound.left) < 0.05:
                            if abs(lines[j].bound.top - lines[i].bound.top) < 0.1:
                                lines[j].attributes.append("statblock_title")
                                if 'text_title' in lines[j].attributes:
                                    lines[j].attributes.remove('text_title')

                                ### Potentially merge line with previous one if it's spread over two lines
                                if j > 0:
                                    if abs(lines[j].bound.left - lines[j-1].bound.left) < 0.1:
                                        if abs(lines[j].bound.top - lines[j-1].bound.top) < 0.1:
                                            testSize = [a.split(":")[1] for a in lines[j].attributes if "size:" in a]
                                            size = [a.split(":")[1] for a in lines[j-1].attributes if "size:" in a]
                                            if len(size) == 1 and len(testSize) == 1:
                                                if size[0] == testSize[0]:
                                                    self.logger.debug("Merging previous line into title due to closeness")
                                                    lines[j].text = lines[j-1].text + " " + lines[j].text
                                break
                                
                    j -= 1

            if "." in line.text and line.text[0].isupper() and len(line.text.split('.')[0].split()) < 5:
                line.attributes.append("block_title")

            # If it is large text we've not otherwise accounted for, it's probably actual text so we want
            # to skip it. Note this attribute comes from the text loading stage
            if line.attributes == ["very_large"]:
                line.attributes.append("text_title")

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
    
    feature_annotations = [
        "spellcasting"
    ]

    action_annotations = [
        "action_header",
        "action_title",
        "melee_attack",
        "ranged_attack",
        "multiattack"
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

    reaction_annotations = [
        "reaction_header"
    ]

    generic_annotations = [
        "dice_roll",
        "check",
        "recharge",
        "counter",
        "spellcasting",
        "save_to_halve",
        "form_restriction",
        "use_count",
        "template"
    ]

    weak_generic_annotations = [
        "block_title"
    ]

    #These are annotations we are certain are NOT part of a statblock
    anti_annotations = [
        "text_title",
        "credits",
        'proofreader'
    ]

class SectionAnnotator(object):

    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("clusanno")

        self.logger.debug("Configured SectionAnnotator")

    def annotate(self, sections: List[Section]) -> List[Section]:

        if len(sections) == 0:
            self.logger.debug("No sections found to annotate. Skipping")
            return sections

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

            for df in LineAnnotationTypes.feature_annotations:
                if df in line_annotations:
                    c.attributes.append("sb_feature_block")
                    break

            for af in LineAnnotationTypes.action_annotations:
                if af in line_annotations:
                    c.attributes.append("sb_action_block")
                    break

            for lf in LineAnnotationTypes.legendary_annotations:
                if lf in line_annotations:
                    c.attributes.append("sb_legendary_action_block")
                    break

            for lf in LineAnnotationTypes.reaction_annotations:
                if lf in line_annotations:
                    c.attributes.append("sb_reaction_block")

            for gf in LineAnnotationTypes.generic_annotations:
                if gf in line_annotations:
                    c.attributes.append("sb_part")

            for gf in LineAnnotationTypes.anti_annotations:
                if gf in line_annotations:
                    c.attributes.append("sb_skip")

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
