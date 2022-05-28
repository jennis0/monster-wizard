from . import constants
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
        },
        error="Failed to validate list text"
    )

AverageDiceSchema = Schema(
    {
        "average": int,
        "formula": str
    },
    error="Failed to validate dice roll text"
)

HPSchema = Or(AverageDiceSchema, Schema({"special":str}))

CreatureTypeSchema = Schema(
    {
        "type": [Or('any', enum_str(constants.CREATURE_TYPES))],
        "swarm": bool,
        "swarm_size": Or(enum_str(constants.SIZES), None)
    },
    error="Failed to validate creature type"
)

SizeSchema = [enum_str(constants.SIZES)]

ACSchema = Schema(
    {
        "ac":int,
        "from":[str],
        "condition":str
    },
    error="Failed to validate AC text"
)

SpeedSchema = Schema( 
    {
        "type": enum_str(constants.MOVEMENT_TYPES),
        "distance": int,
        "measure": enum_str(constants.MEASURES)
    },
    error="Failed to validate speed text"
)

SkillSchema = Schema(
    {
        "skill": Or(enum_str(constants.SHORT_SKILLS ), str),
        "mod": int,
        "prof": bool,
        Optional("default"):bool
    },
    error="Failed to validate skill"
)

DamageResistSchema = pre_post_schema(constants.DAMAGE_TYPES)
ConditionResistSchema = pre_post_schema(constants.CONDITIONS)

UsesSchema = Schema(
    {
        "slots": int,
        "period": enum_str(constants.TIME_MEASURES)
    },
    error="Failed to validate uses"
)

SenseSchema = Schema(
    {
        "type":enum_str(constants.SENSES),
        "distance":int,
        "measure": enum_str(constants.MEASURES)
    },
    error="Failed to validate senses"
)

CRSchema = Schema(
    {
        "cr": Or(float, int),
        Optional("lair"): Or(float, int),
        Optional("coven"):  Or(float, int)
    },
    error="Failed to validate Challenge Rating"
)

DurationSchema = Schema(
    {
        "length":int,
        "measure":enum_str(constants.TIME_MEASURES)
    },
    error="Failed to validate effect duration"
)

DamageSchema = Schema(
    {
        "damage": AverageDiceSchema,
        "type": enum_str(constants.DAMAGE_TYPES),
    },
    error="Failed to validate damage text"
)

ConditionSchema = Schema(
    {
        "condition": enum_str(constants.CONDITIONS),
        Optional("duration"): DurationSchema,
    },
    error="Failed to validate contition text"
)

EffectSchema = Schema({
        Optional("damage"): [DamageSchema],
        Optional("rolls"): [{"roll": AverageDiceSchema, Optional("type"):str}],
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
    },
    error="Failed to validate effect text"
)

RangeSchema = Schema(
    {
        "distance": int,
        Optional("long_distance"): int,
        "measure": enum_str(constants.MEASURES)
    },
    error="Failed to validate range text"
)

TargetSchema = Schema(
    {
        "count": Or(int, "all", "any"),
        "type": Or("creature", "target", "object"),
        Optional("post_text"): str
    },
    error="Failed to validate target text"
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
    },
    error="Failed to validate attack"
)

FeatureSchema = Schema(
    {
        "title":str,
        "text":str,
        Optional("attack"): AttackSchema,
        Optional("effects"): [EffectSchema],
        Optional("uses"): UsesSchema
    },
    error="Failed to validate feature"
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
    },
    error="Failed to validate action"
)

SpellSchema = Schema(
    {
        "name": str,
        Optional("level"): int,
        Optional("post_text"): str
    },
    error="Failed to validate spell"
)

SpellLevelSchema = Schema(
    {
        "frequency": enum_str(constants.SPELL_FREQUENCIES),
        "spells": [SpellSchema],
        "level": Or('unlevelled','cantrip','1','2','3','4','5','6','7','8','9'),
        Optional("each"): bool,
        Optional("slots"): int
    },
    error="Failed to validate spell level"
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
    },
    error="Failed to validate spellcasting text"
)

SourceSchema = Schema(
    {
        "title":str,
        Optional("short_title"):str,
        Optional("pages"):[int],
        Optional("authors"):[str]
    },
    error="Failed to validate source"
)

ImageSchema = Schema(
    {
        Or(
            {"source_ref":str},
            {"ref": str},
            {"data": str}
        )
    },
    error="Failed to validate image"
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
        Optional("source"): SourceSchema,

        #Monster Image reference
        Optional("image"): ImageSchema,
        Optional("token"): ImageSchema

    },
    error="Failed to validate creature"
)
