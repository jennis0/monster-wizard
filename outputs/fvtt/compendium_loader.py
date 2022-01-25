from distutils.log import Log
import json
import os
from copy import deepcopy

from configparser import ConfigParser
from logging import Logger
from typing import List, Optional, Any

from outputs.fvtt.types import CompendiumTypes

class CompendiumLoader(object):

    def __format_name(self, s):
        return s.lower().replace(" ","")

    def __format_image_name(self, s):
        return "".join([s.strip() for s in s.lower().split() if s])

    def load_compendium(self, data):
        if data["type"].lower() not in self.compendia:
            self.compendia[data["type"].lower()] = {}
        target = self.compendia[data["type"].lower()]
        for item in data["items"]:
            target[self.__format_name(item["name"])] = item

    def __merge_dicts(self, d1, d2):
        for k in d2:
            if k in d1:
                for n in d2[k]:
                    if n in d1[k]:
                        d1[k][n] += d2[k][n]
                    else:
                        d1[k][n] = d2[k][n]
            else:
                d1[k] = d2[k]

    def __get_images(self, data):
        images = {}
        if isinstance(data, dict):
            if "name" in data and "img" in data:
                name = data["name"]
                img = data["img"]
                if "tokens" not in img and "mystery-man" not in img:
                    name = self.__format_image_name(name)
                    images[name] = {data["img"]:1}

            for k in data:
                if k == "name" or k == "img":
                    continue

                self.__merge_dicts(images, self.__get_images(data[k]))

        elif isinstance(data, list):
            for entry in data:
                self.__merge_dicts(images, self.__get_images(entry))

        return images

    def to_map(self, images):
        data = {}
        for k in images:
            path = max(images[k].items(), key=lambda x: x[1])[0]
            data[k] = path

        return data

    def __init__(self, config: ConfigParser, logger: Logger):
        self.config = config
        self.logger = logger.getChild("fvtt_cmp_loader")

        compendiums = []
        compendium_dir = self.config.get("foundry", "compendium-dir", fallback="./foundry")
        for f in os.listdir(compendium_dir):
            if ".json" not in f:
                continue
            compendiums.append(os.path.join(compendium_dir, f))
        for f in self.config.get("foundry", "compendia", fallback="").split(","):
            if f != "":
                compendiums.append(f)

        self.compendia = {}
        for c in compendiums:
            self.logger.info(f"Loading compendium {c}")
            with open(c, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.load_compendium(data)

        for c in self.compendia:
            self.logger.info(f"Processing {len(self.compendia[c])} entries of type {c}")

        self.image_paths = self.to_map(self.__get_images(self.compendia[CompendiumTypes.Item.name.lower()]))
        self.actor_image_paths = self.to_map(self.__get_images(self.compendia[CompendiumTypes.Actor.name.lower()]))

        self.logger.info(f"Loaded {len(self.image_paths)} entries of type 'item'")
        self.logger.info(f"Loaded {len(self.actor_image_paths)} entries of type 'actor'")


    def query_compendium(self, type: CompendiumTypes, name: str) -> Optional[Any]:
        '''
        Check loaded foundry compendia looking for items with the same name.
        type: A foundry compendium type (e.g. Actor or Item)
        name: The name of the item you're looking for
        returns: Json blob of the item or None
        '''
        target_type = type.name.lower()
        if target_type not in self.compendia:
            return None

        n = self.__format_name(name)
        if n in self.compendia[target_type]:
            return deepcopy(self.compendia[target_type][n])
        return None

    def query_compendium_image(self, name: str, remove_brackets=True, type='item') -> Optional[str]:
        '''
        Looks for an existing compendium entry with the same name to take an image from
        name: Name of the item you wish to search for. This currently trys to find an exact match
        type: Can be either 'item' or 'actor'
        '''

        if type == 'item':
            paths = self.image_paths
        else:
            paths = self.actor_image_paths

        ### Try full name first
        n = self.__format_image_name(name)
        if n in paths:
            if type == 'actor':
                print(n, paths[n])
            return paths[n]

        ### Try after removing brackets
        if remove_brackets and "(" in n:
            n = n.split("(")[0]

        if n in paths:
            return paths[n]

        return "icons/svg/mystery-man.svg"
