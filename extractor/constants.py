from enum import Enum, auto
import re
from typing import Any, List

def is_in_enum(candidate: str, enum: Enum) -> bool:
    '''Helper function to check membership of string in enum'''
    return candidate in enum.__members__

def enum_values(enum: Enum) -> List[str]:
    '''Helper function to return list of names'''
    return list([k.replace("_"," ") for k in enum.__members__.keys()])
        

class SIZES(Enum):
    tiny = auto()
    small = auto()
    medium = auto()
    large = auto()
    huge = auto()
    gargantuan = auto()

class DAMAGE_TYPES(Enum):
    acid = auto()
    cold = auto()
    necrotic = auto()
    fire = auto()
    thunder = auto()
    bludgeoning = auto()
    slashing = auto()
    piercing = auto()
    force = auto()
    lightning = auto()
    psychic = auto()
    radiant = auto()
    poison = auto()

class CONDITIONS(Enum):
    stunned = auto()
    paralyzed = auto()
    blinded = auto()
    grappled = auto()
    restrained = auto()
    immobilized = auto()
    petrified = auto()
    prone = auto()
    charmed = auto()
    deafened = auto()
    exhausted = auto()
    incapacitated = auto()
    invisible = auto()
    surprised = auto()
    unconscious = auto()
    exhaustion = auto()
    frightened = auto()
    poisoned = auto()

class CREATURE_TYPES(Enum):
    aberration = auto()
    beast = auto()
    celestial = auto()
    construct = auto()
    dragon = auto()
    elemental = auto()
    fey = auto()
    fiend = auto()
    giant = auto()
    humanoid = auto()
    monstrosity = auto()
    ooze = auto()
    plant = auto()
    undead = auto()
    swarm = auto()

class CREATURE_TYPE_PLURALS(Enum):
    aberrations = auto()
    beasts = auto()
    celestials = auto()
    constructs = auto()
    dragons = auto()
    elementals = auto()
    fey = auto()
    fiends = auto()
    giants = auto()
    humanoids = auto()
    monstrosities = auto()
    oozes = auto()
    plants = auto()
    undead = auto()

    def to_singular(self) -> CREATURE_TYPES:
        if self == CREATURE_TYPE_PLURALS.monstrosities:
            return CREATURE_TYPES.monstrosity
        elif self == CREATURE_TYPE_PLURALS.fey:
            return CREATURE_TYPES.fey
        elif self == CREATURE_TYPE_PLURALS.undead:
            return CREATURE_TYPES.undead
        
        return CREATURE_TYPES[self.name[:-1]]

class ABILITIES(Enum):
    strength = auto()
    dexterity = auto()
    constitution = auto()
    intelligence = auto()
    wisdom = auto()
    charisma = auto()

class SHORT_ABILITIES(Enum):
    str = auto()
    dex = auto()
    con = auto()
    int = auto()
    wis = auto()
    cha = auto()

class MOVEMENT_TYPES(Enum):
    walk = auto()
    burrow = auto()
    climb = auto()
    fly = auto()
    swim = auto()

class SENSES(Enum):
    blindsight = auto()
    darkvision = auto()
    tremorsense = auto()
    truesight = auto()

class SKILLS(Enum):
    acrobatics = auto()
    animal_handling = auto()
    arcana = auto()
    athletics = auto()
    deception = auto()
    history = auto()
    insight = auto()
    intimidation = auto()
    investigation = auto()
    medicine = auto()
    nature = auto()
    perception = auto()
    performance = auto()
    persuasion = auto()
    religion = auto()
    sleight_of_hand = auto()
    stealth = auto()
    survival = auto()

class SHORT_SKILLS(Enum):
    acr = auto()
    ani = auto()
    arc = auto()
    ath = auto()
    dec = auto()
    his = auto()
    ins = auto()
    itm = auto()
    inv = auto()
    med = auto()
    nat = auto()
    prc = auto()
    prf = auto()
    per = auto()
    rel = auto()
    slt = auto()
    ste = auto()
    sur = auto()

SHORTSKILLSMAP = {
        SKILLS.acrobatics.name: "acr",
        SKILLS.animal_handling.name: "ani",
        "animal handling": "ani",
        SKILLS.arcana.name: "arc",
        SKILLS.athletics.name: "ath",
        SKILLS.deception.name: "dec",
        SKILLS.history.name: "his",
        SKILLS.insight.name: "ins",
        SKILLS.intimidation.name: "itm",
        SKILLS.investigation.name: "inv",
        SKILLS.medicine.name: "med",
        SKILLS.nature.name: "nat",
        SKILLS.perception.name: "prc",
        SKILLS.performance.name: "prf",
        SKILLS.persuasion.name: "per",
        SKILLS.religion.name: "rel",
        SKILLS.sleight_of_hand.name: "slt",
        "sleight of hand": "slt",
        SKILLS.stealth.name: "ste",
        SKILLS.survival.name: "sur"
}

class MEASURES(Enum):
    ft = auto()
    mi = auto()

    @staticmethod
    def normalise(text: str) -> str:
        '''Replace any expanded instances of the measures by the shortened ones'''
        text = re.sub("[\s\.,:;]feet[\s\.,:;]","ft", text)
        return re.sub("[\s\.,:;]miles[\s\.,:;]","mi", text)

class TIME_MEASURES(Enum):
    round = auto()
    turn = auto()
    seconds = auto()
    minute = auto()
    hour = auto()
    day = auto()
    week = auto()
    year = auto()
    century = auto()
    encounter = auto()
    rest = auto()
    long_rest = auto()
    short_rest = auto()
    long_or_short_rest = auto()

class SPELL_FREQUENCIES(Enum):
    will = auto()
    encounter = auto()
    daily = auto()
    rest = auto()
    weekly = auto()
    cantrip = auto()
    levelled = auto()

class ACTION_TYPES(Enum):
    action = auto()
    bonus = auto()
    reaction = auto()
    free = auto()
    legendary = auto()
    mythic = auto()
    lair = auto()

class ALIGNMENTS(Enum):
    lawful = auto()
    chaotic = auto()
    good = auto()
    evil = auto()
    neutral = auto()
    unaligned = auto()


XP_BY_CR = {
    "0":	0,
    "1/8":	25,
    "1/4":	50,
    "1/2":	100,
    "1":	200,
    "2":	450,
    "3":	700,
    "4":	1100,
    "5":	1800,
    "6":	2300,
    "7":	2900,
    "8":	3900,
    "9":	5000,
    "10":	5900,
    "11":	7200,
    "12":	8400,
    "13":	10000,
    "14":	11500,
    "15":	13000,
    "16":	15000,
    "17":	18000,
    "18":	20000,
    "19":	22000,
    "20":	25000,
    "21":	33000,
    "22":	41000,
    "23":	50000,
    "24":	62000,
    "25":	75000,
    "26":	90000,
    "27":	105000,
    "28":	120000,
    "29":	135000,
    "30":	155000,
}
