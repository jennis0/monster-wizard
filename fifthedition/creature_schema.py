import fifthedition.constants as constants
from enum import Enum
import re

from schema import Schema, And, Or, Use, Optional

def enum_str(options: Enum):
    return And(str, Use(str.lower), lambda s: constants.is_in_enum(s, options))

def pre_post_schema(options: Enum) -> Schema:
    return Schema(
        {
            "type": [enum_str(options)],
            "pre_text": str,
            "post_text": str
        }
    )

AverageDiceSchema = Schema(
    {
        "average": int,
        "formula": str
    }
)

HPSchema = Or(AverageDiceSchema, Schema({"special":int}))

CreatureTypeSchema = Schema(
    {
        "type": Or('any', enum_str(constants.CREATURE_TYPES)),
        "swarm": bool,
        "swarm_size": Or(enum_str(constants.SIZES), None)
    }
)

SizeSchema = enum_str(constants.SIZES)

ACSchema = Schema(
    {
        "ac":int,
        "from":[str],
        "condition":str
    }
)

SpeedSchema = Schema( 
    {
        "type": enum_str(constants.MOVEMENT_TYPES),
        "distance": int,
        "measure": enum_str(constants.MEASURES)
    }
)

SkillSchema = Schema(
    {
        "skill": Or(enum_str(constants.SKILLS), lambda x: x.strip().lower().endswith("tools")),
        "mod": int
    }
)

DamageResistSchema = pre_post_schema(constants.DAMAGE_TYPES)
ConditionResistSchema = pre_post_schema(constants.CONDITIONS)

UsesSchema = Schema(
    {
        "slots": int,
        "period": Or("day", "rest", "encounter", "long rest", "short rest")
    }
)

SenseSchema = Schema(
    {
        "sense":enum_str(constants.SENSES),
        "distance":int,
        "measure": enum_str(constants.MEASURES)
    }
)

CRSchema = Schema(
    {
        "cr": And(str, lambda x: re.match("[0-9/]+", x) != None),
        Optional("lair"): And(str, lambda x: re.match("[0-9/]+", x) != None),
        Optional("coven"):  And(str, lambda x: re.match("[0-9/]+", x) != None)
    }
)

DurationSchema = Schema(
    {
        "length":int,
        "measure":enum_str(constants.TIME_MEASURES)
    }
)

DamageSchema = Schema(
    {
        "damage": AverageDiceSchema,
        "type": enum_str(constants.DAMAGE_TYPES),
        "on_save": Or("none", "halved", "applied")
    }
)

ConditionSchema = Schema(
    {
        "condition": enum_str(constants.CONDITIONS),
        "duration": DurationSchema,
        "on_save": Or("none", "applied")
    }
)

EffectSchema = Schema({
        Optional("damage"): [DamageSchema],
        Optional("condition"): [ConditionSchema],
        Optional("save"): {
            "ability": enum_str(constants.SHORT_ABILITIES),
            "value": int
        }
    }
)

RangeSchema = Schema(
    {
        "distance": int,
        Optional("long_distance"): int,
        "measure": enum_str(constants.MEASURES)
    }
)

AttackSchema = Schema(
    {
        "name": str,
        "type": Or("melee", "ranged", "both"),
        Optional("reach"): {
            "distance":int,
            "measure":enum_str(constants.MEASURES)
        },
        Optional("range"): {
            "short_distance":int,
            "long_distance":int,
            "measure":enum_str(constants.MEASURES)
        },
        "hit":int,
        "target": Or("one target"),
        "effects": [EffectSchema],
    }
)

FeatureSchema = Schema(
    {
        "title":str,
        "text":str,
        Optional("attack"): AttackSchema,
        Optional("effect"): [EffectSchema]
    }
)

ActionSchema = Schema(
    {
        "title":str,
        "text":str,
        "type": enum_str(constants.ACTION_TYPES),
        Optional("attack"): AttackSchema,
        Optional("effect"): EffectSchema,
        Optional("cost"): int,
        Optional("uses"): UsesSchema,
        Optional("recharge"): [int]
    }
)

SpellLevelSchema = Schema(
    {
        "frequency": enum_str(constants.SPELL_FREQUENCIES),
        "spells": [str],
        Optional("level"): Or('cantrip','1','2','3','4','5','6','7','8','9'),
        Optional("each"): bool,
        Optional("slots"): int
    }
)

SpellcastingSchema = Schema(
    {
        "title": str,
        "mod": enum_str(constants.SHORT_ABILITIES),
        "text":str,
        "levels": [SpellLevelSchema],
        Optional("save"):int,
        Optional("post_text"):str
    }
)

CreatureSchema = Schema(
    {
        ### Basics
        "name": str,
        "size": SizeSchema,
        "creature_type": CreatureTypeSchema,
        "alignment":str,
        "ac": [ACSchema],
        "hp": HPSchema,
        "speed": [SpeedSchema],

        ### Abilities
        "abilities": {
            "str": int,
            "dex": int,
            "con": int,
            "int": int,
            "wis": int,
            "cha": int
        },

        ### Traits
        Optional("saves"): {
            Optional("str"): int,
            Optional("dex"): int,
            Optional("con"): int,
            Optional("int"): int,
            Optional("wis"): int,
            Optional("cha"): int
        },

        Optional("skills"): [SkillSchema],
        Optional("senses"): [SenseSchema],
        Optional("passive"): int,
        Optional("resistances"): [DamageResistSchema],
        Optional("damage_immunities"):[DamageResistSchema],
        Optional("condition_immunities"):[ConditionResistSchema],
        Optional("vulnerabilities"):[DamageResistSchema],
        Optional("languages"):[str],
        Optional("cr"):CRSchema,
        Optional("proficiency"):int,

        ### Features
        Optional("features"): [FeatureSchema],
        Optional("spellcasting"): [SpellcastingSchema],

        ### Actions
        Optional("action"): [ActionSchema],
        Optional("bonus"): [ActionSchema],
        Optional("legendary"): [ActionSchema],
        Optional("mythic"): [ActionSchema],
        Optional("reaction"): [ActionSchema],
        Optional("lair"): [ActionSchema],

        #Descriptive block for legendary actions
        Optional("legendary_block"): str

    }
)
