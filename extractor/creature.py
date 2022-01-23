from enum import Enum
from extractor.annotators import LineAnnotationTypes
from typing import Any, List
import configparser
import logging
import schema


from extractor.constants import *
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

        ### Precompile some regexes
        self.attack_res = {
            "type":re.compile("^(melee|ranged|melee\s*or\s*ranged)\s*(spell|weapon)?\s*(?:attack)?:", re.IGNORECASE),
            "hit":re.compile(":\s*([+-]?\s*\d+)\s*to\s*hit", re.IGNORECASE),
            "reach":re.compile(f"reach\s*(\d+)\s*({'|'.join(enum_values(MEASURES))})"),
            "range":re.compile(f"range\s*(\d+)(?:/(\d+))?\s*({'|'.join(enum_values(MEASURES))})"),
            "target":re.compile(f",\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten|all|any)\s*(creature|target|object)s?,?\s*([a-zA-Z,\s']+)?.\s*Hit"),
            "hit_damage":re.compile(f".\s*hit:\s*(\d+)\s*(?:\(([\d\s\+-d]+)\))?\s*({'|'.join(enum_values(DAMAGE_TYPES))})", re.IGNORECASE),
            "versatile_damage":re.compile(f"or\s*(\d+)\s*(?:\(([\d\s\+-d]+)\))?\s*({'|'.join(enum_values(DAMAGE_TYPES))})\s*[a-zA-Z\s]*\s*two hands", re.IGNORECASE)
        }

        self.general_res = {
            "damage":re.compile(f"\s*(\d+)\s*(?:\(([\d\s\+-d]+)\))?\s*({'|'.join(enum_values(DAMAGE_TYPES))})", re.IGNORECASE),
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

    def to_json(self) -> Any:
        return self.data

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
            "|".join(enum_values(enum))),
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
            skills.append({
                "skill": skill[0].strip(),
                "mod": int(skill[2]) * (-1 if skill[1] == '-' else 1)
            })

        self.data["skills"] = skills
        self.__validate_part("skills")

    def set_cr(self, line: Line):
        cr_matches = re.findall("^Challenge\s+([0-9]+/?[0-9]*)\s*\(?([0-9,]+)?(?:XP)?\s*\)?", line.text, re.IGNORECASE)
        if len(cr_matches) == 0:
            self.logger.warning("Failed to find challenge rating")
            return

        cr = {"cr":cr_matches[0][0]}
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
        level_re = re.compile("a\s*(\d+)(?:st|nd|rd|th)?\s*level\s*spellcaster", re.IGNORECASE)
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
            attack["reach"] = {"distance": v[1][0], "measure": v[1][1]}
            max_parsed = max(v[0], max_parsed)

        if properties["range"]:
            v = properties["range"]
            print(v)
            attack["range"] = {"short_distance": v[1][0], "long_distance": v[1][1], "measure": v[1][2]}
            max_parsed = max(v[0], max_parsed)

        if properties["hit"]:
            attack["hit"] = int(properties["hit"][1][0])
            max_parsed = max(properties["hit"][0], max_parsed)

        if properties["target"]:
            v = properties["target"][1]
            try:
                c = int(v[0])
            except:
                c = target_count_map[v[0]]
            attack["target"] = {"count":c, "type":v[1]}
            if v[2] and v[2].strip():
                attack["target"]["post_text"] = v[2].strip()
            max_parsed = max(properties["hit"][0], max_parsed)


        if properties["hit_damage"]:
            v = properties["hit_damage"][1]
            attack["damage"] = {"damage":{"average":v[0], "formula":v[1]}, "type":v[2].strip()}
            max_parsed = max(properties["hit_damage"][0], max_parsed)


        if properties["versatile_damage"]:
            v = properties["versatile_damage"][1]
            attack["versatile"] = {"damage":{"average":v[0], "formula":v[1]}, "type":v[2].strip()}
            max_parsed = max(properties["hit_damage"][0], max_parsed)

        effects = self.__create_effects(properties, start_char=max_parsed)
        if len(effects) > 0:
            attack["effects"] = effects

        return attack

    def __create_effects(self, properties: Any, start_char=0):
        '''Use results of precompiled regexes to turn action text into structred effect data'''
        
        used_conditions = []
        used_damage = []
        used_halves = []

        effects = []

        damage = properties["damage"] if properties["damage"] else []
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
                    "value": saves[i][1][0]
                }
                effect["on_save"] = "none"

            condition_set = set()

            ### Add damage
            for di,d in enumerate(damage):
                if di in used_damage:
                    continue
                if d[0] < start_char or d[0] > end_char:
                    continue
                if "damage" not in effect:
                    effect["damage"] = []
                effect["damage"].append({"damage":{"average":d[1][0], "formula":d[1][1]}, "type":d[1][2]})
                used_damage.append(di)

            ### Add conditions
            for ci,c in enumerate(conditions):
                if ci in used_conditions or c[1] in condition_set:
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
                            "value":escape[0][1][0]
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

    def add_action(self, section: Section, action_type: ACTION_TYPES):
        
        ### Do some parsing to get the title from the text
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

        ### Start parsing the main action text
        # Run a set of regexes over the text to pull out key information
        # First regexes handle the attack header
        properties = {}
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
            action["attack"] = self.__create_attack(title, properties)
        else:
            effects = self.__create_effects(properties)
            if len(effects) > 0:
                action["effects"] = effects

        # Look at title to pull out any associated costs/recharge/uses
        recharge_re = re.compile("recharge\s*(\d+)(?:-+(\d+))?", re.IGNORECASE)
        uses_re = re.compile(f"(\d+)\s*/\s*({'|'.join(enum_values(TIME_MEASURES))})", re.IGNORECASE)
        cost_re = re.compile(f"costs\s*\d+\s*action")

        recharge = recharge_re.findall(title)
        uses = uses_re.findall(title)
        costs = cost_re.findall(title)

        if len(recharge) == 1:
            if recharge[0][1]:
                action["recharge"] = {"from":int(recharge[0][0]), "to":int(recharge[0][1])}
            else:
                action["recharge"] = {"from":int(recharge[0][0]), "to":int(recharge[0][0])}

        if len(uses) == 1:
            action["uses"] = {"slots":int(uses[0][0]), "period":uses[0][1].lower()}

        if len(costs) == 1:
            action["cost"] = int(costs[0])
        elif action_type == ACTION_TYPES.legendary:
            action["cost"] = 1

        ### Append parsed action to data
        self.data[action_type.name].append(action)
        self.__validate_part(action_type.name)

    def add_background(self, sections: List[Section]):
        self.data["background"] = [s.get_section_text() for s in sections]