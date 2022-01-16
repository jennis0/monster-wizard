from typing import Any, List
import json
import sys

def added(s, indent):
    return "<font class='add'>" + "&nbsp"*indent + "+ {}</font>".format(s)

def remove(s, indent):
    return "<font class='remove'>" + "&nbsp"*indent + "+ {}</font>".format(s)

def change(s, indent):
    return "<font class='change'>" + "&nbsp"*indent + "+ {}</font>".format(s)

def header():
    return """
    <head>
    <Title>Diff Report</Title>
    <style>
        font.add {color: green}
        font.remove {color: red}
        font.change {color: orange}
    </style>
    </head>
    """

def diff_mw_file(f_old: Any, f_new: Any, indent: int=4) -> str:
    titles_old = {e['title']:e for e in f_old}
    titles_new= {e['title']:e for e in f_new}
    
    lines = ["<p>Source Changes:"]

    ### Full sources that have been added or removed
    for t in titles_new:
        if t not in titles_old:
            lines.append(added(f"Source: {t}", 0))
            if "creatures" in titles_new[t]:
                for c in titles_new[t]["creatures"]:
                    lines.append(added(f"Creature: {c['name']}", indent))

    lines.append("</p><p>Creature Changes:")

    for t in titles_old:
        if t not in titles_new:
            lines.append(remove(f"Source: {t}", 0))
            if "creatures" in titles_old[t]:
                for c in titles_old[t]["creatures"]:
                    lines.append(remove(f"Creature: {c['name']}", indent))

    for t in titles_new:
        if t not in titles_old:
            continue

        tn = titles_new[t]
        to = titles_old[t]

        cns = {c['name']: c for c in tn['creatures']}
        cos = {c['name']: c for c in to['creatures']}

        lines.append(f"Source {t}")

        for c in cns:
            if c not in cos:
                lines.append(added(f"Creature: {c} added to source: {t}", indent+1))
            else:
                lines += diff_creature(cos[c], cns[c], indent+1)

        for c in cos:
            if c not in cns:
                lines.append(remove(f"Creature: {c} removed from source: {t}", indent+1))
            
    lines.append("</p>")

    return """
    <!Doctype Html>  
    <html>
    {}
    <body>
    {}
    </body>
    </html>
    """.format(header(), "</br>".join(lines))

def diff_optional_feature(feature: str, c_old: Any, c_new: Any, indent: int) -> List[str]:
    diffs = []
    norm_feature = feature.lower().replace(" ","_")
    if norm_feature in c_old: 
        if norm_feature not in c_new:
            diffs.append(remove(f'Removed {feature}: {c_old[norm_feature]} -> None', indent))
        elif c_old[norm_feature] != c_new[norm_feature]:                
            diffs.append(change(f"Changed {feature}: {c_old[norm_feature]} -> {c_new[norm_feature]}", indent))

    elif norm_feature in c_new:
        diffs.append(added(f'Added {feature}: None -> {c_new[norm_feature]}', indent))

    return diffs

def diff_list(key, c_old: Any, c_new: Any, indent: int, human_key) -> List[str]:
    f_o = {f['title']:f for f in c_old[key]} if key in c_old else {}
    f_n = {f['title']:f for f in c_new[key]} if key in c_new else {}

    diffs = []
    for k in f_o:
        if k not in f_n:
            diffs.append(remove(f"Removed {human_key} \"{k}\": {f_o[k]} -> None", indent))
        elif f_n[k] != f_o[k]:
            diffs.append(change(f"Changed {human_key} \"{k}\": {f_o[k]} -> {f_n[k]}", indent))

    for k in f_n:
        if k not in f_o:
            diffs.append(added(f"Added {human_key} \"{k}\": None -> {f_n[k]}", indent))

    return diffs

def add_or_change_diff(d_old: Any, d_new: Any, key: str, name: str, indent: int) -> List[str]:
    if key in d_old and key not in d_new:
        return [remove(f'Removed {name}: {d_old[key]} -> None', indent)]
    elif key in d_new and key not in d_old:
        return [added(f'Added {name}: None -> {d_new[key]}', indent)]
    elif key in d_new and key in d_old and d_new[key] != d_old[key]:
        return [change(f"Changed {name}: {d_old[key]} -> {d_new[key]}", indent)]
    return []
    
def diff_spells(s_old: Any, s_new: Any, indent: int) -> List[str]:
    so = {f['level']:f for f in s_old if 'level' in f}
    sn = {f['level']:f for f in s_new if 'level' in f}

    diffs = []
    for l in so:
        if l not in sn:
            diffs.append(remove(f'Spell level {l}: {so[l]} -> None'))
        if so[l] != sn[l]:
            add_or_change_diff(so, sn, 'frequency', f'level {l} spell frequency', indent)
            add_or_change_diff(so, sn, 'spells', f'level {l} spells', indent)
            add_or_change_diff(so, sn, 'slots', f'level {l} slots', indent)
            add_or_change_diff(so, sn, 'each', 'level {l} each setting', indent)
    
    for l in sn:
        if l not in so:
            diffs.append(added(f'Spell level {l}: None -> {sn[l]}', indent))

    return diffs

def diff_spellcasting(c_old: Any, c_new: Any, indent: int) -> List[str]:
    key = 'spellcasting'
    f_o = {f['title']:f for f in c_old[key]} if key in c_old else {}
    f_n = {f['title']:f for f in c_new[key]} if key in c_new else {}

    diffs = []
    for k in f_o:
        if k not in f_n:
            diffs.append(remove(f"Removed \"{k}\": {f_o[k]} -> None", indent))
        elif f_n[k] != f_o[k]:
            so = f_o[k]
            sn = f_n[k]

            diffs += add_or_change_diff(so, sn, 'mod', f'{k} modifier', indent)
            diffs += add_or_change_diff(so, sn, 'text', f'{k} text', indent)
            diffs += add_or_change_diff(so, sn, 'save', f'{k} save', indent)
            diffs += add_or_change_diff(so, sn, 'post_text', f'{k} post text', indent)
            diffs += diff_spells(so['levels'], sn['levels'], indent)

    for k in f_n:
        if k not in f_o:
            diffs.append(added(f"Added \"{k}\": None -> {f_n[k]}", indent))

    return diffs

def diff_creature(c_old: Any, c_new: Any, indent: int) -> List[str]:
    diff_lines = ["&nbsp"*indent + f"<p>Changes to creature {c_old['name']}"]

    for atr in ['Name', 'Size', 'Creature Type', 'Alignment', 'AC', 'HP', 'Speed', "Abilities",
                'Saves', 'Skills', 'Senses', 'Passive', 'Resistances', 
                'Damange Immunities', 'Condition Immunities', 'Vulnerabilities', 
                'Languages', 'CR', 'Proficiency']:
        diff_lines += diff_optional_feature(atr, c_old, c_new, indent)

    for atr,atr_name in zip(['features', 'action', 'legendary', 'mythic', 'reaction', 'lair'],
         ['feature', 'action', 'legendary action', 'mythic action', 'reaction', 'lair action']):
        diff_lines += diff_list(atr, c_old, c_new, indent, atr_name)

    diff_lines += diff_spellcasting(c_old, c_new, indent)

    diff_lines[-1] += "</p>"

    if len(diff_lines) == 1:
        return ["&nbsp"*indent + f"{c_old['name']}: No changes"]

    return diff_lines

if __name__ == "__main__":

    if len(sys.argv) >= 3:
        old = sys.argv[1]
        new = sys.argv[2]
    else:
        old = "statblocks\statblocks.mw"
        new = "statblocks\statblocks_new.mw"
    if len(sys.argv) == 4:
        out = sys.argv[3]
    else:
        out = "diff.html"

    with open(old, 'r') as f_old:
        with open(new, 'r') as f_new:
            result = diff_mw_file(json.load(f_old), json.load(f_new))
    
    with open(out, 'w') as f:
        f.write(result)

