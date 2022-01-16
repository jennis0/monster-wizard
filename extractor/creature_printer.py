from numpy import ceil
from extractor.creature_schema import ActionSchema
from extractor import constants
from typing import List, Dict
import ansiwrap

from extractor.creature import Creature

def to_fixed_width(width: int, indent: int, strs: List[str]) -> List[str]:
    indent = " "*indent    
    break_new_lines = []
    for line in strs:
        break_new_lines += line.split("\n")

    new_lines = []
    for line in break_new_lines:
        if line == "":
            new_lines.append("")
            continue
        new_lines += ansiwrap.wrap(line, width=width, initial_indent="", subsequent_indent=indent, 
            break_long_words=False, drop_whitespace=True, break_on_hyphens=False, expand_tabs=True)
        if line[-1] == "\n":
            new_lines.append("")
    return new_lines

def format_type_alignment(creature: Creature) -> str:
    type_str = ""
    type = " or ".join(creature.data["creature_type"]["type"]) if "creature_type" in creature.data else ""
    size = " or ".join(creature.data["size"]) if "size" in creature.data else ""
    if creature.data["creature_type"]["swarm"]:
        s = creature.data["creature_type"]["swarm_size"]
        if s is None:
            s = creature.data["size"]
        if s is not None:
            type_str = "Swarm of {size} {type}".format(size=size, type=type)
        else:
            type_str = "Swarm of {type}".format(type=type)

    else:
        type_str = "{} {}".format(size, type).strip()

    parts = [
        type_str[0].upper() + type_str[1:] if len(type_str) > 0 else type_str
    ]
    if "alignment" in creature.data:
        parts.append(creature.data["alignment"])

    return ", ".join(parts)

def format_name(creature: Creature) -> str:
    return creature.data["name"]

def format_hp(creature: Creature) -> str:
    if "formula" in creature.data["hp"]:
        return "{average} ({formula})".format(**creature.data["hp"])
    elif "average" in creature.data["hp"]:
        return "{average}".format(**creature.data["hp"])
    else:
        return "{special}".format(**creature.data["hp"])

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
    return  "   " + " ".join(abs_str)

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
        return cr_str + mid + prof_str
    return cr_str
    
def format_header(width: int, formats: List[str], creature: Creature) -> str:
        text = ["{bold}{name}{plain}\n\
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

        return "\n".join(to_fixed_width(width, 4, text))


def format_traits(width: int, formats: List[str], creature: Creature) -> str:
    
    trait_strs = []
    if "skills" in creature.data:
        trait_strs.append("{bold}Skills{plain} {skills}".format(**formats, skills=format_skills(creature)))

    if "saves" in creature.data:
        trait_strs.append("{bold}Saving Throws{plain} {saves}".format(**formats, saves=format_saves(creature)))
    #if "skills",
    if "resistances" in creature.data:
        trait_strs.append("{bold}Damage Resistances{plain} {res}".format(
            **formats, 
            res=format_resistances(creature, "resistances")
            )
        )
    if "damage_immunities" in creature.data:
        trait_strs.append("{bold}Damage Immunities{plain} {res}".format(
            **formats, 
            res=format_resistances(creature, "damage_immunities")
            )
        )
    if "condition_immunities" in creature.data:
        trait_strs.append("{bold}Condition Immunities{plain} {res}".format(
            **formats, 
            res=format_resistances(creature, "condition_immunities")
            )
        )
    if "vulnerabilities" in creature.data:
        trait_strs.append("{bold}Damage Vulnerabilities{plain} {res}".format(
            **formats, 
            res=format_resistances(creature, "vulnerabilities")
            )
        )
    if "senses" in creature.data:
        trait_strs.append("{bold}Senses{plain} {senses}".format(**formats, senses=format_senses(creature)))

    if "languages" in creature.data:
        trait_strs.append("{bold}Languages{plain} {lang}".format(**formats, lang=format_languages(creature)))

    if "cr" in creature.data:
        trait_strs.append("{bold}Challenge{plain} {cr}".format(**formats, cr=format_cr(width, formats, creature)))

    trait_strs = to_fixed_width(width, 4, trait_strs)

    return "\n".join(trait_strs)

def format_features(width: int, formats: Dict[str, str], creature: Creature) -> str:
    lines = []

    ### Handle normal features

    if "features" not in creature.data and "spellcasting" not in creature.data:
        return ""

    if "features" in creature.data:
        for feature in creature.data["features"]:
            lines.append("{bold}{title}.{plain} {text}".format(**formats, **feature))
            lines.append("")

    if "spellcasting" not in creature.data:
        return "\n".join(to_fixed_width(width, 0, lines))

    ### Handle Spellcasting features

    spellcast_proper_titles = {
        "cantrip": "Cantrip",
        "will":"At will",
        "daily":"day",
        "rest":"rest",
        "weekly":"week",
        "levelled":"",
        "constant":"Constant",
        '1':"1st level",
        '2':"2nd level",
        '3':"3rd level",
        '4':"4th level",
        '5':"5th level",
        '6':"6th level",
        '7':"7th level",
        '8':"8th level",
        '9':"9th level"
    }

    for s in creature.data["spellcasting"]:
        lines.append("{bold}{title}.{plain} {text}".format(**formats, **s))
        lines.append("")
        for freq in ["will", "constant"]:
            for level in s["levels"]:
                if level["frequency"] == freq:
                    freq_long = spellcast_proper_titles[level["frequency"]]
                    formatted_spells = ", ".join(level["spells"])
                    lines.append("{freq_long}: {italics}{format_spells}{plain}".format(**formats, 
                        freq_long=freq_long, 
                        format_spells=formatted_spells))

        for freq in ["daily","rest","weekly"]:
            for level in s["levels"]:
                if level["frequency"] == freq:
                    freq_long = spellcast_proper_titles[level["frequency"]]
                    if "slots" in level:
                        freq_long = "{}/".format(level["slots"]) + freq_long
                    if "each" in level and level["each"]:
                        freq_long += " each"
                    formatted_spells = ", ".join(level["spells"])
                    lines.append("{freq_long}: {italics}{format_spells}{plain}".format(**formats, 
                        freq_long=freq_long, 
                        format_spells=formatted_spells))

        for level in s["levels"]:
            if level["frequency"] == 'levelled':
                formatted_spells = ", ".join(level["spells"])
                if level["level"] == "cantrip":
                    freq_long = "Cantrips (at will)"
                else:
                    freq_long = "{lev} ({slots} slots{each})".format(
                        lev=spellcast_proper_titles[level["level"]],
                        slots=level["slots"] if "slots" in level else "?",
                        each=" each" if "each" in level and level["each"] else ""
                    )
                lines.append("{freq_long}: {italics}{format_spells}{plain}".format(**formats, 
                    freq_long=freq_long, 
                    format_spells=formatted_spells))
        if "post_text" in s:
            lines.append(s["post_text"] + "\n")
        else:
            lines.append("")

    return "\n".join(to_fixed_width(width, 0, lines))

def _action_group_to_text(formats: Dict[str, str], action_type: str, actions: List[Dict], creature: Creature):

    action_type_names = {
        "action": "Actions",
        "bonus": "Bonus Actions",
        "free": "Free Actions",
        "reaction": "Reactions",
        "legendary": "Legendary Actions",
        "mythic": "Mythic Actions",
        "lair": "Lair Actions",
    }

    lines = []
    lines.append("{bold}{type}{plain}".format(**formats, type=action_type_names[action_type]))

    if action_type == "legendary":
        lines.append(creature.data["legendary_block"] + "\n")
    elif action_type == "lair":
        lines.append(creature.data["lair_block"] + "\n")
    else:
        lines.append("")
    
    for action in actions:
        lines.append(
            "{bold}{title}{plain}. {text}".format(**formats, **action)
        )
        lines.append("")

    lines.append(formats["small_break"])
    return lines

def format_actions(width: int, formats: Dict[str, str], creature: Creature):
    lines = []

    for at in constants.ACTION_TYPES:
        if at.name in creature.data:
            lines += _action_group_to_text(formats, at.name, creature.data[at.name], creature)
        elif at.name in ["legendary", "lair"] and "{}_block".format(at.name) in creature.data:
            lines += _action_group_to_text(formats, at.name, [], creature)

    #Ignore last line as it's an unnecessary break
    return "\n".join(to_fixed_width(width, 0, lines[:-1]))









################# Main Function ##########################

def pretty_format_creature(creature: Creature) -> str:
    width = 55
    columns = True
    separator = 2

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
"{bold}     STR     DEX     CON     INT     WIS     CHA{plain}\n\
{abilities}\n\
{small_break}\n".format(
        **formats,
        abilities=format_abilities(creature),
    )

    text +=\
"{traits}\n\
{small_break}\n".format(
        **formats,
        traits = format_traits(width, formats, creature)
    )

    text +=\
"{features}\n\
{small_break}\n".format(
        **formats,
        features = format_features(width, formats, creature)
    )

    text +=\
"{actions}\n".format(
        **formats,
        actions = format_actions(width, formats, creature)
    )

    lines = text.split("\n")
    if len(lines) > 40 and columns:
        lines_per_col = int(ceil(len(lines) / 2))
        sep = " " * separator
        new_lines = ["="*(2*width+separator)]

        for i in range(lines_per_col):
            j = i + lines_per_col
            l1 = lines[i].rstrip()
            if ansiwrap.ansilen(l1) < width:
                l1 += " "*(width-ansiwrap.ansilen(l1))
            if ansiwrap.ansilen(lines) > j:
                l2 = lines[j].strip()
                if len(l2) < width:
                    l2 += " "*(width-ansiwrap.ansilen(l2))
                new_line = "{l1}{s}{l2}".format(l1=l1, s=sep, l2=l2)
            else:
                new_line = l1 + sep + " "*width
            new_lines.append(new_line)

        new_lines.append(new_lines[0])
        text = "\n".join(new_lines)
    else:
        text = "="*width + "\n" + text + "="*width

    if "background" in creature.data:
        text += "\n"
        bg = creature.data["background"]
        text += "".join(["\n{}\n".format(t) for t in bg])

        if len(lines) > 40 and columns:
            text += "="*width*2 + "\n" 
        else:
            text += "="*width + "\n" 

    return text