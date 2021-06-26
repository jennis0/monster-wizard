from fifthedition import constants
from re import M
from typing import List

from cv2 import data
from numpy import fix
from fifthedition.creature_2 import Creature2 as Creature

def format_type_alignment(creature: Creature) -> str:
    type_str = ""
    type = creature.data["creature_type"]["type"] if "creature_type" in creature.data else ""
    size = creature.data["size"] if "size" in creature.data else ""
    if creature.data["creature_type"]["swarm"]:
        if size is not None:
            type_str = "Swarm of {size} {type}".format(type)
        else:
            type_str = "Swarm of {type}".format(type)

    else:
        type_str = "{} {}".format(size, type).strip()

    parts = [
        type_str[0].upper() + type_str[1:]
    ]
    if "alignment" in creature.data:
        parts.append(creature.data["alignment"])

    return ", ".join(parts)

def format_name(creature: Creature) -> str:
    return creature.data["name"]

def format_hp(creature: Creature) -> str:
    if "formula" in creature.data["hp"]:
        return "{average} ({formula})".format(**creature.data["hp"])
    else:
        return "{average}".format(**creature.data["hp"])

def format_ac(creature: Creature) -> str:
    ac_strs = []
    for ac in creature.data["ac"]:
        if len(ac["from"]) > 0 and ac["from"][0] != '':
            from_str = ", ".join(ac["from"])
            ac_str = "{} ({}) {}".format(ac["ac"], from_str, ac["condition"])
        else:
            ac_str = "{ac} {condition}".format(**ac)
        ac_strs.append(ac_str)
    return ", ".join(ac_strs)

def format_speed(creature: Creature) -> str:
    walk_speed = ""
    speeds_strs = []
    for s in creature.data["speed"]:
        if s["type"] == "walk":
            walk_speed = "{distance} {measure}.".format(**s)
        else:
            speeds_strs.append("{type} {distance} {measure}.".format(**s))
    speeds_strs = [walk_speed] + speeds_strs
    return ", ".join(speeds_strs)

def format_abilities(creature: Creature) -> str:
    mods = {k: int((creature.data["abilities"][k] - 10) / 2) for k in creature.data["abilities"]}
    abs = creature.data["abilities"]

    # Add positive signs
    for k in mods:
        if mods[k] > 0:
            mods[k] = "+{}".format(mods[k])
        else:
            mods[k] = "{}".format(mods[k])

    abs_str = []
    for k in {"str", "dex", "con", "int", "wis", "cha"}:
        abs_str.append("{:2d} ({:2s})".format(abs[k], mods[k]))
    return  "\t".join(abs_str)

def format_saves(creature: Creature) -> str:
    saves = creature.data["saves"]
    save_str = []
    for k in {"str", "dex", "con", "int", "wis", "cha"}:
        if k not in saves:
            continue
        if saves[k] > 0:
            save = "+{}".format(saves[k])
        else:
            save = "{}".format(saves[k])
        save_str.append("{} {}".format(k.upper(), save))
    return ", ".join(save_str)

def format_senses(creature: Creature) -> str:
    parts = []
    for sense in creature.data["senses"]:
        parts.append("{sense} {distance} {measure}.".format(**sense))

    if "passive" in creature.data:
        parts.append("passive Perception {}".format(creature.data["passive"]))

    return ", ".join(parts)

def format_resistances(creature: Creature, key: str) -> str:
    parts = []
    for res in creature.data[key]:
        parts.append("{} {} {}".format(
            res["pre_text"].strip(), 
            ", ".join(r[0].upper() + r[1:].strip() for r in res["type"]),
            res["post_text"].strip()
            ).strip())
    return "; ".join(parts).strip()

def format_languages(creature: Creature) -> str:
    return ", ".join(creature.data["languages"])

def format_skills(creature: Creature) -> str:
    parts = []
    for s in creature.data["skills"]:
        mod = s["mod"]
        if mod  > 0:
            mod = "+{}".format(mod)
        parts.append("{} {}".format(s["skill"], mod))
    return ", ".join(parts)

def format_cr(width: int, formats: List[str], creature: Creature) -> str:
    cr = creature.data["cr"]["cr"]
    xp = constants.XP_BY_CR[cr]
    cr_str = "{} ({:,} XP)".format(cr, xp)

    if "proficiency" in creature.data:
        prof_str = "{bold}Proficency Bonus{plain} +{prof}".format(**formats, prof=creature.data["proficiency"])

        gap = width - (len(cr_str) + len(prof_str)) - 18
        mid = " " * gap
        print(len(cr_str), len(prof_str), len(mid), width)
        return cr_str + mid + prof_str
    return cr_str
    













def format_header(width: int, formats: List[str], creature: Creature) -> str:
        text = [
"{big_break}\n\
{bold}{name}{plain}\n\
{italics}{type}{plain}\n\
{small_break}".format(**formats, name=format_name(creature), type=format_type_alignment(creature))
        ]

        if "ac" in creature.data:
            text.append("{bold}Armor Class{plain} {ac}".format(**formats, ac=format_ac(creature)))

        if "hp" in creature.data:
            text.append("{bold}Hit Points{plain} {hp}".format(**formats, hp=format_hp(creature)))

        if "speed" in creature.data:
            text.append("{bold}Speed{plain} {speed}".format(**formats, speed=format_speed(creature)))

        text.append("{small_break}".format(**formats))

        return "\n".join(text)


def format_traits(width: int, formats: List[str], creature: Creature) -> str:
    
    trait_str = []
    if "skills" in creature.data:
        trait_str.append("{bold}Skills{plain} {skills}".format(**formats, skills=format_skills(creature)))

    if "saves" in creature.data:
        trait_str.append("{bold}Saving Throws{plain} {saves}".format(**formats, saves=format_saves(creature)))
    #if "skills",
    if "resistances" in creature.data:
        trait_str.append("{bold}Damage Resistances{plain} {res}".format(
            **formats, 
            res=format_resistances(creature, "resistances")
            )
        )
    if "damage_immunities" in creature.data:
        trait_str.append("{bold}Damage Immunities{plain} {res}".format(
            **formats, 
            res=format_resistances(creature, "damage_immunities")
            )
        )
    if "condition_immunities" in creature.data:
        trait_str.append("{bold}Condition Immunities{plain} {res}".format(
            **formats, 
            res=format_resistances(creature, "condition_immunities")
            )
        )
    if "vulnerabilities" in creature.data:
        trait_str.append("{bold}Damage Vulnerabilities{plain} {res}".format(
            **formats, 
            res=format_resistances(creature, "vulnerabilities")
            )
        )
    if "senses" in creature.data:
        trait_str.append("{bold}Senses{plain} {senses}".format(**formats, senses=format_senses(creature)))

    if "languages" in creature.data:
        trait_str.append("{bold}Languages{plain} {lang}".format(**formats, lang=format_languages(creature)))

    if "cr" in creature.data:
        trait_str.append("{bold}Challenge{plain} {cr}".format(**formats, cr=format_cr(width, formats, creature)))

    fixed_width_trait_strs = []
    for t in trait_str:
        while len(t) > width:
            parts = t.split()
            first_line_parts = []
            for i, p in enumerate(parts):
                first_line = " ".join(first_line_parts)
                if len(first_line) + len(p) + 1 > width:
                    fixed_width_trait_strs.append(first_line)
                    first_line_parts = []
                    t = " "*4 + " ".join(parts[i:])
                    break
                first_line_parts.append(p)
        fixed_width_trait_strs.append(t)

    return "\n".join(fixed_width_trait_strs)



################# Main Function ##########################

def pretty_format_creature(creature: Creature) -> str:
    width = 75

    formats = {
        "bold":'\033[1m',
        "italics":'\033[3m',
        "plain":'\033[0m',
        "big_break": "=" * width,
        "small_break": "-" * width,
        "inset": " " * 4
    }

    text = format_header(width, formats, creature) + "\n"

    if "abilities" in creature.data:
        text +=\
"{bold}  STR     DEX     CON     INT     WIS     CHA{plain}\n\
{abilities}\n\
{small_break}\n".format(
        **formats,
        abilities=format_abilities(creature),
    )

    text +=\
"{traits}\n\
{small_break}\n\
{big_break}\n".format(
        **formats,
        traits = format_traits(width, formats, creature)
    )

    return text