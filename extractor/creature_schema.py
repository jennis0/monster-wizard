import extractor.constants as constants
from enum import Enum
import re

from schema import Schema, And, Or, Use, Optional

def enum_str(options: Enum):
    return And(str, Use(str.lower), lambda s: constants.is_in_enum(s.replace(" ", "_"), options))

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

HPSchema = Or(AverageDiceSchema, Schema({"special":str}))

CreatureTypeSchema = Schema(
    {
        "type": [Or('any', enum_str(constants.CREATURE_TYPES))],
        "swarm": bool,
        "swarm_size": Or(enum_str(constants.SIZES), None)
    }
)

SizeSchema = [enum_str(constants.SIZES)]

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
        "skill": enum_str(constants.SHORT_SKILLS),
        "mod": int
    }
)

DamageResistSchema = pre_post_schema(constants.DAMAGE_TYPES)
ConditionResistSchema = pre_post_schema(constants.CONDITIONS)

UsesSchema = Schema(
    {
        "slots": int,
        "period": enum_str(constants.TIME_MEASURES)
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
        "cr": Or(float, int),
        Optional("lair"): Or(float, int),
        Optional("coven"):  Or(float, int)
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
    }
)

ConditionSchema = Schema(
    {
        "condition": enum_str(constants.CONDITIONS),
        Optional("duration"): DurationSchema,
    }
)

EffectSchema = Schema({
        Optional("damage"): [DamageSchema],
        Optional("conditions"): [ConditionSchema],
        Optional("save"): {
            "ability": Or(enum_str(constants.SHORT_ABILITIES), enum_str(constants.SKILLS), enum_str(constants.SHORT_SKILLS), "ath or acr"),
            "value": int
        },
        Optional("on_save"): Or("half", "none"),
        Optional("end_save"): {
            "ability": Or(enum_str(constants.SHORT_ABILITIES), enum_str(constants.SKILLS), enum_str(constants.SHORT_SKILLS), "ath or acr"),
            "value": int
        },
    }
)

RangeSchema = Schema(
    {
        "distance": int,
        Optional("long_distance"): int,
        "measure": enum_str(constants.MEASURES)
    }
)

TargetSchema = Schema(
    {
        "count": Or(int, "all", "any"),
        "type": Or("creature", "target", "object"),
        Optional("post_text"): str
    }
)

AttackSchema = Schema(
    {
        "name": str,
        "type": Or("melee", "ranged", "both"),
        "weapon": Or("weapon", "spell"),
        Optional("reach"): {
            "distance":int,
            "measure":enum_str(constants.MEASURES)
        },
        Optional("range"): {
            "short_distance":int,
            "long_distance": Or(int, None),
            "measure":enum_str(constants.MEASURES)
        },
        "hit":int,
        "target": TargetSchema,
        "damage": DamageSchema,
        Optional("versatile"): DamageSchema,
        Optional("effects"): [EffectSchema]
    }
)

FeatureSchema = Schema(
    {
        "title":str,
        "text":str,
        Optional("attack"): AttackSchema,
        Optional("effects"): [EffectSchema]
    }
)

ActionSchema = Schema(
    {
        "title":str,
        "text":str,
        "type": enum_str(constants.ACTION_TYPES),
        Optional("attack"): AttackSchema,
        Optional("effects"): [EffectSchema],
        Optional("cost"): int,
        Optional("uses"): UsesSchema,
        Optional("recharge"): {"from": int, "to":int}
    }
)

SpellSchema = Schema(
    {
        "name": str,
        Optional("level"): int,
        Optional("post_text"): str
    }
)

SpellLevelSchema = Schema(
    {
        "frequency": enum_str(constants.SPELL_FREQUENCIES),
        "spells": [SpellSchema],
        "level": Or('unlevelled','cantrip','1','2','3','4','5','6','7','8','9'),
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
        "spellcastingLevel": int,
        Optional("save"):int,
        Optional("post_text"):str
    }
)

SourceSchema = Schema(
    {
        "title":str,
        Optional("short_title"):str,
        Optional("page"):int,
        Optional("authors"):[str]
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
        Optional("legendary_block"): str,
        Optional("lair_block"): str,

        #Additional Text
        Optional("description"): [str],

        #Monster Source
        Optional("source"): SourceSchema

    }
)
