import os
import random

from math import floor
import string


from configparser import ConfigParser
from logging import Logger

from ..fvtt.types import CompendiumTypes
from ..fvtt.compendium_loader import CompendiumLoader
from ...core.creature_schema import ActionSchema, SpellLevelSchema, SpellSchema
from ...core import constants
from ...utils import text_format as fmt

from typing import Any, Dict

class FVTTConverter(object):

    __SIZEMAP = {
        constants.SIZES.tiny.name: "tiny",
        constants.SIZES.small.name: "sm",
        constants.SIZES.medium.name: "med",
        constants.SIZES.large.name: "lg",
        constants.SIZES.huge.name: "huge",
        constants.SIZES.gargantuan.name: "grg"
    }

    __SKILLATRMAP = {
        "acr":"dex",
        "ani":"wis",
        "arc":"int",
        "ath":"str",
        "dec":"cha",
        "his":"int",
        "ins":"wis",
        "itm":"cha",
        "inv":"int",
        "med":"wis",
        "nat":"int",
        "prc":"wis",
        "prf":"cha",
        "per":"cha",
        "rel":"int",
        "slt":"dex",
        "ste":"dex",
        "sur":"wis"
    }

    __PROFICIENCIES = [
        #Artisan Tools
        "art"
        "alchemist",
        "brewer",
        "carpenter",
        "cartographer",
        "cobbler",
        "cook",
        "glassblower",
        "jeweler",
        "leatherworker",
        "mason",
        "painter",
        "potter",
        "smith",
        "tinker",
        "weaver",
        "woodcarver",
        #Instruments
        "instrument"
        "bagpipes",
        "drum",
        "dulcimer",
        "flute",
        "horn",
        "lute",
        "lyre",
        "pan flute",
        "shawm",
        "viol",
        "violin",
        #Gaming
        "gam",
        "chess",
        "dice",
        "playing cards",
        #Kits
        "disguise",
        "forgery",
        "navigator",
        "poisoner",
        "thieves",
        #Vehicles
        "vehicle"
        "air",
        "land",
        "water"
    ]

    __FREQUENCYMAP = {
        constants.SPELL_FREQUENCIES.encounter.name: "sr",
        constants.SPELL_FREQUENCIES.daily.name: "day",
        constants.SPELL_FREQUENCIES.rest.name: "lr",
        constants.SPELL_FREQUENCIES.weekly.name: "charges",
        constants.SPELL_FREQUENCIES.cantrip.name: "",
        constants.SPELL_FREQUENCIES.will.name: "",
        constants.TIME_MEASURES.day.name: "day",
    }

    __IDCHARS = string.ascii_letters + "0123456789"

    def __generate_id(self):
        return "".join([random.choice(FVTTConverter.__IDCHARS) for i in range(16)])

    def __make_feature(self, title: str, description: str, get_image: bool=True):
        return  {
        "_id": self.__generate_id(),
        "name": title,
        "type": "feat",
        "img": self.cl.query_compendium_image(title, type='actor'),
        "data": {
          "description": {"value": f"<p>{description}</p>", "chat": "","unidentified": ""},
          "source": "",
          "activation": {"type": "","cost": None,"condition": ""},
          "duration": {"value": None,"units": ""},
          "target": {"value": None,"width": None,"units": "","type": ""},
          "range": {"value": None,"long": None,"units": ""},
          "uses": {"value": 0,"max": 0,"per": None},
          "consume": {"type": "","target": None,"amount": None},
          "ability": None,
          "actionType": "",
          "attackBonus": 0,
          "chatFlavor": "",
          "critical": {"threshold": None,"damage": ""},
          "damage": {"parts": [],"versatile": ""},
          "formula": "",
          "save": {"ability": "","dc": None,"scaling": "spell"},
          "requirements": "",
          "recharge": {"value": None,"charged": False},
          "attunement": 0
        },
        "effects": [],
        "folder": None,
        "sort": 200001,
        "permission": {"default": 0},
        "flags": {}
      }

    def __make_spell(self, spell: SpellSchema):
        return  {
          "_id": "1VqHo34RfZWxXk7R",
          "name": spell["name"],
          "type": "spell",
          "img": self.cl.query_compendium_image(spell["name"]),
          "data": {
            "description": {"value": "","chat": "","unidentified": ""},
            "source": "",
            "activation": {"type": "action","cost": 1,"condition": ""},
            "duration": {"value": None,"units": "inst"},
            "target": {"value": 1,"width": None,"units": "","type": "creature"},
            "range": {"value": None,"long": None,"units": "ft"},
            "uses": {"value": None,"max": None, "per":None},
            "consume": {},
            "ability": "",
            "actionType": "save",
            "attackBonus": 0,
            "chatFlavor": "",
            "critical":{"threshold":None,"damage": ""},
            "damage": {"parts": [],"versatile": ""},
            "formula": "",
            "level": 0,
            "school": "evo",
            "components": {"value": "","vocal": False,"somatic": False,"material": False,"ritual": False,"concentration": False},
            "preparation": {"mode": "prepared","prepared":True},
          }
        }

    def __make_action(self, action: ActionSchema, current_data: Any):

        core_data =   {
          "_id": self.__generate_id(),
          "name": action["title"],
          "type": "feat",
          "img": self.cl.query_compendium_image(action["title"]),
          "data": {
            "description": {"value": f"<p>{action['text']}</p>"},
            "source": "",
            "equipped": True,
            "identified": True,
            "activation": {"type": action['type'],"cost": action["cost"] if "cost" in action else 1,"condition": ""},
            "proficient": True,
            "attuned": False,
            "properties": {}
          },
          "effects": [],
          "folder": None,
          "sort": 800000,
          "permission": {
            "default": 0
          },
          "flags": {}
        }

        ### Handle action uses
        if "uses" in action:
            core_data["data"]["uses"] = {
                "value":action["uses"]["slots"],
                "max":action["uses"]["slots"],
                "per":self.__FREQUENCYMAP[action["uses"]["period"]]
            }

        ### Handle action recharge
        if "recharge" in action: 
            core_data["data"]["recharge"] = {
                "charged":True,
                "value":action["recharge"]["from"]
            }

        abls = current_data["abilities"]
        prof = int(current_data["attributes"]["prof"])

        #Handle attributes specific to attacks
        if "attack" in action:
            action_data = action['attack']

            core_data["type"] = "weapon"

            ## Handle melee attacks
            if action_data["type"] == "melee":
                if action_data["weapon"] == "weapon":
                    core_data["data"]["actionType"] = 'mwak'
                    ability = 'str'
                else:
                    core_data["data"]["actionType"] = 'msak'
                    ability = "int"
                core_data["data"]["range"] = {"value":action_data["reach"]["distance"],"long":None,"units":action_data["reach"]["measure"]}

            ## Handle ranged attacks
            else:
                if action_data["weapon"] == "weapon":
                    core_data["data"]["actionType"] = 'rwak'
                    ability = 'dex'
                else:
                    core_data["data"]["actionType"] = 'rsak'
                    ability = 'int'
                core_data["data"]["range"] = {
                    "value":action_data["range"]["short_distance"],
                    "long":action_data["range"]["long_distance"],
                    "units":action_data["range"]["measure"]
                    }

            core_data["data"]["ability"] = ability

            ### We use this to counteract Foundry's mandatory ability score adding.
            core_data["data"]["attackBonus"] = action_data["hit"] - (prof + abls[ability]["mod"])

            ### Apply damage formula
            if "damage" in action_data:
                core_data["data"]["damage"] = {
                    "parts": [[action_data["damage"]["damage"]["formula"], action_data["damage"]["type"]]]
                }

            ### Add versatile damage
            if "versatile" in action_data:
                core_data["data"]["damage"]["versatile"] = action_data["versatile"]["damage"]["formula"]
                core_data["data"]["properties"]["ver"] = True

            ### Handle effects. Note Foundry only supports a single save-based effect!
            if "effects" in action_data:
                for effect in action_data["effects"]:
                    #Only add first save since that's probably the most important
                    if "save" in effect:
                        core_data["data"]["save"] = {
                            "ability": effect["save"]["ability"][:3],
                            "dc": int(effect["save"]["value"]),
                            "scaling": "flat"
                        }  
                        if "damage" in effect:
                            for dmg in effect["damage"]:
                                core_data["data"]["formula"] = f'{dmg["damage"]["formula"]}[{dmg["type"]}]'
                    else:
                        #Handle non-save related damage
                        if "damage" in effect:
                            for dmg in effect["damage"]:
                                core_data["data"]["damage"]["parts"].append([dmg["damage"]["formula"],dmg["type"]])

        if "effects" in action:
            effect_data = action["effects"]
            for effect in effect_data:
                    if "damage" in effect:
                        for dmg in effect["damage"]:
                            core_data["data"]["formula"] = f'{dmg["damage"]["formula"]}[{dmg["type"]}]'

                    #Only add first save since that's probably the most important
                    if "save" in effect:
                        core_data["data"]["save"] = {
                            "ability": effect["save"]["ability"][:3],
                            "dc": int(effect["save"]["value"]),
                            "scaling": "flat"
                        }
                        
                    #Only add first effect                
                    break
        
        return core_data


    def __init__(self, config: ConfigParser, logger: Logger):
        self.config = config
        self.logger = logger.getChild("fvtt_conv")
        self.cl = CompendiumLoader(config, logger)

    def __handle_dr(self, values, enums):
        custom = []
        dis = []
        for di in values:
            if di["pre_text"] != "" or di["post_text"] != "":
                    custom.append("".join([di["pre_text"], ",".join(di["type"]), di["post_text"]]))
            else:
                for d in di["type"]:
                    if d in enums:
                        dis.append(d)
                    else:
                        custom.append(d)
        return {"value":dis, "custom":",".join(custom)}

    def convert_creature(self, cr: Dict[str, Any]) -> Any:
        '''Converts a creature from the default format to the FoundryVTT Actor format'''

        new_creature = {}

        #### Header ####
        new_creature["name"] = cr["name"]
        new_creature["type"] = "npc"
        new_creature["img"] = None#self.cl.query_compendium_image(cr["name"], type='actor')

        ### Creature Data ###
        data = {}
        data['abilities'] = self.ability_scores(cr, data)
        data['attributes'] = self.attributes(cr, data)
        data['details'] = self.details(cr, data)
        data['traits'] = self.traits(cr, data)
        skills, profs = self.skills_and_proficiencies(cr, data)
        data["skills"] = skills
        data["traits"]["toolProf"] = profs
        new_creature["items"] = []

        if "spellcasting" in cr:
            spell_items, spell_data = self.spells(cr, data)
            new_creature["items"] += spell_items
            data["spells"] = spell_data
        

        if "features" in cr:
            new_creature["items"] += self.features(cr, data)

        new_creature["items"] += self.actions(cr, data)

        new_creature['data'] = data
        return new_creature

    def ability_scores(self, data, current_state):
        conv = {}
        if "abilities" not in data:
            data["abilities"] = {}
        for abs in constants.enum_values(constants.SHORT_ABILITIES):
            if abs in data['abilities']:
                ab_data = data['abilities'][abs]
            else:
                ab_data = 10
            if "saves" in data and abs in data["saves"]:
                ab_save = data["saves"][abs]
            else:
                ab_save = 0
            ab_mod = int((ab_data - 10) / 2)

            conv[abs] = {
                'value': ab_data,
                "proficient": ab_save != 0,
                "bonuses": {"check":"", "save":""},
                "min": 3,
                "mod": ab_mod,
                "save": ab_mod + ab_save,
                "prof": ab_save != 0,
                "saveBonus": 0,
                "checkBonus": 0,
                "dc": 10 + ab_mod + 2 #Why?
            }
        
        return conv

    def attributes(self, data, current_state):
        conv = {}

        ### AC
        ac = {"flat":10, "calc":'natural', 'formula':'', 'min':10}
        if 'ac' in data and len(data['ac']) > 0:
            ac['flat'] = data['ac'][0]['ac'],
        else:
            ac['calc']  = 'default'
        conv["ac"] = ac

        ### HP
        hp = {"value":0, "min":0, "max":0, "temp":0, "tempmax":0, "formula":""}
        if 'hp' in data:
            if 'special' in data['hp']:
                hp["value"] = data['hp']['special']
                hp["max"] = data['hp']['special']
            else:
                hp["value"] = data["hp"]["average"]
                hp["max"] = data["hp"]["average"]
                hp["formula"] = data["hp"]["formula"]
        conv["hp"] = hp

        ### Init
        init = {"value":0, "bonus": 0, "mod": 0, "total": 0, "prof": 0}
        if "abilities" in data and "dex" in data["abilities"]:
            init['total'] = 10 + int((data['abilities']['dex'] - 10)/2)
        conv['init'] = init

        ### Movement
        move = {'burrow':0, 'climb':0, 'fly':0, 'walk':0, 'units':'ft', 'hover':False}
        if 'speed' in data:
            for entry in data['speed']:
                move[entry['type']] = entry['distance']
                move['units'] = entry['measure']
        conv['movement'] = move

        ### Senses
        senses = {"darkvision": 120,"blindsight": 0,"tremorsense": 0,"truesight": 0,"units": "ft","special": ""}
        if "senses" in data:
            for entry in data["senses"]:
                senses[entry["type"]] = entry["distance"]
                senses["units"] = entry["measure"]
        conv["senses"] = senses
    

        if "proficiency" in data:
            conv["prof"] = data["proficiency"]
        elif "cr" in data:
            conv["prof"] = 2 + floor(0.25 * (float(data["cr"]["cr"]) - 1))
        else:
            conv["prof"] = 0

        ### Spellcasting Ability
        conv["spellcasting"] = ""
        if "spellcasting" in data:
            for sc in data["spellcasting"]:
                if "mod" in sc:
                    mod = sc["mod"]
                    if mod:
                        conv["spellcasting"] = mod
                    if "save" in sc:
                        conv["spelldc"] =  sc["save"]
                    elif mod:
                        8 + current_state["abilities"][mod]["mod"] + conv["prof"]
                        
                    conv["spellLevel"] = sc["spellcastingLevel"] if "spellcastingLevel" in sc else 0
                    break

        return conv

    def details(self, data, current_state):
        conv = {}

        conv["biography"] = {}
        
        if "alignment" in data:
            conv["alignment"] = data["alignment"]

        if "type" in data:
            conv["type"] = {
                "type": data["type"]["type"],
                "swarm": data["type"]["swarm_size"] if data["type"]["swarm"] else ""
            }

        if "cr" in data:
            conv["cr"] = data["cr"]["cr"]

        if "source" in data:
            if "short_title" in data["source"]:
                title = data["source"]["short_title"]
            else:
                title = data["source"]["title"]
            if "page" in data["source"]:
                title += f" pg. {data['source']['page']}"
            conv["source"] = title

        return conv

    def traits(self, data, current_state):
        conv = {}

        if "size" in data:
            conv["size"] = self.__SIZEMAP[data["size"][0].lower()]

        damage_types = constants.enum_values(constants.DAMAGE_TYPES)
        condition_types = constants.enum_values(constants.CONDITIONS)

        if "damage_immunities" in data:
            conv["di"] = self.__handle_dr(data["damage_immunities"], damage_types)

        if "damage_resistances" in data:
            conv["dr"] = self.__handle_dr(data["damage_resistances"], damage_types)

        if "damage_vulnerabilities" in data:
            conv["dv"] = self.__handle_dr(data["damage_vulnerabilities"], damage_types)

        if "condition_immunities" in data:
            conv["ci"] = self.__handle_dr(data["condition_immunities"], condition_types)
            
        if "languages" in data:
            for l in data["languages"]:
                conv["languages"] = {
                    "value": data["languages"],
                    "custom":""
                }

        return conv

    def skills_and_proficiencies(self, data, current_state):
        conv = {}
        toolProf = {"value":[], "custom":""}
        prof = current_state["attributes"]["prof"]
        if "skills" in data:
            for skill in data["skills"]:
                if skill["skill"] in self.__SKILLATRMAP:
                    atr = self.__SKILLATRMAP[skill["skill"]]
                    total = skill["mod"]
                    mod = current_state["abilities"][atr]["mod"]

                    if total >= 2*mod + prof:
                        prof_level = 2
                    elif total >= mod + prof:
                        prof_level = 1
                    else:
                        prof_level = 0

                    conv[skill["skill"]] = {
                        "value": prof_level,
                        "ability": atr,
                        "bonuses": {"check":"", "passive":""},
                        "mod":mod,
                        "bonus":total - (mod * prof_level + prof),
                        "passive": 10 + total,
                        "prof": prof,
                        "total":total
                    }

                # Handle tools, gaming sets and instruments
                else:
                    for k in self.__PROFICIENCIES:
                        if k in skill["skill"]:
                            toolProf["value"].append(k)
                        else:
                            toolProf["custom"] += skill["skill"].strip() + ";"

        return conv, toolProf

    def __prepare_spell(self, sl: SpellLevelSchema, orig: SpellSchema, spell: Any):
        if sl["frequency"] != constants.SPELL_FREQUENCIES.levelled.name:
            spell['data']["preparation"] = {"mode":"innate","prepared":True}

            # Note that Foundry currently has no way to link 'X/day' spells uses so spells get separate counters
            if sl["frequency"] == constants.SPELL_FREQUENCIES.will.name:
                spell['data']['uses'] = {"value":None,"max":None,"per":None}
            else:
                spell["data"]["uses"] = {
                    "value":sl["slots"] if "slots" in sl else 1,
                    "max": sl["slots"] if "slots" in sl else 1,
                    "per": self.__FREQUENCYMAP[sl['frequency']]
                }

            if "level" in orig:
                spell["data"]["level"] = orig["level"]

        spell["name"] = fmt.upcase(fmt.spell(orig).strip())
        return spell      

    def spells(self, data, current_state):
        spell_items = []
        spell_data = {
            "spell1": {"value": 0,"override": None, "max": 0},
            "spell2": {"value": 0,"override": None, "max": 0},
            "spell3": {"value": 0,"override": None, "max": 0},
            "spell4": {"value": 0,"override": None, "max": 0},
            "spell5": {"value": 0,"override": None, "max": 0},
            "spell6": {"value": 0,"override": None, "max": 0},
            "spell7": {"value": 0,"override": None, "max": 0},
            "spell8": {"value": 0,"override": None, "max": 0},
            "spell9": {"value": 0,"override": None, "max": 0},
            "spell0": {"value": 0,"override": None, "max": 0},
            "pact":   {"value": 0,"override": None, "max": 0},       
        }

        if "spellcasting" not in data:
            return spell_items, spell_data

        for sc in data["spellcasting"]:
            feat = self.__make_feature(sc["title"], fmt.spellblock(sc))
            spell_items.append(feat)

            for level in sc["levels"]:
                for spell in level["spells"]:
                    resolved_spell = self.cl.query_compendium(CompendiumTypes.Item, spell["name"], distance_threshold=2)
                    if resolved_spell is None:
                        self.logger.warning(f"Could not find spell {spell} in compendium")
                        resolved_spell = self.__make_spell(spell)
                        resolved_spell["data"]["description"]["value"] = "<p>Failed to import</p>"

                    spell_items.append(self.__prepare_spell(level, spell, resolved_spell))

                    #Set number of spell slots. Note we assume a creature onyl has one levelled spellcasting block
                    if level["frequency"] == "levelled":
                        spell_data[f"spell{level['level']}"] = {
                            "value":level["slots"] if "slots" in level else 1,
                            "override":None,
                            "max":level["slots"] if "slots" in level else 1,
                        }
                            

        return spell_items, spell_data

    def features(self, data, current_state):
        features= []

        for f in data["features"]:
            self.logger.debug(f"Converting action: {f['title']}")
            feat = self.__make_feature(f["title"], f["text"])
            features.append(feat)

        return features

    def actions(self, data, current_state):
        actions = []
        supported_action_types = ["action", "bonus", "reaction", "legendary"]
        unsupported_action_types = ["mythic", "lair"]

        for action_type in supported_action_types:
            if action_type not in data:
                continue
            for action in data[action_type]:
                try:
                    self.logger.debug(f"Converting action: {action['title']}")
                    actions.append(self.__make_action(action, current_state))
                except Exception as e:
                    self.logger.error(e)
                    self.logger.error(action)

        for at in unsupported_action_types:
            if at in data:
                self.logger.warn(f"Found unsupported action type {at} in creature data['name']. These will not be converted.")

        return actions