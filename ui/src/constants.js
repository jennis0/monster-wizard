export const SIZES = [
    "tiny", "small", "medium", "large", "huge", "gargantuan"
];

export const TYPES = [
    "aberration", "beast", "celestial", "construct", "dragon", "elemental",
    "fey", "fiend", "giant", "humanoid", "monstrosity", "ooze", "plant", 
    "undead"
]

export const PLURAL_TYPES = [
    "aberrations", "beasts", "celestials", "constructs", "dragons", "elementals",
    "fey", "fiends", "giants", "humanoids", "monstrosities", "oozes", "plants", 
    "undead"
]

export const DAMAGE_TYPES = [
    "acid", "cold", "necrotic", "fire", "thunder", "bludgeoning",
    "slashing", "piercing", "force", "lightning", "psychic",
    "radiant", "poison"
]

export const CONDITIONS = [
    "blinded", "charmed", "deafened", "exhaustion", "frightened", "grappled", 
    "immobilized", "incapacitated", "invisible", "paralyzed","petrified", "poisoned", 
    "prone", "restrained", "stunned",  "surprised", "unconcious"
]

export const SHORT_ABILITIES = [
    "str", "dex", "con", "int", "wis", "cha"
]

export const SENSES = [
    "blindsight", "darkvision", "tremorsense", "truesight"
]

export const SKILLS = {
    skills: [
        "acrobatics", "animal handling", "arcana", "athletics", "deception",
        "history", "insight", "intimidation", "investigation", "medicine",
        "nature", "perception", "performance", "persuasion", "religion",
        "sleight of hand", "stealth", "survival"
    ],
    artisans:[
        "alchemist's supplies", "brewer's supplies", "calligrapher's supplies", "carpenter's tools", 
        "cobbler's tools", "cook's utensils", "glassblower's tools", "jeweler's tools", "leatherworker's tools",
        "mason's tools", "navigator's tools", "painter's supplies", "potter's tools", "smith's tools", "tinker's tools", "thieve's tools", "weaver's tools",
        "woodcarver's tools"],
    gaming:["dice set", "playing card set"],
    vehicles:["land", "water"],
    instruments:["bagpipes", "drum", "dulcimer", "flute", "lute", "lyre", "horn", "pan flute", "shawm", "viol",]
}

export const TIME_MEASURES = [
    "round",
    "turn",
    "seconds",
    "minute",
    "hour",
    "day",
    "week",
    "year",
    "century",
    "encounter",
    "rest",
    "long_rest",
    "short_rest",
    "long_or_short_rest",
]

export const SHORT_SKILLS = [
        "acr",
        "ani",
        "arc",
        "ath",
        "dec",
        "his",
        "ins",
        "itm",
        "inv",
        "med",
        "nat",
        "prc",
        "prf",
        "per",
        "rel",
        "slt",
        "ste",
        "sur"
]

export const SKILL_MAP = {
    acr: "Acrobatics",
    ani: "Animal Handling",
    arc: "Arcana",
    ath: "Athletics",
    dec: "Deception",
    his: "History",
    ins: "Insight",
    itm: "Intimidation",
    inv: "Investigation",
    med: "Medicine",
    nat: "Nature",
    prc: "Perception",
    prf: "Performance",
    per: "Persuasion",
    rel: "Religion",
    slt: "Sleight of Hand",
    ste: "Stealth",
    sur: "Survival"
};

export const SHORT_SKILL_ABILITY_MAP = {
    acr: "dex",
    ani: "wis",
    arc: "int",
    ath: "str",
    dec: "cha",
    his: "int",
    ins: "wis",
    itm: "cha",
    inv: "int",
    med: "wis",
    nat: "int",
    prc: "wis",
    prf: "cha",
    per: "cha",
    rel: "int",
    slt: "dex",
    ste: "dex",
    sur: "wis"
};

export const SKILL_ABILITY_MAP = {
    "acrobatics": "dex",
    "animal handling": "wis",
    "arcana": "int",
    "athletics": "str",
    "deception": "cha",
    "history": "int",
    "insight": "wis",
    "intimidation": "cha",
    "investigation": "int",
    "medicine": "wis",
    "nature": "int",
    "perception": "wis",
    "performance": "cha",
    "persuasion": "cha",
    "religion": "int",
    "sleight of hand": "dex",
    "stealth": "dex",
    "survival": "wis"
}

export const MEASURES = [
    "ft","mi"
]

export const MOVEMENT_TYPES = [
    "walk","burrow","climb","fly","swim"
]

export const CRTABLE = [
    [0,"0","0", 2],
    [0.125,"1/8","25", 2],
    [0.25,"1/4", "50", 2],
    [0.5,"1/2", "100", 2],
    [1,"1", "200",2],
    [2,"2","450",2],
    [3,"3","700",2],
    [4,"4","1,100",2],
    [5,"5","1,800",3],
    [6,"6","2,300",3],
    [7,"7","2,900",3],
    [8,"8","3,900",3],
    [9,"9","5,000",4],
    [10,"10","5,900",4],
    [11,"11","7,200",4],
    [12,"12","8,400",4],
    [13,"13","10,000",5],
    [14,"14","11,500",5],
    [15,"15","13,000",5],
    [16,"16","15,000",5],
    [17,"16","18,000",6],
    [18,"18","20,000",6],
    [19,"19","22,000",6],
    [20,"20","25,000",6],
    [21,"21","33,000",7],
    [22,"22","41,000",7],
    [23,"23","50,000",7],
    [24,"24","62,000",7],
    [25,"25","75,000",8],
    [26,"26","90,000",8],
    [27,"27","105,000",8],
    [28,"28","120,000",8],
    [29,"29","135,000",9],
    [30,"30","155,000",9],
];
