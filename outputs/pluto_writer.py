
import os
import re
import json
import time

from configparser import ConfigParser
from logging import Logger
from typing import Any, List

from extractor import constants
from utils.datatypes import Source
from utils.interacter import get_input
from outputs.writer_interface import WriterInterface

def int_to_add_string(i: int):
    if i >= 0:
        return "+{}".format(i)
    else:
        return str(i)

class PlutoWriter(WriterInterface):

    def __init__(self, config: ConfigParser, logger: Logger, append: bool=False):
        self.logger = logger.getChild("pluto_out")
        self.config = config
        self.append = append

    @staticmethod
    def get_long_name() -> str:
        '''Returns a human readable name for this output writer'''
        return "5e Compatible"

    @staticmethod
    def get_name() -> str:
        '''Returns an internal name for this output writer'''
        return "5et"

    @staticmethod
    def get_filetype() -> str:
        '''Returns the output filetype of this writer'''
        return ".json"

    def write(self, filename: str, source: Source, creatures: List[Any], append: bool=None) -> bool:
        '''Writes the creatures to the specified file. If append is set to true, creatures will be inserted into the existing file. Returns True if write is successful'''

        ### Apply configuration overrides
        if append is None:
            append = self.append

        ### Ensure we're writing something with the correct filetype
        if not filename.endswith(PlutoWriter.get_filetype()):
            filename = ".".join(filename.split(".")[:-1]) + PlutoWriter.get_filetype()

        make_file = False
        if not os.path.exists(filename) or not append:
            make_file = True
            self.logger.debug("Writing new file")
        elif not os.path.isfile(filename):
            self.logger.error("Output file is a directory. Can't write")
            return False

        data = None
        if make_file:
            data = {
                "_meta":{
                    "sources":[],
                    "dateAdded":int(time.time()),
                    "dateLastModified":int(time.time())
                }
            }
        else:
            with open(filename, 'r') as f:
                data = json.load(f)

        source_meta = self.__source_to_meta(source)

        source_exists = False
        for source_entry in data["_meta"]["sources"]:
            if source_entry["json"] == source_meta["json"]:
                source_exists = True
                source_meta = source_entry
                break

        ### Get additional information
        print()
        source_meta["full"] = get_input("Source Title", "Title for this source", source_meta["full"])
        source_meta["abbreviation"] = get_input("Source Abbreviation", "Abbreviation for this source", source_meta['abbreviation'])
        source_meta["authors"] = get_input("Authors", "Comma-delimited list of authors", source_meta["authors"], is_list=True)
        source_meta["convertedBy"] = get_input("Converters", "Comma-delimited list of converters", source_meta["convertedBy"], is_list=True) 
        print()
        
        if not source_exists:
            self.logger.debug("Making new source entry")
            data["_meta"]["sources"].append(source_meta)
        
        if "monster" not in data:
            data["monster"] = []

        for creature in creatures:
            try:
                cr = self.__convert_creature(creature.to_json())
                cr["source"] = source_meta["json"]
            except Exception as e:
                self.logger.error(e)


            ### Replace monsters with the same name from the same source
            replaced=False
            for i,monster in enumerate(data["monster"]):
                if monster["name"] == cr["name"] and monster["source"] == source_meta["json"]:
                    data["monster"][i] = cr
                    replaced = True
                    break
            
            if not replaced:
                data["monster"].append(cr)

        if make_file:
            data["_meta"]["dateAdded"] = int(time.time())
        data["_meta"]["dateLastModified"] = int(time.time())

        with open(filename, 'w') as f:
            json.dump(data, f)

        return True


    def __source_to_meta(self, source: Source) -> Any:
        '''Create the metadata for the file'''

        ### Create JSON-ified title
        to_remove = [":",";",",","?",".","/","\\", '"', "'"]
        json_title = source.name.replace(" ","_")
        for c in to_remove:
            json_title = json_title.replace(c, "_")

        ### Create Abbreviation
        stop_words = ["of","and","the","in","a","an"]

        title = source.name.split("\\")[-1]

        data = {
            "json": json_title,
            "abbreviation":"".join(w[0].upper() for w in source.name.split() if w not in stop_words),
            "full": title,
            "authors": source.authors,
            "url": source.url,
            "convertedBy":["StatblockParser"],
            "version":"1.0",
            "targetSchema":"1.0.8"
        }

        return data

    def __convert_creature(self, creature: Any) -> Any:
        '''Converts a creature from the default format to the 5e tools format'''

        new_creature = {}

        #### Header ####
        new_creature["name"] = creature["name"]

        if "size" in creature:
            new_creature["size"] = creature["size"][0].upper()

        if "creature_type" in creature:
            if creature["creature_type"]["swarm"]:
                new_creature["type"] = {
                    "type":creature["creature_type"],
                    "swarmSize":new_creature["size"]
                }
            else:
                new_creature["type"] = creature["creature_type"]["type"]

        if "alignment" in creature:
            new_creature["alignment"] = self.__convert_alignment(creature["alignment"])
        else:
            new_creature["alignment"] = ['U']

        if "ac" in creature:
            new_creature["ac"] = self.__convert_ac(creature["ac"])
        else:
            new_creature["ac"] = [{"ac":0}]

        if "hp" in creature:
            new_creature["hp"] = creature["hp"]
        else:
            new_creature["hp"] = {"special":0}

        if "speed" in creature:
            new_creature["speed"] = self.__convert_speed(creature["speed"])
        else:
            new_creature["speed"] = {}


        ### Traits ###
        if "abilities" in creature:
            for abl in creature["abilities"]:
                new_creature[abl] = creature["abilities"][abl]

        if "saves" in creature:
            new_creature["save"] = {}
            for save in creature["saves"]:
                new_creature["save"] = int_to_add_string(creature["saves"][save])

        if "skills" in creature:
            new_creature["skill"] = {}
            for s in creature["skills"]:
                new_creature["skill"][s["skill"].lower()] = int_to_add_string(s["mod"])

        if "senses" in creature:
            new_creature["sense"] = []
            new_creature["senseTags"] = []
            for sense in creature["senses"]:
                new_creature["sense"].append("{} {} {}.".format(sense["sense"].lower(), sense["distance"], sense["measure"]))
                if sense["sense"] == constants.SENSES.truesight.value:
                    new_creature["senseTags"].append('U')
                else:
                    new_creature["senseTags"].append(sense["sense"][0].upper())

        if "passive" in creature:
            new_creature["passive"] = creature["passive"]

        if "resistances" in creature:
            new_creature["resist"] = []
            for r in creature["resistances"]:
                new_creature["resist"].append(self.__format_pre_post_value(r, 'resist'))

        if "vulnerabilities" in creature:
            new_creature["vulnerable"] = []
            for r in creature["vulnerabilities"]:
                new_creature["vulnerable"].append(self.__format_pre_post_value(r, 'vulnerable'))

        if "condition_immunities" in creature:
            new_creature["conditionImmune"] = []
            for r in creature["condition_immunities"]:
                new_creature["conditionImmune"].append(self.__format_pre_post_value(r, 'conditionImmune'))

        if "damage_immunities" in creature:
            new_creature["immune"] = []
            for r in creature["damage_immunities"]:
                new_creature["immune"].append(self.__format_pre_post_value(r, 'immune'))

        if "languages" in creature:
            new_creature["languages"] = creature["languages"]

        if "cr" in creature:
            if len(creature["cr"].keys()) == 1:
                new_creature["cr"] = creature["cr"]["cr"]
            else:
                new_creature["cr"] = creature["cr"]

        #### Features ###
        if "features" in creature:
            new_creature["trait"] = []
            for feature in creature["features"]:
                new_creature["trait"].append(
                    {
                        "name":feature["title"],
                        "entries":[self.__format_text(feature["text"])]
                    }
                )

        if "spellcasting" in creature:
            new_creature["spellcasting"] = []
            for feature in creature["spellcasting"]:
                new_feat = {
                    "name": feature["title"],
                    "headerEntries": [feature["text"]],
                    "ability":feature["mod"],
                    "type":"spellcasting"
                }
                if "post_text" in feature:
                    new_feat["footerEntries"] = [feature["post_text"]]

                levelled_spells = {}
                for level in feature["levels"]:
                    spell_list = ["{@spell "+ spell + "}" for spell in level["spells"]]
                    freq = level["frequency"]
                    
                    if freq in ["constant", "will"]:
                        new_feat[freq] = spell_list

                    if freq in ["daily", "rest", "weekly"]:
                        title = "{}{}".format(level["slots"] if "slots" in level else 1, "e" if "each" in level and level["each"] else '')
                        new_feat[freq] = {
                            title: spell_list
                        }

                    elif freq == "levelled":
                        if level["level"] == "cantrip":
                            levelled_spells['0'] = {
                                "spells": spell_list
                            }
                        else:
                            levelled_spells[level["level"]] = {
                                "spells": spell_list,
                                "slots": level["slots"] if "slots" in level else 0
                            }
                if len(levelled_spells.keys()) > 0:
                    new_feat["spells"] = levelled_spells
                new_creature["spellcasting"].append(new_feat)



        ### Actions ###
        if "action" in creature:
            new_creature["action"] = []
            for action in creature["action"]:
                new_creature["action"].append(
                    {
                        "name": action["title"],
                        "entries": [self.__format_text(action["text"])]
                    }
                )

        ### Legendary Actions ###
        if "legendary" in creature:
            new_creature["legendary"] = []
            for legendary in creature["legendary"]:
                new_creature["legendary"].append(
                    {
                        "name": legendary["title"],
                        "entries": [self.__format_text(legendary["text"])]
                    }
                )

        ### Bonus Actions ###
        if "bonus" in creature:
            new_creature["bonus"] = []
            for bonus in creature["bonus"]:
                new_creature["bonus"].append(
                    {
                        "name": bonus["title"],
                        "entries": [self.__format_text(bonus["text"])]
                    }
                )

        ### Lair Actions ###
        if "lair" in creature:
            new_creature["lair"] = []
            for lair in creature["lair"]:
                new_creature["lair"].append(
                    {
                        "name": lair["title"],
                        "entries": [self.__format_text(lair["text"])]
                    }
                )

        ### Fluff ###
        if "background" in creature:
            new_creature["fluff"] = {}
            new_creature["fluff"]["entries"] = creature["background"]

        return new_creature


    ######################################################################################
    ######################################  Header  ######################################
    ######################################################################################


    def __format_from_ac_str(self, from_str: str) -> str:
        '''Handle special cases where ac is not from armour'''
        if from_str.lower() == "natural armour" or from_str.lower() == "natural armor":
            return from_str
        if from_str.lower() == "unarmoured defence" or from_str.lower() == "unarmored defence":
            return from_str
        
        return "{@item " + from_str + "}"


    def __convert_ac(self, ac : Any) -> Any:
        '''Convert AC schema'''
        new_ac = []

        for entry in ac:
            new_ac.append({
                "ac": entry["ac"],
            })
            if len(entry["from"]) > 0:
                new_ac[-1]["from"] = [self.__format_from_ac_str(item) for item in entry["from"]]
            if entry["condition"] != '':
                new_ac[-1]["condition"] = entry["condition"]
            
        return new_ac

    def __convert_speed(self, speeds: Any) -> Any:
        '''Convert Speed Schema'''
        new_speed = {}
        for speed in speeds:
            new_speed[speed["type"]] = speed["distance"]
        return new_speed

    def __convert_alignment(self, alignment_string: str) -> List[str]:
        '''Returns list of possible alignments'''
        align = []
        parts = [p.strip() for p in alignment_string.upper().split()]
        if len(parts) == 0:
            align=['U']
        elif parts[0] == "ANY":
            if len(parts) == 1:
                align = ['A']
            elif parts[1] == "CHAOTIC" or parts[1] == 'LAWFUL' :
                align = [parts[1][0], 'G', 'NY', 'E']
            elif parts[1] == 'GOOD' or parts[1] == 'EVIL':
                align = ['L', 'NX', 'C', parts[1][0]]
            elif parts[1] == 'NEUTRAL':
                align = ['NX', 'NY', 'N']
            elif parts[1].startswith('NON'):
                if parts[1] == "NON-CHAOTIC":
                    align = ['NX', 'L', 'G', 'NY', 'E']
                elif parts[1] == 'NON-LAWFUL' :
                    align = ['C', 'NX', 'G', 'NY', 'E']
                elif parts[1] == 'NON-GOOD':
                    align = ['L', 'NX', 'C', 'NY', 'E']
                elif parts[1] == 'NON-EVIL':
                    align =  ["L", "NX","C", "NY", "G"]
            else:
                align = ['A']
        elif parts[0] == 'UNALIGNED':
            align = ['U']
        else:
            if len(parts) == 1:
                align = [parts[0][0]]

            else:
                align = [parts[0][0], parts[1][0]]

        if len(align) == 0:
            self.logger.warning("Failed to convert alignment string {}".format(alignment_string))
            return []

        return align

    ######################################################################################
    ####################################  Features  ######################################
    ######################################################################################

    def __format_pre_post_value(self, value: Any, title: str) -> Any:
        # if value["pre_text"].strip() != '' or value["post_text"].strip() != '':
        new_v = {
                title:value["type"],
            }
        if value["pre_text"].strip() != '':
            new_v["note"] = value["pre_text"],
        if value["post_text"].strip() != '':
            new_v["postNote"] = value["post_text"]
        # else:
        #     return value[]

        return new_v

    def __replace_damage(self, text):
        return re.sub("\s*([0-9]+\s)?(\()?((?:[+-]?\s*[0-9]+d[0-9]+\s*)+(?:[+-]?\s*[0-9]+)?)(\)?\s+)(({})\s+damage)".format("|".join(constants.enum_values(constants.DAMAGE_TYPES))),
            " \g<1>\g<2>{@damage \g<3>}\g<4>\g<5>", text, flags=re.IGNORECASE)

    def __replace_dcs(self, text):
        return re.sub("\s+(dc)\s*([0-9]+)([()\s,])".format("|".join(constants.enum_values(constants.ABILITIES))), " {@dc \g<2>}\g<3>", text, flags=re.IGNORECASE)

    def __replace_hit(self, text):
        return re.sub("\s([+-]?[0-9]+)\s*to\s*hit", " {@hit \g<1>} to hit", text, flags=re.IGNORECASE)

    def __replace_rolls(self, text):
        return re.sub("(?<!damage\s)([0-9]+d[0-9]+)\s*([+-]\s*[0-9]+)?\s*([^}])", " {@dice \g<1>\g<2>} \g<3>", text)

    def __format_text(self, text: str) -> str:

        text = self.__replace_hit(text)
        text = re.sub("Melee\s*or\s*Ranged\s*Weapon\s*Attack", "{@atk mw,rw}", text, re.IGNORECASE)
        text = re.sub("Melee\s*Weapon\s*Attack:", "{@atk mw}", text, re.IGNORECASE)
        text = re.sub("Ranged\s*Weapon\s*Attack:", "{@atk rw}", text, re.IGNORECASE)
        text = self.__replace_damage(text)
        text = re.sub("(?:Hit: )([0-9]+)\s", "{@h}\g<1> ", text, flags=re.IGNORECASE)
        text = self.__replace_dcs(text)
        text = self.__replace_rolls(text)
        
        return text