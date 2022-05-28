from enum import Enum
from fractions import Fraction
from math import floor
from random import randint

from .annotators import LineAnnotationTypes
from typing import Any, List, Dict, Optional
import configparser
import logging
import schema
import re

from . import creature_schema as cs
from .constants import *
from ..utils.datatypes import Line, Section

import traceback

class Creature:
    '''Class for constructing a validated creature schema'''

    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        self.data = {}
        self.config = config
        self.logger = logger
        self.errors = {}
        self.section = None

        add_damage_types = [
            "damage",
            "healing"
        ]

        ### Complex regexes for dice formula
        average_regex = '[^d](\d+)[^d]' #Finds 5 but not 1d5
        formula_regex = '\(?((?:\d+d\d+)(?:\s*(?:\+|-|\s+)\s*(?:\d+d\d+|\d+))*)\)?' #Finds 1d6+3 or (1d2-4)
        damage_type_regex = f"({'|'.join(enum_values(DAMAGE_TYPES) + add_damage_types)})" #Finds damage types
        dice_formula_regex = f'(?:{formula_regex}|{average_regex})+\s*{damage_type_regex}?' #Finds at least one of the above

        ### Precompile some regexes
        self.attack_res = {
            "type":re.compile("^(melee|ranged|melee\s*or\s*ranged)\s*(spell|weapon)?\s*(?:attack)?:", re.IGNORECASE),
            "hit":re.compile(":\s*([+-]?\s*\d+)\s*to\s*hit", re.IGNORECASE),
            "reach":re.compile(f"reach\s*(\d+)\s*({'|'.join(enum_values(MEASURES))})"),
            "range":re.compile(f"(?:range|reach)\s*(\d+)(?:/(\d+))?\s*({'|'.join(enum_values(MEASURES))})"),
            "target":re.compile(f",\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten|all|any)\s*(creature|target|object)s?\s*,?\s*([a-zA-Z,\s']+)?\.\s*[Hh]it"),
            "hit_damage":re.compile(f".\s*hit:?\s*{dice_formula_regex}", re.IGNORECASE),
            "versatile_damage":re.compile(f"or\s*{dice_formula_regex}\s*[a-zA-Z\s]*\s*two hands", re.IGNORECASE)
        }

        self.general_res = {
            #"dice_damage":re.compile(f"[^\d]\s+([d\d\s\+-]+)\s+({'|'.join(enum_values(DAMAGE_TYPES) + ['damage'])})", re.IGNORECASE),
            #"damage":re.compile(f"\s*[^d](\d+)\s+(?:\(([\d\s\+-d]+)\))?\s*({'|'.join(enum_values(DAMAGE_TYPES) + ['damage'])})", re.IGNORECASE),
            "dice_rolls":re.compile(dice_formula_regex, re.IGNORECASE),
            "saves":re.compile(f"dc\s*(\d+)\s*\(?\s*({'|'.join(enum_values(ABILITIES) + enum_values(SHORT_ABILITIES) + enum_values(SKILLS))})\s*\(?", re.IGNORECASE),
            "escape":re.compile(f"escape\s*dc\s*(\d+)", re.IGNORECASE),
            "conditions":re.compile(f"({'|'.join(enum_values(CONDITIONS))})", re.IGNORECASE),
            "halves":re.compile('half\s*as\s*much\s*damage', re.IGNORECASE)
        }

    def is_valid(self):

        if 'name' not in self.data:
            self.logger.warn(f'Failed to build basic statblock. No name present')
            return False

        fails = 0
        required = ['size', 'creature_type', 'hp', 'ac', 'speed']
        for r in required:
            if r not in self.data:
                self.logger.warn(f"{self.data['name']} missing {r}")
                fails += 1

        if fails > 1:
            self.logger.warn(f'Rejecting {self.data["name"]} as it is missing too many core stats')
            return False

        return True

    def set_source(self, source_title: str, page: int=-1):
        self.data['source'] = {
            'title': source_title,
        }
        if page >= 0:
            self.data['source']['page'] = page
    
    def __basic_pattern_match(self, text: str, options: Enum, expected: int=1) -> List[str]:
        '''Find words matching the enum within this string'''
        matches = re.findall("({})".format("|".join(enum_values(options))), text, re.IGNORECASE)
        if len(matches) == 0:
            self.logger.warning("Failed to find {} in {}".format(options.__name__, text))
            return []
        elif len(matches) != expected:
            self.logger.warning("Found unexpected number of options in creature text!")
            self.logger.warning("\t{} - {}".format(text, matches))
            return []
        else:
            return matches

    def __create_error(self, key, type, error, detail, severity="error"):
        return {    
                "key":key,
                "type":type,
                "error":error,
                "detail":detail,
                "handled":False,
        }

    def __do_validate(self, key, data:Any, test_schema:Any) -> List[Any]:
        errors = []
        try:
            schema.Schema(test_schema).validate(data)
        except schema.SchemaError as e:
            errors.append(self.__create_error(
                key,
                "schema",
                e.errors[-1],
                e.autos[-1]
            ))

        return errors
            

    def __validate_part(self, key: str, index: Optional[int]=None) -> bool:
        '''Validate a subcomponent of the creature data against the schema'''

        errors = []

        if key in cs.CreatureSchema.schema:
            test_schema = cs.CreatureSchema.schema[key]
            data = self.data[key]
        elif schema.Optional(key) in cs.CreatureSchema.schema:
            test_schema = cs.CreatureSchema.schema[schema.Optional(key)]
            data = self.data[key]
        else:
            test_schema = None
            errors = [self.__create_error(key, "unknown_key", f"Unknown key {key}", "")]

        if key:
            ### Handle checking one item in a list
            if index:
                if index == -1:
                    index = len(data) - 1
                if not isinstance(data, list):
                    errors.append(self.__create_error(f"{key}[{index}]", "not_list", "", ""))
                    test_schema = None
                else:
                    test_schema = test_schema[0]
                    errors += self.__do_validate(f"{key}[{index}]", data[index], test_schema)
            
            ### Handle checking all items in a list
            elif isinstance(test_schema, list):
                if not isinstance(data, list):
                    errors.append(self.__create_error(key, "not_list", "", ""))
                    test_schema = None
                else:
                    test_schema = test_schema[0]
                    for i in range(len(self.data[key])):
                        errors += self.__do_validate(f"{key}[{i}]", data[i], test_schema)

            ### Basic case of not a list
            else:
                errors += self.__do_validate(f"key", data, test_schema)

        if len(errors) > 0:
            if key in self.errors:
                self.errors[key] += errors
            else:
                self.errors[key] = errors

            self.logger.error("{}: Failed to validate parsed schema for {}.".format(self.data["name"], key))
            self.logger.error(errors)
            self.logger.error(f"Data: {self.data[key]}\n")
            return False

        return True

    def _parse_enum_with_pre_post(self, text: str, enum: Enum):
        results = []
        
        #hack to deal with 'cold iron'
        text = text.replace("cold iron", "cldirn")

        #Normalise space formatting
        text = " ".join([t for t in text.split() if t != ""])

        match = re.compile("([\w\s'()]+\w)?(?:^|\s+)({})(?:\s*)([^.,]+)?,?".format(
            "|".join(enum_values(enum))),
            re.IGNORECASE)
        # Split the line based on semi-colons
        texts = text.split(";")
        for t in texts:
            matches = match.findall(t)
            if len(matches) > 0:
                fields = {
                    "type": [m[1] for m in matches],
                    "pre_text": matches[0][0].strip().replace("cldirn", "cold iron"),
                    "post_text": matches[-1][2].strip().replace("cldirn", "cold iron")
                    }
                results.append(fields)
            elif len(matches) == 0:
                results.append({
                    'type':[],
                    "pre_text":t.replace("cldirn", "cold iron"),
                    "post_text":""
                })
        return results

    ####################################################################################
    #################################### Header ########################################
    ####################################################################################

    def set_name(self, text: str) -> bool:
        '''Sets the name of the monster'''
        #Split line into words
        words = text.split()

        #Normalise capitalisation
        words = [word.lower() for word in words]
        for i in range(len(words)):
            word = words[i]
            if i == 0 or word not in ["in", "of", "the", "and", "a", "an"]:
                words[i] = word[0].upper() + word[1:]

        self.data["name"] = " ".join(words)
        self.__validate_part("name")



    def set_race_type_size(self, text: str):
        '''Set the race, type, and size of the monster'''
        parts = text.strip().split(",")

        ### Check for complex swarm case
        matches = re.findall("({})\s+swarm\s+of\s+({})\s+({})".format(
            "|".join(enum_values(SIZES)),
            "|".join(enum_values(SIZES)),
            "|".join(enum_values(CREATURE_TYPES) + enum_values(CREATURE_TYPE_PLURALS))
        ), text.strip(), re.IGNORECASE)
        if len(matches) == 1:
            self.data["size"] = [matches[0][0]]
            self.data["creature_type"] = {
                "type": matches[0][2],
                "swarm": True,
                "swarm_size": matches[0][1]
            }
        else:
            ### Find size by pattern matching
            sizes = self.__basic_pattern_match(parts[0], SIZES)
            if len(sizes) > 0:
                self.data["size"] = []
                for s in sizes:
                    self.data["size"].append(s.lower())
                self.__validate_part("size")

            ### Find creature type, and whether they are a swarm
            types = self.__basic_pattern_match(parts[0], CREATURE_TYPES)
            if len(types) > 0:
                ts = []
                for t in types:
                    if len(t) > 0:
                        ts.append(t.lower())
                if len(ts) == '':
                    ts = ["unknown"]
                    
                swarm = "swarm" in parts[0]
                swarm_size = self.data["size"] if swarm else None
                self.data["creature_type"] = {
                    "type": ts, "swarm": swarm, "swarm_size": swarm_size
                }
                self.__validate_part("creature_type")

        if len(parts) > 1:
            self.data["alignment"] = ",".join(parts[1:]).strip()
            self.__validate_part("alignment")
        else:
            #If we fail to get it from a comma, try to guess
            words = text.strip().split()
            for i,word in enumerate(words):
                if "creature_type" in self.data and word.lower() == self.data["creature_type"]["type"][-1].lower() and i < len(words):
                    self.data["alignment"] =  " ".join(words[i+1:])
                    self.__validate_part("alignment")
            




    ####################################################################################
    ################################### DEFENCE ########################################
    ####################################################################################

    def set_ac(self, text: str):
        '''Set AC of creature'''
        ### Use regex to pull out ACs and associated text
        acs = re.findall("([0-9]+)\s*(?:\(([\w\s+,]+)?\)?)?\s*([\w\s]+)?", text)

        if len(acs) == 0:
            self.logger.warning("Failed to parse AC string {}".format(text))
            return None

        ac_data = []
        for ac in acs:
            from_list = [s.strip() for s in ac[1].split(",") if s.strip() != '']
            ac_data.append({
                "ac": int(ac[0]),
                "from": from_list,
                "condition": ac[2].strip()
            })

        self.data["ac"] = ac_data
        self.__validate_part("ac")
        
    def set_hp(self, text):
        '''Set the HP'''

        # Find the average and formula part of the dice string
        avg_and_or_dice_match = "([0-9]+)\s*\+?\s*(?:\(?([0-9]+d[0-9]+)\s*(\+\s*[0-9]*)?\)?)?"
        match = re.compile("Hit\sPoints\s+" + avg_and_or_dice_match)
        m = match.match(text)
        groups = m.groups()

        hp = {}
        if groups[0] == None:
            self.logger.warning("Failed to parse HP string = {}".format(text))
            return None
       
        if groups[1] != None:
            formula = groups[1]
            if groups[2] != None:
                formula += f"{''.join(groups[2].split())}"
            hp = {
                "formula": formula,
                "average": int(groups[0])
            }
        else:
            hp = {
                "special": groups[0]
            }

        self.data["hp"] = hp
        self.__validate_part("hp")

    def set_speed(self, text: str):
        
        text = MEASURES.normalise(text)
        matches = re.findall('({})?\s([0-9]+)\s*({})\.?'.format(
                "|".join(enum_values(MOVEMENT_TYPES)),
                "|".join(enum_values(MEASURES))),
            text,
            re.IGNORECASE)

        speeds = []
        for value in matches:
            s = {
                "type": value[0].lower().strip() if value[0] else 'walk',
                "distance": int(value[1]),
                "measure": value[2]
            }
            speeds.append(s)
        
        self.data["speed"] = speeds
        self.__validate_part("speed")


    ####################################################################################
    #################################### Traits ########################################
    ####################################################################################
    
    def set_senses(self, line: Line):
        '''Sets the creatures senses'''

        text = MEASURES.normalise(line.text)
        sense_matches = re.findall("({})\s+([0-9]+)\s*({})".format(
            "|".join(enum_values(SENSES)),
            "|".join(enum_values(MEASURES))),
            text,
            re.IGNORECASE
        )
        #Iterate over found senses and add them
        senses = []
        for match in sense_matches:
            senses.append({
                "type":match[0], 
                "distance":int(match[1]),
                "measure":match[2]
            })
        self.data["senses"] = senses
        self.__validate_part("senses")

        # Handle passive perception separately
        passive_matches = re.findall("passive\s+perception\s+([0-9]+)", line.text, re.IGNORECASE)
        if len(passive_matches) == 1:
            self.data["passive"] = int(passive_matches[0])
            self.__validate_part("passive")

    def set_damage_immunities(self, line: Line):
        self.data["damage_immunities"] = self._parse_enum_with_pre_post(line.text[17:].strip(), DAMAGE_TYPES)
        self.__validate_part("damage_immunities")

    def set_conditions_immunities(self, line: Line):
        self.data["condition_immunities"] = self._parse_enum_with_pre_post(line.text[20:].strip(), CONDITIONS)
        self.__validate_part("condition_immunities")

    def set_damage_resistances(self, line: Line):
        self.data["resistances"] = self._parse_enum_with_pre_post(line.text[18:].strip(), DAMAGE_TYPES)
        self.__validate_part("resistances")

    def set_vulnerabilities(self, line: Line):
        self.data["vulnerabilities"] = self._parse_enum_with_pre_post(line.text[22:].strip(), DAMAGE_TYPES)
        self.__validate_part("vulnerabilities")

    def set_saves(self, line: Line):
        parsed_saves = {}
        found_saves = re.findall("(?:[\s,.]|^)({})\s*([+-])?\s*([0-9]+)".format(
            "|".join(enum_values(SHORT_ABILITIES))
        ), line.text, re.IGNORECASE)
        
        if len(found_saves) == 0:
            self.logger.warning("Failed to find saves in {}".format(line.text))
            return

        for save in found_saves:
            if save[1] == '':
                parsed_saves[save[0].strip().lower()] = int(save[2].strip())
            else:
                parsed_saves[save[0].strip().lower()] = int(save[1].strip() + save[2].strip())

        self.data["saves"] = parsed_saves 
        self.__validate_part("saves")

    def set_languages(self, line: Line):
        self.data["languages"] = [l.strip() for l in " ".join(line.text.split()[1:]).split(",")]

    def set_skills(self, line: Line):        
        skill_matches = re.findall("[\s\.,;]([a-zA-Z'\s]+?)\s+([+-])\s*([0-9]+)",
            line.text,
            re.IGNORECASE
            )

        skills = []
        for skill in skill_matches:
            if skill[0].strip().lower() in SHORTSKILLSMAP:
                sk = SHORTSKILLSMAP[skill[0].strip().lower()]
            else:
                sk = skill[0].strip().lower()

            skills.append({
                "skill": sk,
                "mod": int(skill[2]) * (-1 if skill[1] == '-' else 1),
                "prof":True
            })

        self.data["skills"] = skills
        self.__validate_part("skills")

    def set_cr(self, line: Line):
        cr_matches = re.findall("^Challenge\s+([0-9]+/?[0-9]*)\s*\(?([0-9,]+)?(?:XP)?\s*\)?", line.text, re.IGNORECASE)
        if len(cr_matches) == 0:
            self.logger.warning("Failed to find challenge rating")
            return

        cr = {"cr":cr_matches[0][0]}

        for k in cr:
            if "/" in cr[k]:
                cr[k] = float(Fraction(cr[k]))
            else:
                cr[k] = int(cr[k])

        if "lair" in line.text:
            cr["lair"] = cr_matches[1]
        elif "coven" in line.text:
            cr["coven"] = cr_matches[1]

        self.data["cr"] = cr
        self.__validate_part("cr")
    
    def set_proficiency(self, line: Line):
        prof_match = re.findall("Proficiency[\s\w:]+\+?([0-9]+)", line.text, re.IGNORECASE)
        if len(prof_match) == 1:
            self.data["proficiency"] = int(prof_match[0])
            self.__validate_part("proficiency")
        else:
            self.logger.warning("Failed to parse proficiency", line.text)



    ####################################################################################
    ################################### Features #######################################
    ####################################################################################

    def add_normal_feature(self, title: str, text: str):
        if "features" not in self.data:
            self.data["features"] = []
        
        self.logger.debug("Adding feature {}".format(title))
        
        ### Start parsing the main feature text
        # Run a set of regexes over the text to pull out key information
        # General damage and effects
        properties = {}
        for r in self.general_res:
            v = [(match.end(), match.groups()) for match in self.general_res[r].finditer(text.lower(), pos=0)]
            properties[r] = v if len(v) > 0 else None

        feature = {
            "title":title,
            "text":text,
        }

        effects = self.__create_effects(properties)
        if len(effects) > 0:
            feature["effects"] = effects

        # Look at title to pull out any associated costs/recharge/uses
        recharge_re = re.compile("recharge\s*(\d+)(?:-+(\d+))?", re.IGNORECASE)
        uses_re = re.compile(f"(\d+)\s*/\s*({'|'.join(enum_values(TIME_MEASURES))})", re.IGNORECASE)

        recharge = recharge_re.search(title)
        uses = uses_re.search(title)

        if recharge:
            if recharge.group(2):
                feature["recharge"] = {"from":int(recharge.group(1)), "to":int(recharge.group(2))}
            else:
                feature["recharge"] = {"from":int(recharge.group(1)), "to":6}
            span = recharge.span()
            feature["title"] = title[0:span[0]] + title[span[1]:]

        if uses:
            span = uses.span()
            feature["uses"] = {"slots":int(uses.group(1)), "period":uses.group(2).lower()}
            feature["title"] = title[0:span[0]] + title[span[1]:]

        feature["title"] = feature["title"].strip()
        if feature["title"].endswith("."):
            feature["title"] = feature["title"][:-1]
        if feature["title"].strip().endswith("()"):
            feature["title"] = feature["title"].strip()[:-2]

        ### Append parsed action to data
        self.data["features"].append(feature)
        self.__validate_part("features", -1)


    def __parse_spell_names(self, spells: List[str]) -> List[Any]:
            per_spell_level_re = re.compile("([a-zA-Z\s/']+)\s*\((.*)\)", re.IGNORECASE)
            spell_list = []
            for s in spells:
                parts = per_spell_level_re.findall(s.lower().strip())
                if len(parts) == 1:
                    t = parts[0][1].strip()
                    if "level" in t and t[0] in "123456789":
                        spell_list.append({"name":parts[0][0].strip(), "level": int(t[0])})
                    elif "cantrip" in t:
                        spell_list.append({"name":parts[0][0].strip(), "level":0})
                    else:
                        spell_list.append({"name":parts[0][0].strip(), "post_text":t})
                else:
                    spell_list.append({"name":s.lower().strip()})

            return spell_list

    def add_spell_feature(self, section: Section):
        parts = section.lines[0].text.split(".")
        title = parts[0]
        text = ". ".join(parts[1:]).strip()

        has_colon = title.find(":")
        if has_colon > 0:
            title = title[:has_colon]
            text = title[has_colon:] + " " + text


        text = [text] + [l.text for l in section.lines[1:]]
        starts = [["^(constant):","constant"], 
                  ["^(at will):","will"], 
                  ["^([0-9]+)/(day|rest|week)\s*(each)?-?","x"],
                  ["^cantrips\s*(?:\(at will\))?:", "s0"],
                  ["^([0-9])(?:st|nd|rd|th)\s*-?\s*level \(([0-9]+)\s*slots?\s*\)", "sx"]
        ]

        header_types = {
            "day":"daily",
            "rest":"rest",
            "week":"weekly",
        }

        for s in starts:
            s[0] = re.compile(s[0], re.IGNORECASE)

        spellblocks = [['h', [], [text[0]]]]
        for line in text[1:]:
            used = False
            for s in starts:
                found = s[0].findall(line)
                if len(found) == 1:
                    spellblocks.append([s[1], found[0], [line]])
                    used=True
                    break
            if not used:
                spellblocks[-1][2].append(line)

        results = {"title":title, "levels":[]}
        level_re = re.compile("an?\s*(\d+)(?:st|nd|rd|th)?[-\s*]level\s*spellcaster", re.IGNORECASE)
        ability_re = re.compile("spellcasting\s*ability\s*(?:score)?\s*is\s*({})".format("|".join(enum_values(ABILITIES))), re.IGNORECASE)
 
        last_line = " ".join(spellblocks[-1][2])
        split = -1
        for i,l in enumerate(last_line.split(",")):
            if len(l) > 5:
                split = i
                break
        if split > 0:
            spellblocks.append(['f', [], spellblocks[-1][2][i:]])
            spellblocks[-2][2] = spellblocks[-2][2][:i]

        for sb in spellblocks:
            # Process headers
            if sb[0] == 'h':
                # Reattach lines while removing hyphenated line breaks
                line = ""
                next_space=" "
                for l in sb[2]:
                    if len(l) == 0:
                        continue
                    if l[-1] == "-":
                        line += "{}{}".format(next_space, l[:-1])
                        next_space = ""
                    else:
                        line += "{}{}".format(next_space, l)
                        next_space = " "
                
                abilities = ability_re.findall(line)
                if len(abilities) == 0:
                    self.logger.warning("No spellcasting ability found")
                    results['mod'] = None
                elif len(abilities) > 1:
                    self.logger.warning("Conflicting spellcasting abilities")
                else:
                    results["mod"] = abilities[0].strip()[:3].lower()

                level = level_re.findall(line)
                if len(level) == 0:
                    self.logger.warning("No spellcasting level found")
                    results["spellcastingLevel"] = 0
                elif len(level) > 1:
                    self.logger.warning("Conflicting spellcasting levels found")
                else:
                    results["spellcastingLevel"] = int(level[0])

                
                results["text"] = line

                save = re.findall("spell\s*save\s*DC\s*([0-9]+)", line)
                if len(save) == 1:
                    results["save"] = int(save[0])

            # Process post text
            elif sb[0] == 'f':
                results["post_text"] = " ".join(sb[2])

            # Handle constant and at will spells
            elif sb[0] == 'constant' or sb[0] == "will":
                spell_level = {
                    "frequency": sb[0].lower(),
                    'level':'unlevelled'
                }
                spells_names = " ".join(sb[2]).split(":")[1].split(",")
                spell_level['spells'] = self.__parse_spell_names(spells_names)
                results["levels"].append(spell_level)

            else:
                spell_level = {}
                s = " ".join(sb[2])
                if ":" in s:
                    spells_names = s.split(":")[1].split(",")
                elif "each" in s:
                    ind = s.find("each")
                    spells_names = " ".join(s[ind+5].split(","))
                else:
                    spells_names = s.split(",")

                spell_list = self.__parse_spell_names(spells_names)

                # Handle fixed frequency spells (daily, per rest, etc)
                if sb[0] == 'x':
                    spell_level['level'] = 'unlevelled'
                    spell_level["frequency"] = header_types[sb[1][1].lower()] 
                    spell_level["each"] = sb[1][2] != ''
                    if sb[1][0] != '':
                        spell_level["slots"] = int(sb[1][0])
                    else:
                        self.logger.warning("Failed to read number of slots for spell level {}".format(sb[2][0]))
                        spell_level["slots"] = 1
                    spell_level["spells"] = spell_list

                # Handle levelled spells
                else:
                    if sb[0] == 's0':
                        spell_level["frequency"] = "levelled"
                        spell_level["level"] = "cantrip"
                        spell_level["spells"] = spell_list
                    elif sb[0] == 'sx':
                        spell_level["frequency"] = "levelled"
                        spell_level["level"] = sb[1][0]
                        spell_level["spells"] = spell_list

                        if sb[1][1] is not None:
                            spell_level["slots"] = int(sb[1][1])

                results["levels"].append(spell_level)

        if "spellcasting" not in self.data:
            self.data["spellcasting"] = []
        self.data["spellcasting"].append(results)
        self.__validate_part("spellcasting")
        return





    ####################################################################################
    #################################### Actions #######################################
    ####################################################################################

    # def add_action(self, title: str, text: str, action_type: ACTION_TYPES):

    def add_legendary_block(self, section: Section):
        self.data["legendary_block"] = section.get_section_text().strip().replace("\n", " ").replace("  ", " ")
        self.__validate_part("legendary_block")

    def add_lair_block(self, section: Section):
        self.data["lair_block"] = section.get_section_text().strip().replace("\n", " ").replace("  ", " ")
        self.__validate_part("lair_block")


    @staticmethod
    def __pm_str_to_int(s: str) -> int:
        s = s.replace("+","")
        s = s.strip()
        return int(s)

    def __create_attack(self, title: str, properties: Any):
        '''Use results of precomplied regexes to turn attack text intro structured data'''

        attack = {
            "name":title,
            "type":properties["type"][1][0].strip(),
            "weapon": properties["type"][1][1].strip() if properties["type"][1][1] else "weapon",
        }

        
        target_count_map = {
            "one":1, "two":2, "three":3, "four":4, "five":5,"six":6,"seven":7,"eight":8,"nine":9,"any":"any","all":"all"
        }

        max_parsed = properties["type"][0] 

        if "or" in attack["type"]:
            attack["type"] = "both"

        if properties["reach"]:
            v = properties["reach"]
            attack["reach"] = {"distance": int(v[1][0]), "measure": v[1][1]}
            max_parsed = max(v[0], max_parsed)

        ### Only write long range for non-melee attacks
        if properties["range"] and attack["type"] != "melee":
            v = properties["range"]
            attack["range"] = {"short_distance": int(v[1][0]), "long_distance": int(v[1][1]) if v[1][1] else None, "measure": v[1][2]}
            max_parsed = max(v[0], max_parsed)

        if properties["hit"]:
            if properties["hit"]:
                attack["hit"] = Creature.__pm_str_to_int(properties["hit"][1][0])
                max_parsed = max(properties["hit"][0], max_parsed)
            else:
                self.logger.warning(f"Hit is missing a value.")

        if properties["target"]:
            v = properties["target"][1]
            try:
                c = Creature.__pm_str_to_int(v[0])
            except:
                c = target_count_map[v[0]]
            attack["target"] = {"count":c, "type":v[1]}
            if v[2] and v[2].strip():
                attack["target"]["post_text"] = v[2].strip()            
            max_parsed = max(properties["target"][0], max_parsed)


        if properties["hit_damage"]:
            v = list(properties["hit_damage"][1])
            #Number but no formula
            if v[1] and not v[0]:
                v[0] = str(v[1])

            #If formula or number
            if v[0]:
                #Normalise formula
                v[0] = self.__normalise_formula(v[0])   
                
                #Formula but no number
                if v[0] and not v[1]:
                    v[1] = self.__calculate_average_formula(v[0])

                attack["damage"] = {"damage":{"average":int(v[1]), "formula":v[0]}, "type":v[2].strip() if v[2] else None}
                max_parsed = max(properties["hit_damage"][0], max_parsed)

        if properties["versatile_damage"]:
            v = list(properties["versatile_damage"][1])
            #Number but no formula
            if v[1] and not v[0]:
                v[0] = str(v[1])

            #If formula or number
            if v[0]:
                #Normalise formula
                v[0] = self.__normalise_formula(v[0])   
                
                #Formula but no number
                if v[0] and not v[1]:
                    v[1] = self.__calculate_average_formula(v[1])

                attack["versatile"] = {"damage":{"average":int(v[1]), "formula":v[0]}, "type":v[2].strip() if v[2] else None}
                max_parsed = max(properties["versatile_damage"][0], max_parsed)

        effects = self.__create_effects(properties, start_char=max_parsed)
        if len(effects) > 0:
            attack["effects"] = effects

        return attack

    def __normalise_formula(self, formula: str) -> str:
        last_was_num = False
        parts = [f.strip() for f in formula.split() if f.strip()]
        normed_parts = []
        for p in parts:
            if p.replace('d','').isnumeric():
                if last_was_num:
                    self.logger.warn(f"Unnormalised formula {formula}, adding '+'")
                    normed_parts.append("+")
                normed_parts.append(p.strip())
                last_was_num = True
            elif p in ['+','-']:
                last_was_num = False
                normed_parts.append(p.strip())

        return " ".join(normed_parts)

    @staticmethod
    def __calculate_average_formula(formula: str) -> int:
        '''
        Performs a dirty quick calculation to get the average of a maths formula.
        Does not handle brackets!
        '''
        total = 0
        next_pos = 1
        for part in formula.split():
            part = part.strip()
            if "d" in part:
                num,size = part.split("d")
                num = int(num)
                size = int(size)
                total += floor(next_pos * num * ((size / 2) + 0.5))
                next_pos = 1
            elif part == "-":
                next_pos = -1
            else:
                total += next_pos * int(part)
                next_pos = 1
        return total

    def __create_effects(self, properties: Any, start_char=0):
        '''Use results of precompiled regexes to turn action text into structred effect data'''
        
        used_conditions = []
        used_rolls = []
        used_halves = []

        effects = []

        rolls = properties["dice_rolls"] if properties["dice_rolls"] else []
        saves = properties["saves"] if properties["saves"] else []
        conditions = properties["conditions"] if properties["conditions"] else []
        halves = properties["halves"] if properties["halves"] else []
        escape = properties["escape"] if properties["escape"] else []

        #Add a 'no save' save at the start so we can capture any effects not tied to a save
        saves = [[start_char,None]] + saves

        for i in range(len(saves)):
            effect = {}     

            ### Only consider things up to the next check
            if i+1 == len(saves):
                end_char = 1000000
            else:
                end_char = saves[i+1][0]

            ### Add Save
            if saves[i][1]:
                effect["save"] = {
                    "ability": saves[i][1][1][:3],
                    "value": int(saves[i][1][0])
                }
                effect["on_save"] = "none"

            condition_set = set()

            ### Add dice rolls (inc. damage)
            for ri,r in enumerate(rolls):
                if ri in used_rolls:
                    continue
                if r[0] < start_char or r[0] > end_char:
                    continue

                #conver to list for asignment
                roll = list(r[1])

                #Ignore case of just numbers without either formula or damage type
                if not roll[2] and not (roll[0] and roll[1]):
                    continue

                ### Handle average but no formula
                if not roll[0] and roll[1]:
                    roll[0] = str(roll[1])
                elif not roll[1] and roll[0]:
                    roll[1] = self.__calculate_average_formula(roll[0])

                roll[0] = self.__normalise_formula(roll[0])

                #Handle damage rolls
                if roll[2] in enum_values(DAMAGE_TYPES) or roll[2] == "damage":
                    if "damage" not in effect:
                        effect["damage"] = []

                    effect["damage"].append({"damage":{"average":int(roll[1]), "formula":roll[0]}, "type":roll[2]})

                else:
                    if "rolls" not in effect:
                        effect["rolls"] = []
                    if roll[2]:
                        effect["rolls"].append({"roll":{"average":int(roll[1]), "formula":roll[0]}, "type":roll[2]})
                    else:
                        effect["rolls"].append({"roll":{"average":int(roll[1]), "formula":roll[1]}})
                
                used_rolls.append(ri)

            ### Add conditions Note we have to filter for conditions being repeated
            for ci,c in enumerate(conditions):
                if ci in used_conditions or c[1][0] in condition_set:
                    continue
                if c[0] < start_char or c[0] > end_char:
                    continue
                if "conditions" not in effect:
                    effect["conditions"] = []
                if c[1][0] == CONDITIONS.grappled.name:
                    if len(escape) == 0:
                        continue
                    else:
                        effect["end_save"] = {
                            "ability":"ath or acr",
                            "value":int(escape[0][1][0])
                        }

                effect["conditions"].append({"condition":c[1][0]})
                condition_set.add(c[1][0])
                used_conditions.append(ci)

            ### Add save efect
            if saves[i][1]:
                for hi,h in enumerate(halves):
                    if hi in used_halves:
                        continue
                    if h[0] < start_char or h[0] > end_char:
                        continue
                    effect["on_save"] = "half"
                    used_halves.append(hi)
                    break            

            if len(effect.keys()) > 0:
                effects.append(effect)

        return effects


    def get_title(self, text):
        words = text.split()

        ### Handle common feature titles
        common_titles = ["Multiattack"]
        for ct in common_titles:
            if text.startswith(ct):
                return (ct, text[len(ct):].strip())
        
        short_text = " ".join(words[:min(10, len(words))]).lower()
        mwa = short_text.find("melee weapon attack")
        if mwa > 1:
            return (text[:mwa].strip(), text[mwa:].strip())
        rwa = short_text.find("ranged weapon attack")
        if rwa > 1:
            return (text[:rwa].strip(), text[rwa:].strip())

        parts = text.split(".")
        title = parts[0].strip()
        text = ". ".join(parts[1:]).strip()

        has_colon = title.find(":")
        if has_colon > 0:
            title = title[:has_colon]
            text = title[has_colon:] + " " + text
# 
        has_brackets = title.find("(")
        if has_brackets > -1 and has_brackets < 30:
            title_end = title.find(")")
            text = title[title_end+1:] + " " + text
            title = title[:title_end+1]

        title_words = title.split()
        if len(title_words) > 6:
            stop_word = 1
            for tw in title_words[1:]:
                if tw[0].isupper():
                    stop_word += 1
                else:
                    break

            text = " ".join(title_words[stop_word-1:]) + " " + text
            text.replace("  ", " ")
            title = " ".join(title_words[:stop_word-1])

        return (title, text)



    def add_action(self, section: Section, action_type: ACTION_TYPES):

        ### Do some parsing to get the title from the text
        # First handle some common cases we don't need to rely on punctuation
        text = section.get_section_text(join_char=" ")
        title, text = self.get_title(text)        
        self.logger.debug("Adding action {}".format(title))
        
        if not self.data:
            self.logger.error("Data object does not exist")
            self.logger.error(section.get_section_text())
            self.logger.error(section.attributes)
            self.logger.error(action_type)
            return

        if not action_type.name in self.data:
            self.data[action_type.name] = []

        ### Start parsing the main action text
        # Run a set of regexes over the text to pull out key information
        # First regexes handle the attack header
        properties = {"text": [0,section.get_section_text()]}
        for r in self.attack_res:
            v = self.attack_res[r].search(text.lower())
            properties[r] = [v.end(), v.groups()] if v else None

        ### Track where the 'attack header' ends so we don't double count damage
        attack_line_end = 0
        if properties["type"]:
            for p in properties:
                v = properties[p]
                if v:
                    attack_line_end = max(attack_line_end, v[0])

        # Seconds regexes handle more general damage and effects
        for r in self.general_res:
            v = [(match.end(), match.groups()) for match in self.general_res[r].finditer(text.lower(), pos=attack_line_end)]
            properties[r] = v if len(v) > 0 else None

        action = {
            "title":title,
            "text":text,
            "type":action_type.name
        }

        # If attack, parse attack, otherwise only parse effects
        if properties["type"]:
            try:
                action["attack"] = self.__create_attack(title, properties)
            except Exception as e:
                self.logger.error(traceback.format_exc())
        else:
            effects = self.__create_effects(properties)
            if len(effects) > 0:
                action["effects"] = effects

        # Look at title to pull out any associated costs/recharge/uses
        recharge_re = re.compile("recharge\s*(\d+)(?:-+(\d+))?", re.IGNORECASE)
        uses_re = re.compile(f"(\d+)\s*/\s*({'|'.join(enum_values(TIME_MEASURES))})", re.IGNORECASE)
        cost_re = re.compile(f"costs\s*(\d+)\s*action", re.IGNORECASE)

        costs = cost_re.search(title)
        recharge = recharge_re.search(title)
        uses = uses_re.search(title)

        if recharge:
            if recharge.group(2):
                action["recharge"] = {"from":int(recharge.group(1)), "to":int(recharge.group(2))}
            else:
                action["recharge"] = {"from":int(recharge.group(1)), "to":6}
            span = recharge.span()
            action["title"] = title[0:span[0]] + title[span[1]:]

        if uses:
            span = uses.span()
            action["uses"] = {"slots":int(uses.group(1)), "period":uses.group(2).lower()}
            action["title"] = title[0:span[0]] + title[span[1]:]

        if costs:
            action["cost"] = int(costs.group(1))
        elif action_type == ACTION_TYPES.legendary:
            action["cost"] = 1


        action["title"] = action["title"].strip()
        if action["title"].endswith("."):
            action["title"] = action["title"][:-1]
        if action["title"].strip().endswith("()"):
            action["title"] = action["title"].strip()[:-2]

        ### Append parsed action to data
        self.data[action_type.name].append(action)
        self.__validate_part(action_type.name, -1)

    def add_background(self, sections: List[Section]):
        self.data["background"] = [s.get_section_text() for s in sections]


    ####################################################################################
    ################################## Primary API #####################################
    ####################################################################################

    def set_header(self, section: Section):
        '''Set name of monster and it's race/type/size'''
        if len(section.lines) == 0:
            self.logger.warning("No lines in header section")
            return
        if len(section.lines) > 2:
            self.logger.debug("Additional lines found in header. Merging")
        
        self.set_name(section.lines[0].text)
        self.set_race_type_size(" ".join([l.text for l in section.lines[1:]]))

    def set_defence(self, section: Section):
        '''Set the AC, Hit Points, and Size/Type of the creature'''
        for line in section.lines:
            if "ac" in line.attributes:
                self.set_ac(line.text)
            elif "speed" in line.attributes:
                self.set_speed(line.text)
            elif "hp" in line.attributes:
                self.set_hp(line.text)



    def set_abilities(self, section: Section):

        #Find which line we actually care about
        attr_values = ""
        for line in section.lines:
            if "array_values" in line.attributes:
                attr_values = line.text.strip()

        if attr_values == "":
            self.logger.warning("Failed to find attribute string")
            return

        parts = attr_values.split()
        attribs = {}
        if len(parts) != 12:
            #Assume OCR has failed so try to guess values
            tokens = re.findall('([^\(][0-9]+)?\s*(\([+-][0-9]+\))?', attr_values)
            if len(tokens) < 6:
                self.logger.warning("Failed to parse attribute string {}".format(attr_values))
                return None

            #Iterate over values and either use raw number of guess based on ability score
            for t,a in zip(tokens, SHORT_ABILITIES):
                if t[0] != '':
                    attribs[a.name] = int(t[0])
                else:
                    if t[1] == '':
                        self.logger.warning("Failed to parse attribute string {}".format(attr_values))
                        return None
                    guess = int(10 + (int(t[1][1:-1]) * 2)) #Index to remove starting/ending brackets
                    attribs[a.name] = guess
                    self.logger.warning("Missing proper value for attribute {}. Guessing {} based on modifier {}".format(a.name, guess, t[1]))

        else:
            #Otherwise, we have everthing we need!
            for i,a in enumerate(SHORT_ABILITIES):
                attribs[a.name] = int(parts[2*i])

        self.data["abilities"] = attribs
        self.__validate_part("abilities")
        return


    def set_traits(self, section : Section):
        trait_set_map = {
            "senses":self.set_senses,
            "dam_immunities":self.set_damage_immunities,
            "con_immunities":self.set_conditions_immunities,
            "vulnerabilities":self.set_vulnerabilities,
            "resistances":self.set_damage_resistances,
            "saves":self.set_saves,
            "languages":self.set_languages,
            "skills": self.set_skills,
            "cr": self.set_cr,
            "proficiency": self.set_proficiency
        }
        
        if len(section.lines) == 0:
            self.logger.warn("Submitted empty traits section")
            return

        current_line = section.lines[0]
        for line in section.lines[1:]:
            if not any(attr in LineAnnotationTypes.trait_annotations for attr in line.attributes):
                current_line = Line.merge([current_line, line])
            else:
                for attr in current_line.attributes:                    
                    if attr in trait_set_map:
                        trait_set_map[attr](current_line)
                        break
                current_line = line

        for attr in current_line.attributes:
            if attr in trait_set_map:
                trait_set_map[attr](current_line)
                break


    def add_feature(self, section : Section):
        text = section.get_section_text(join_char=" ")
        title, text = self.get_title(text)

        if "spellcasting" in title.lower():
            self.add_spell_feature(section)
        else:
            self.add_normal_feature(title, text.replace("\n", " ").replace("  ", " "))

    def finish(self) -> Dict[str, Any]:
        ### Set proficiency bonus
        if not "proficiency" in self.data and "cr" in self.data:
            if self.data["cr"]["cr"] in PROF_BY_CR:
                self.data["proficiency"] = PROF_BY_CR[self.data["cr"]["cr"]]

        ### Set whether skills are calculated using proficiency
        if "skills" in self.data:
            for i,s in enumerate(self.data["skills"]):
                if s["skill"] in SHORT_SKILL_ABILITY_MAP:
                    if "proficiency" in self.data:
                        ability = SHORT_SKILL_ABILITY_MAP[s["skill"]]
                        ability = self.data["abilities"][ability]
                        default_value = self.data["proficiency"] + floor((ability - 10)/2)
                        self.data["skills"][i]["default"] = default_value == s["mod"]
                else:
                    self.data["skills"][i]["default"] = True
                    self.data["skills"][i]["__custom_id"] = randint(10000,100000) #Needed for the statblock editor to give the skill a unique ID

        ### Store errors
        self.data["errors"] = self.errors

        if self.section:
            self.data["section"] = self.section.serialise()

        return self.data
