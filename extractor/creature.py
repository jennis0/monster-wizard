from enum import Enum
from extractor.annotators import LineAnnotationTypes
from typing import Any, List
import configparser
import logging
import schema

from extractor import constants
import re

import extractor.creature_schema as cs
import extractor.constants as constants
from utils.datatypes import Line, Section

class Creature():
    '''Class for constructing a validated creature schema'''

    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        self.data = {}
        self.config = config
        self.logger = logger

    def to_json(self) -> Any:
        return self.data
    
    def __basic_pattern_match(self, text: str, options: Enum, expected: int=1) -> List[str]:
        '''Find words matching the enum within this string'''
        matches = re.findall("({})".format("|".join(constants.enum_values(options))), text, re.IGNORECASE)
        if len(matches) == 0:
            self.logger.warning("Failed to find {} in {}".format(options.__name__, text))
            return []
        elif len(matches) != expected:
            self.logger.warning("Found unexpected number of options in creature text!")
            self.logger.warning("\t{} - {}".format(text, matches))
            return []
        else:
            return matches


    def __validate_part(self, key: str) -> bool:
        '''Validate a subcomponent of the creature data against the schema'''
        try:
            if key in cs.CreatureSchema.schema:
                schema.Schema(cs.CreatureSchema.schema[key]).validate(self.data[key])
            elif schema.Optional(key) in cs.CreatureSchema.schema:
                schema.Schema(cs.CreatureSchema.schema[schema.Optional(key)]).validate(self.data[key])
            else:
                raise schema.SchemaError("{}: Did not find correct key type in schema for key {}".format(self.data["name"], key))
        except schema.SchemaError as e:
            self.logger.error("{}: Failed to validate parsed schema for {}. Error was:".format(self.data["name"], key))
            self.logger.error("\n"+e.__str__()+"\n")
            return False

        return True

    def _parse_enum_with_pre_post(self, text: str, enum: Enum):
        results = []
        match = re.compile("([\w\s'()]+\w)?(?:^|\s+)({})(?:\s*)([^.,]+)?,?".format(
            "|".join(constants.enum_values(enum))),
            re.IGNORECASE)
        # Split the line based on semi-colons
        texts = text.split(";")
        for t in texts:
            matches = match.findall(t)
            if len(matches) > 0:
                fields = {
                    "type": [m[1] for m in matches],
                    "pre_text": matches[0][0].strip(),
                    "post_text": matches[-1][2].strip()
                    }
                results.append(fields)
            elif len(matches) == 0:
                results.append({
                    'type':[],
                    "pre_text":t,
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
            "|".join(constants.enum_values(constants.SIZES)),
            "|".join(constants.enum_values(constants.SIZES)),
            "|".join(constants.enum_values(constants.CREATURE_TYPES) + constants.enum_values(constants.CREATURE_TYPE_PLURALS))
        ), text.strip(), re.IGNORECASE)
        if len(matches) == 1:
            self.data["size"] = [matches[0][0]]
            self.data["creature_type"] = [{
                "type": matches[0][1],
                "swarm": True,
                "swarm_size": matches[0][2]
            }]
        else:
            ### Find size by pattern matching
            sizes = self.__basic_pattern_match(parts[0], constants.SIZES)
            if len(sizes) > 0:
                self.data["size"] = []
                for s in sizes:
                    self.data["size"].append(s.lower())
                self.__validate_part("size")

            ### Find creature type, and whether they are a swarm
            types = self.__basic_pattern_match(parts[0], constants.CREATURE_TYPES)
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
        
        if groups[1] != None and groups[2] != None:
            formula = groups[1]
            formula += "".join(groups[2].split())
            hp = {
                "formula": formula,
                "average": int(groups[0])
            }
        else:
            hp = {
                "special": int(groups[0])
            }

        self.data["hp"] = hp
        self.__validate_part("hp")



    def set_speed(self, text: str):
        
        text = constants.MEASURES.normalise(text)
        matches = re.findall('({})?\s([0-9]+)\s*({})\.?'.format(
                "|".join(constants.enum_values(constants.MOVEMENT_TYPES)),
                "|".join(constants.enum_values(constants.MEASURES))),
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

        text = constants.MEASURES.normalise(line.text)
        sense_matches = re.findall("({})\s+([0-9]+)\s*({})".format(
            "|".join(constants.enum_values(constants.SENSES)),
            "|".join(constants.enum_values(constants.MEASURES))),
            text,
            re.IGNORECASE
        )
        #Iterate over found senses and add them
        senses = []
        for match in sense_matches:
            senses.append({
                "sense":match[0], 
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
        self.data["damage_immunities"] = self._parse_enum_with_pre_post(line.text[17:].strip(), constants.DAMAGE_TYPES)
        self.__validate_part("damage_immunities")

    def set_conditions_immunities(self, line: Line):
        self.data["condition_immunities"] = self._parse_enum_with_pre_post(line.text[20:].strip(), constants.CONDITIONS)
        self.__validate_part("condition_immunities")

    def set_damage_resistances(self, line: Line):
        self.data["resistances"] = self._parse_enum_with_pre_post(line.text[18:].strip(), constants.DAMAGE_TYPES)
        self.__validate_part("resistances")

    def set_vulnerabilities(self, line: Line):
        self.data["vulnerabilities"] = self._parse_enum_with_pre_post(line.text[22:].strip(), constants.DAMAGE_TYPES)
        self.__validate_part("vulnerabilities")


    def set_saves(self, line: Line):
        parsed_saves = {}
        found_saves = re.findall("(?:[\s,.]|^)({})\s*([+-])?\s*([0-9]+)".format(
            "|".join(constants.enum_values(constants.SHORT_ABILITIES))
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
            skills.append({
                "skill": skill[0].strip(),
                "mod": int(skill[2]) * (-1 if skill[1] == '-' else 1)
            })

        self.data["skills"] = skills
        self.__validate_part("skills")

    def set_cr(self, line: Line):
        cr_matches = re.findall("^Challenge\s+([0-9]+/?[0-9]*)\s+\(.*?XP\s*\)", line.text, re.IGNORECASE)
        if len(cr_matches) == 0:
            self.logger.warning("Failed to find challenge rating")
            return

        cr = {"cr":cr_matches[0]}
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
        self.data["features"].append({
            "title":title,
            "text": text
        })
        self.__validate_part("features")

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
                  ["^([0-9]*)/(day|rest|week)\s+(each)?","x"],
                  ["^cantrips\s*(?:\(at will\))?:", "s0"],
                  ["^([0-9])(?:st|nd|rd|th)\s*level \(([0-9]+)\s*slots\s*\)", "sx"]
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
        ability_re = re.compile("spellcasting\s*ability\s*(?:score)?\s*is\s*({})".format("|".join(constants.enum_values(constants.ABILITIES))), re.IGNORECASE)
 
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
                    if l[-1] == "-":
                        line += "{}{}".format(next_space, l[:-1])
                        next_space = ""
                    else:
                        line += "{}{}".format(next_space, l)
                        next_space = " "
                
                abilities = ability_re.findall(line)
                if len(abilities) == 0:
                    self.logger.warning("No spellcasting ability found")
                elif len(abilities) > 1:
                    self.logger.warning("Conflicting spellcasting abilities")
                else:
                    results["mod"] = abilities[0].strip()[:3].lower()
                
                #line = self._replace_dcs(line)
                #line = self._replace_hit(line)
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
                    "frequency": sb[0].lower()
                }
                spells_names = " ".join(sb[2]).split(":")[1].split(",")
                spell_level['spells'] = [
                    s.lower().strip() for s in spells_names
                ]
                results["levels"].append(spell_level)

            else:
                spell_level = {}
                spells_names = " ".join(sb[2]).split(":")[1].split(",")
                spell_list = [s.lower().strip() for s in spells_names]

                # Handle fixed frequency spells (daily, per rest, etc)
                if sb[0] == 'x':
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

    # def add_action(self, title: str, text: str, action_type: constants.ACTION_TYPES):

    def add_legendary_block(self, section: Section):
        self.data["legendary_block"] = section.get_section_text().strip().replace("\n", " ").replace("  ", " ")
        self.__validate_part("legendary_block")

    def add_lair_block(self, section: Section):
        self.data["lair_block"] = section.get_section_text().strip().replace("\n", " ").replace("  ", " ")
        self.__validate_part("lair_block")

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
            for t,a in zip(tokens, constants.SHORT_ABILITIES):
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
            for i,a in enumerate(constants.SHORT_ABILITIES):
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
        parts = section.get_section_text(join_char=" ").split(".")
        title = parts[0].strip()
        text = ". ".join(parts[1:]).strip()

        has_colon = title.find(":")
        if has_colon > 0:
            title = title[:has_colon]
            text = title[has_colon:] + " " + text

        if "spellcasting" in title.lower():
            self.add_spell_feature(section)
        else:
            self.add_normal_feature(title, text.replace("\n", " ").replace("  ", " "))

    def add_action(self, section: Section, action_type: constants.ACTION_TYPES):
        
        parts = section.get_section_text(join_char=" ").split(".")
        title = parts[0].strip()
        text = ". ".join(parts[1:]).strip()

        has_colon = title.find(":")
        if has_colon > 0:
            title = title[:has_colon]
            text = title[has_colon:] + " " + text
        
        self.logger.debug("Adding action {}".format(title))
        
        if not self.data:
            self.logger.error("Data object does not exist")
            self.logger.error(section.get_section_text())
            self.logger.error(section.attributes)
            self.logger.error(action_type)
            return

        if not action_type.name in self.data:
            self.data[action_type.name] = []

        self.data[action_type.name].append(
            {
                "title":title,
                "text":text.replace("\n", " ").replace("  ", " "),
                "type":action_type.name
            }
        )
        self.__validate_part(action_type.name)

        #self.add_action(title, text, action_type)

    def add_background(self, sections: List[Section]):
        self.data["background"] = [s.get_section_text() for s in sections]