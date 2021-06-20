import re
import numpy as np
import fifthedition.constants as constants

class LineAnnotator(object):

    def __init__(self):
        self.standard_height=20

    def prepass(self, cols):
        heights = []
        for c in cols:
            heights += [l[1]["height"] for l in c[0]]
        counts,edges = np.histogram(heights)
        self.standard_height = edges[np.argmax(counts)+1] * 1.1

    def annotate(self, lines):
        race_type_str = "^({})\s*({})?,?\s*({})?".format("|".join(constants.SIZES), "|".join(constants.CREATURE_TYPES), "|".join(constants.ALIGNMENTS))
        race_type_re = re.compile(race_type_str, re.IGNORECASE)

        dice_roll_re = re.compile("\d+d\d+")

        line_annotations = []
        for i,line in enumerate(lines):
            annotations = []
            # if line[1]["height"] > self.standard_height:
            #     annotations.append("large")

            race_type_match = race_type_re.findall(line[0].strip().lower())
            if len(race_type_match) > 0 and race_type_match[0] != "":
                if race_type_match[0][0][0] == race_type_match[0][0][0].upper() or race_type_match[0][1] != '' or race_type_match[0][2] != '':
                    annotations.append("race_type_header")
                    j = i - 1
                    while j >= 0:
                        if lines[j][1]["top"] + lines[j][1]["height"] <= lines[i][1]["top"] + 10:
                            lines[j][2].append("statblock_title")
                            break
                        j -= 1

            dice_rolls = dice_roll_re.findall(line[0])
            if len(dice_rolls) > 0:
                annotations.append("dice_roll")

            signatures = [
                ("Challenge \d+", "cr"),
                ("Senses\s[\w\s]+\d+\s*ft", "senses"),
                ("Damage\sImmunities", "dam_immunities"),
                ("Damage\sResistances", "resistances"),
                ("Damage\sVulnerabilities", "vulnerabilities"),
                ("Condition\sImmunities", "con_immunities"),
                ("^Armor Class\s\d+", "ac"),
                ("^Hit Points\s\d+", "hp"),
                ("^Speed\s\d+\s*ft", "speed"),
                ("^Melee\sWeapon\sAttack:", "melee_attack"),
                ("^Ranged\sWeapon\sAttack:", "ranged_attack"),
                ("DC\s\d+\s", "check"),
                ("\d+/(day|minute|hour)", "counter"),
                ("^skills\s.*[+-]\d", "skills"),
                ("^Legendary Action", "legendary_action_title"),
                ("^Actions", "action_title"),
                ("Costs \d+ actions", "legendary_action_cost"),
                ("Recharge \d+-\d+", "recharge"),
                ("^STR\s+DEX\s+CON\s+INT\s+WIS\s+CHA", "array_title"),
                ("^(\d+\s\([+-]?\d+\)\s+)+", "array_values"),
                ("Language", "languages"),
                ("^Saving Throws\s+", "saves"),
                ("^Senses\s+", "senses"),
                ("Proficiency Bonus", "proficiency"),
                ("Hit Dice", "hitdice"),
            ]

            for r,tag in signatures:
                m = re.findall(r, line[0].strip(), re.IGNORECASE)
                if len(m) > 0:
                    annotations.append(tag)

            if "." in line[0] and line[0][0] == line[0][0].upper() and len(line[0].split('.')[0].split()) < 5:
                annotations.append("block_title")

            line.append(annotations)
        return lines



class ClusterAnnotator(object):

    heading_fields = [
        "statblock_title",
        "race_type_header"
    ]

    stats_fields = [
        "array_title",
        "array_values"
    ]

    defence_fields = [
        "hp",
        "ac",
        "speed"
    ]

    flavour_fields = [
        "languages",
        "saves",
        "skills",
        "challenge",
    ]

    action_fields = [
        "action_title",
        "melee_attack",
        "ranged_attack",
    ]

    legendary_action_fields = [
        "legendary_action_title",
        "legendary_action_cost",
    ]

    strong_generic_fields = [
        "dice_roll",
        "check",
        "recharge",
        "counter",
    ]

    weak_generic_fields = [
        "block_title"
    ]

    def annotate(self, clusters):
        _fields = [
            "statblock_title",

        ]

        for c in clusters:
            line_annotations = []
            for line in c[0]:
                line_annotations += line[2]

            cluster_annotations = []
            if "statblock_title" in line_annotations:
                cluster_annotations.append("sb_start")

            for df in ClusterAnnotator.defence_fields:
                if df in line_annotations:
                    cluster_annotations.append("sb_defence_block")
                    break

            for sf in ClusterAnnotator.stats_fields:
                if sf in line_annotations:
                    cluster_annotations.append("sb_array_block")
                    break

            for df in ClusterAnnotator.flavour_fields:
                if df in line_annotations:
                    cluster_annotations.append("sb_flavour_block")
                    break

            for af in ClusterAnnotator.action_fields:
                if af in line_annotations:
                    cluster_annotations.append("sb_action_block")
                    break

            for lf in ClusterAnnotator.legendary_action_fields:
                if lf in line_annotations:
                    cluster_annotations.append("sb_legendary_action_block")
                    break

            for gf in ClusterAnnotator.strong_generic_fields:
                if gf in line_annotations:
                    cluster_annotations.append("sb_part")

            num_generic = 0
            for gf in ClusterAnnotator.weak_generic_fields:
                if gf in line_annotations:
                    num_generic += 1
            if num_generic > 0.1 * len(c[0]):
                cluster_annotations.append("sb_part_weak")
            
            cluster_annotations.append(("lines", line_annotations))
            c.append(cluster_annotations)