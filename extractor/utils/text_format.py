from ..core import creature_schema as cs
from ..core.constants import *

### Common text formatting utilities that will be used across various statblock types

def count_number(n: int):
    if n == 1:
        return "1st"
    elif n == 2:
        return "2nd"
    elif n == 3:
        return "3rd"
    else:
        return f"{n}th"

def upcase(s: str) -> str:
    parts = s.split()
    for i in range(len(parts)):
        if len(parts[i]) > 1:
            parts[i] = parts[i][0].upper() + parts[i][1:]
        else:
            parts[i] = parts[i].upper()
    
    s = " ".join(parts)

    parts = s.split("/")
    for i in range(len(parts)):
        if len(parts[i]) > 1:
            parts[i] = parts[i][0].upper() + parts[i][1:]
        else:
            parts[i] = parts[i].upper()
    
    s = "/".join(parts)

    return s

def spell(s: cs.SpellSchema):
    lvl = ""
    pt = ""
    if "level" in s:
        if s["level"] >= 1:
            lvl = f" ({count_number(s['level'])} level)"
        else:
            lvl = " (Cantrip)"
    if "post_text" in s:
        pt = f" ({s['post_text']})"

    return f"{s['name'].strip()}{lvl}{pt}"

def spellblock(sb: cs.SpellcastingSchema):
    levels = []
    for sl in sb["levels"]:
        if sl['frequency'] == SPELL_FREQUENCIES.will.name:
            freq = 'At will'
        elif sl['frequency'] == SPELL_FREQUENCIES.daily.name:                
            freq = f"{sl['slots']}/day" if "slots" in sl else "1/day"
        elif sl['frequency'] == SPELL_FREQUENCIES.rest.name:                
            freq = f"{sl['slots']}/long or short rest" if "slots" in sl else "1/long or short rest"
        elif sl['frequency'] == SPELL_FREQUENCIES.levelled.name and not sl["level"] == "cantrip":
            l = count_number(sl['level'])
            freq = f'{l} level ({sl["slots"] if "slots" in sl else 1} slots)'
        elif sl['frequency'] == SPELL_FREQUENCIES.cantrip.name or sl["level"] == "cantrip":
            freq = 'Cantrip (at will)'
        
        if "each" in sl and sl["each"]:
            freq += " each"

        levels.append(f'<b>{freq}:</b> {",".join([spell(s) for s in sl["spells"]])}')

    text = sb["text"] + "</br>" + "</br>".join(levels)
    if "post_text" in sb:
        text += f"</br>{sb['post_text']}"

    return text
