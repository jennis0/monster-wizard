import os
import json
from configparser import ConfigParser
from logging import Logger
from typing import Any, List

from utils.datatypes import Source
from outputs.writer_interface import WriterInterface



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

        if not os.path.exists(filename) or append:
            make_file = True
            self.logger.debug("Writing new file")
        elif not os.path.isfile(filename):
            self.logger.error("Output file is a directory. Can't write")
            return False

        with open(filename, 'r') as f:
            if make_file:
                data = []
            else:
                data = json.load(f)

        written = False
        for source_entry in data:
            if source_entry["title"] == source.name:
                source_entry["creatures"] += [self.__convert_creature(c) for c in creatures]
                written = True
                self.logger.debug("Appending creatures to existing source")
                break
        
        if not written:
            self.logger.debug("Making new source entry")
            data.append(
                {
                    "title": source.name,
                    "creatures": [self.__convert_creature(c.to_json()) for c in creatures]
                }
            )
            if source.authors is not None:
                data[-1]["authors"] = source.authors
            if source.url is not None:
                data[-1]["url"] = source.url

        with open(filename, 'w') as f:
            json.dump(data, f)

        return True



    def __convert_creature(self, creature: Any) -> Any:
        '''Converts a creature from the default format to the 5e tools format'''

        new_creature = {}

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

        if "ac" in creature:
            new_creature["ac"] = self.__convert_ac(creature["ac"])

        if "hp" in creature:
            new_creature["hp"] = creature["hp"]

        if "speed" in creature:
            new_creature["speed"] = self.__convert_speed(creature["speed"])

        return new_creature

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

