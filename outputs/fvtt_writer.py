
import os
import json
import string

from configparser import ConfigParser
from logging import Logger
from typing import Any, List

from extractor import constants
from utils.datatypes import Source
from utils.interacter import get_input
from outputs.writer_interface import WriterInterface

from outputs.fvtt.converter import FVTTConverter
from outputs.fvtt.types import CompendiumTypes

from enum import Enum, auto
import traceback

def int_to_add_string(i: int):
    if i >= 0:
        return "+{}".format(i)
    else:
        return str(i)

class FVTTWriter(WriterInterface):

    def __init__(self, config: ConfigParser, logger: Logger, append: bool=False):
        self.logger = logger.getChild("fvtt_out")
        self.config = config
        self.append = append

        self.COREVERSION='9.242'
        self.SYSTEMVERSION='1.5.7'
        self.SYSTEM='dnd5e'

    @staticmethod
    def get_long_name() -> str:
        '''Returns a human readable name for this output writer'''
        return "Foundry VTT Export"

    @staticmethod
    def get_name() -> str:
        '''Returns an internal name for this output writer'''
        return "fvtt"

    @staticmethod
    def get_filetype() -> str:
        '''Returns the output filetype of this writer'''
        return "json"

    def create_compendium_pack(self, label: str, entity: CompendiumTypes=CompendiumTypes.Actor, root: str='p2v', package: str=None):

        if package == None:
            package = label.replace(" ", "_").lower()
            sanitized_package = ""
            for c in package:
                if c not in string.ascii_lowercase + "0123456789_-":
                    continue
                sanitized_package += c
            package = sanitized_package

        return {
            "package": f"{root}.{package}",
            "metadata": {
                "name":package,
                "label":label,
                "path":f"./packs/{package}.db",
                "entity": entity.name,
                "type": entity.name,
                "system": self.SYSTEM,
                "package": root
            },
            "type": entity.name,
            "items": [],
            "source": {
                "world": root,
                "system": self.SYSTEM,
                "version": {
                    "core": self.COREVERSION,
                    "system": self.SYSTEMVERSION
                }
            }
        }

    def write(self, filename: str, source: Source, creatures: List[Any], append: bool=None) -> bool:
        '''Writes the creatures to the specified file. If append is set to true, creatures will be inserted into the existing file. Returns True if write is successful'''

        ### Apply configuration overrides
        if append is None:
            append = self.append

        ### Ensure we're writing something with the correct filetype
        if not filename.endswith(FVTTWriter.get_filetype()):
            if len(filename.split(".")) > 1:
                filename = ".".join(filename.split(".")[:-1])
            filename += "." + FVTTWriter.get_filetype()

        make_file = False
        if not os.path.exists(filename) or not append:
            make_file = True
            self.logger.debug("Writing new file")
        elif not os.path.isfile(filename):
            self.logger.error("Output file is a directory. Can't write")
            return False

        ### Get additional information
        if not self.config.getboolean("default", "use_defaults"):
            print()
            label = get_input("Source Title", "Title for this source", source.name)
            print()
        else:
            label = source.name


        data = None
        if make_file:
            data = self.create_compendium_pack(label)
        else:
            with open(filename, 'r') as f:
                data = json.load(f)
        
        converter = FVTTConverter(self.config, self.logger)
        for creature in creatures:
            try:
                cr = converter.convert_creature(creature)
            except Exception as e:
                traceback.print_exc()
                exit(e)
            if cr is None: 
                self.logger.error("Failed to convert {}".format(creature['name']))
                continue
            #     # cr["source"] = source_meta["json"]
            # except Exception as e:
            #     self.logger.error(f"Failed to convert creature {creature['name']}")
            #     self.logger.error(f"Error: {e}")
            #     continue

            data['items'].append(cr)

        #     ### Replace monsters with the same name from the same source
        #     replaced=False
        #     for i,monster in enumerate(data["monster"]):
        #         if monster["name"] == cr["name"] and monster["source"] == source_meta["json"]:
        #             data["monster"][i] = cr
        #             replaced = True
        #             break
            
        #     if not replaced:
        #         data["monster"].append(cr)

        # if make_file:
        #     data["_meta"]["dateAdded"] = int(time.time())
        # data["_meta"]["dateLastModified"] = int(time.time())

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return True



  