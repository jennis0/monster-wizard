
import re
import constants
import json

class Creature(object):

    average_and_dice_match = "([0-9]+)\s*\+?\s*(?:\(?([0-9]+d[0-9]+)\s*(\+\s*[0-9]*)?\)?)?"

    def set_size(self, s):
        self.size = s.strip().upper()[0]

    def set_name(self, n):
        ws = [w.lower() for w in n.split()]
        ws = [w[0].upper() + w[1:] if w not in ["in", "of", "the", "and", "a", "an"] or i == 0 else w for i,w in enumerate(ws) ]
        self.name = " ".join(ws)

    def set_size_type_alignment(self, line):
        words = [w.lower() for w in line.split()]
        self.set_size(words[0])
        self.set_type(words[1])
        if "," in line:
            self.set_alignment(line.split(",")[1])
        else:
            self.set_alignment(" ".join(words[2:]))

    def set_type(self, t):
        t = re.sub('[^\w\s\d]','', t)
        if t not in constants.CREATURE_TYPES:
            print("ERROR parsing creature type {}".format(t))
            return None
        self.type = t
        return self.type

    def set_source(self, s):
        self.source = s

    def set_alignment(self, alignment_string):
        align = []
        lc = ge = ""
        parts = [p.strip() for p in alignment_string.upper().split()]
        if len(parts) == 0:
            align=['U']
        elif parts[0] == "ANY":
            if len(parts) == 1:
                align = ['A']
            elif parts[1] == "CHAOTIC" or parts[1] == 'LAWFUL' :
                align = [parts[1][0], 'G', 'NY', 'E']
            elif parts[1] == 'GOOD' or parts[1] == 'EVIL':
                align = ['L', 'NX', 'C', parts[1][0]]
            elif parts[1] == 'NEUTRAL':
                align = ['NX', 'NY', 'N']
            elif parts[1].startswith('NON'):
                if parts[1] == "NON-CHAOTIC":
                    align = ['NX', 'L', 'G', 'NY', 'E']
                elif parts[1] == 'NON-LAWFUL' :
                    align = ['C', 'NX', 'G', 'NY', 'E']
                elif parts[1] == 'NON-GOOD':
                    align = ['L', 'NX', 'C', 'NY', 'E']
                elif parts[1] == 'NON-EVIL':
                    align =  ["L", "NX","C", "NY", "G"]
            else:
                align = ['A']
        elif parts[0] == 'UNALIGNED':
            align = ['U']
        else:
            if len(parts) == 1:
                align = [parts[0][0]]

            else:
                align = [parts[0][0], parts[1][0]]

        if len(align) == 0:
            print("ERROR parsing alignment string {}".format(alignment_string))
            return None

        self.align = align
        return self.align

    def set_ac(self, ac_string):
        match = re.compile("([0-9]+)\s*(?:\(([\w\s+,]+)?\)?)?\s*([\w\s]+)?")

        acs = match.findall(ac_string)

        if len(acs) == 0:
            print("ERROR: Failed to parse AC string {}".format(ac_string))
            return None

        self.ac = []
        for ac in acs:
            if len(ac[1]) > 0 or len(ac[2]) > 0:
                self.ac.append({
                    "ac":int(ac[0]),
                })
                if len(ac[1]) > 0:
                    self.ac[-1]["from"] = [s.strip() for s in ac[1].split(",")]
                if len(ac[2]) > 0:
                    self.ac[-1]["condition"] = ac[2].strip()
            else:
                self.ac.append(int(ac[0]))

        return self.ac
        
    def set_hp(self, hp_string):
        avg_and_or_dice_match = "([0-9]+)\s*\+?\s*(?:\(?([0-9]+d[0-9]+)\s*(\+\s*[0-9]*)?\)?)?"
        match = re.compile("Hit\sPoints\s+" + Creature.average_and_dice_match)
        m = match.match(hp_string)
        groups = m.groups()
        self.hp = {}

        if groups[0] == None:
            print("ERROR parsing HP string = {}".format(hp_string))
            return None
        
        self.hp["average"] = int(groups[0])
        if groups[1] != None:
            formula = groups[1]
            if groups[2] != None:
                formula += "".join(groups[2].split())
            self.hp = {
                "formula": formula,
                "average": int(groups[0])
            }
        else:
            self.hp = {
                "special": int(groups[0])
            }

        return self.hp

    def set_speed(self, speed_string):
        walk_match = re.compile('(\w*)?\s([0-9]+)\s*ft\.?')
        m = walk_match.findall(speed_string)
        self.speed = {}
        for value in m:
            if value[0].lower().strip() == "speed":
                self.speed["walk"] = int(value[1])
            else:
                self.speed[value[0]] = int(value[1])
        return self.speed

    def set_attributes(self, attr_string):

        parts = attr_string.split()
        abs = ["str", "dex", "con", "int", "wis", "cha"]
        if len(parts) != 12:

            tokens = re.findall('([^\(][0-9]+)?\s*(\([+-][0-9]+\))?', attr_string)
            if len(tokens) < 6:
                print("ERROR parsing attribute string {}".format(attr_string))
                return None
            for t,a in zip(tokens, abs):
                if t[0] != '':
                    self.attributes[a] = t[0]
                else:
                    if t[1] == '':
                        print("ERROR parsing attribute string {}".format(attr_string))
                        return None
                    guess = str(10 + (int(t[1][1:-1]) * 2)) #Index to remove starting/ending brackets
                    self.attributes[a] = guess
                    print("WARNING: Missing proper value for attribute {}. Guessing {} based on modifier {}".format(a, guess, t[1]))

        else:
            for i,a in enumerate(abs):
                self.attributes[a] = parts[2*i]

        return self.attributes

    def set_saves(self, save_string):
        parsed_saves = {}
        match = re.compile("(?:[\s,.]|^)([a-z]{3})\s*([+-])?\s*([0-9]+)", re.IGNORECASE)
        found_saves = match.findall(save_string)
        if len(found_saves) == 0:
            print("ERROR. Failed to find saves in {}".format(save_string))
            return None
        for s in found_saves:
            if s[1] == '':
                parsed_saves[s[0].strip()] = "+" + s[2].strip()
            else:
                parsed_saves[s[0].strip()] = s[1].strip() + s[2].strip()

        self.saves = parsed_saves        

    def set_skills(self, skill_string):
        skill_string = skill_string[7:]
        parsed_skills = {}
        match = re.compile("([\sa-z']+)\s*([+-]\s*[0-9]+)", re.IGNORECASE)
        found_skills = match.findall(skill_string)
        if len(found_skills) == 0:
            print("ERROR. Failed to find saves in {}".format(skill_string))
            return None
        for s in found_skills:
            parsed_skills[s[0].strip()] = s[1].replace(" ",'')

        self.skills = parsed_skills

    def _parse_enum_with_pre_post(self, title, text, enum):
        results = []
        match = re.compile("([\w\s'()]+\w)?(?:^|\s+)({})(?:\s*)([^,]+)?,?".format("|".join(enum)),re.IGNORECASE)
        #if ';' in text:
        texts = text.split(";")
        for t in texts:
            matches = match.findall(t)
            if len(matches) == 1:
                if matches[0][0] == '' and matches[0][2] == '':
                    results.append(matches[0][1].strip())
                else:
                    results.append({
                        title:matches[0][1]
                    })
                    if matches[0][0] != '':
                        results[-1]['preNote'] = matches[0][0].strip()
                    if matches[0][2] != '':
                        results[-1]['note'] = matches[0][2].strip()
            elif len(matches) > 1:
                fields = {title: [m[1] for m in matches]}
                if matches[0][0] != '':
                    fields["preNote"] = matches[0][0].strip()
                if matches[-1][2] !=  '':
                    fields["note"] = matches[-1][2].strip()
                results.append(fields)
            elif len(matches) == 0:
                results.append({
                    title:[],
                    "note":t
                })
        # else:
        #     for r in match.findall(text):
        #         if r[0] == '' and r[2] == '':
        #             results.append(r[1].strip())
        #         else:
        #             results.append({title:r[1].strip()})
        #             if r[0] != '':
        #                 results[-1]['preNote'] = r[0].strip()
        #             if r[2] != '':
        #                 results[-1]['note'] = r[2].strip()
        return results

    def set_immunities(self, imm_string):
        imm_string = " ".join(imm_string.split()[2:])
        self.damage_immunities = self._parse_enum_with_pre_post("immune", imm_string, constants.DAMAGE_TYPES)
        return self.damage_immunities

    def set_condition_immunities(self, imm_string):
        imm_string = " ".join(imm_string.split()[2:])
        self.condition_immunities = self._parse_enum_with_pre_post("conditionImmune", imm_string, constants.CONDITIONS)
        return self.condition_immunities

    def set_resistances(self, res_string):
        res_string = " ".join(res_string.split()[2:])
        self.resistances = self._parse_enum_with_pre_post("resist", res_string, constants.DAMAGE_TYPES)
        return self.resistances

    def set_vulnerabilities(self, vuln_string):
        vuln_string = " ".join(vuln_string.split()[2:])
        self.vulnerabilities = self._parse_enum_with_pre_post("vulnerable", vuln_string, constants.DAMAGE_TYPES)
        return self.vulnerabilities

    def set_senses(self, sense_string):
        #Remove initial 'Senses '
        sense_string = sense_string[6:].strip()
        senses = [s.strip() for s in sense_string.split(",")]
        parsed_senses = []
        tags = []
        for s in senses:
            s_lower = s.lower()
            if "passive" in s_lower:
                self.passive_perception = int(s.split()[-1])
            else:
                parsed_senses.append(s)
                if "dark" in s_lower:
                    tags.append("D")
                elif "blind" in s_lower:
                    tags.append('B')
                elif "tremor" in s_lower:
                    tags.append('T')
                elif "true" in s_lower:
                    tags.append("U")

        self.senses = parsed_senses
        self.senseTags = tags
        return self.senses

    def set_languages(self, lang_string):
        self.languages = [l.strip() for l in " ".join(lang_string.split()[1:]).split(",")]
        return self.languages

    def set_cr(self, cr_string):
        match = re.compile("^Challenge\s+([0-9]+/?[0-9]*)\s+\(.*?XP\s*\)")
        crs = match.findall(cr_string)
        if len(crs) == 1:
            self.cr = crs[0]
        else:
            cr = {"cr":crs[0]}
            if "lair" in cr_string:
                cr["lair"] = crs[1]
            elif "coven" in cr_string:
                cr["coven"] = crs[1]
            else:
                print("ERROR failed to parse CR {}".format(cr_string))
                return None

            self.cr = cr
        
        return self.cr

    def add_feature(self, title, text):
        if "spellcasting" in title.lower():
            self.spellcasting.append(self._parse_spellcasting_block(title, text))
            return self.spellcasting[-1]
        else:
            text = " ".join(text)
            text = self._replace_damage(text)
            text = self._replace_dcs(text)
            text = self._replace_rolls(text)
            trait = {
                "name":title,
                "entries":[text]
            }
            self.traits.append(trait)
            return self.traits[-1]


    def _parse_spellcasting_block(self, title, text):

        starts = [["^(constant):","constant"], 
                  ["^(at will):","will"], 
                  ["^([0-9]*)/(day|rest|week)\s+(each)?","x"],
                  ["^cantrips\s*(?:\(at will\))?:", "s0"],
                  ["^([0-9])(?:st|nd|rd|th)\s*level \(([0-9]+)\s*slots\s*\)", "sx"]
        ]

        header_types = {
            "day":"daily",
            "rest":"rest",
            "week":"weekly",
        }

        for s in starts:
            s[0] = re.compile(s[0], re.IGNORECASE)

        spellblocks = [['h', [], [text[0]]]]
        for line in text[1:]:
            used = False
            for s in starts:
                found = s[0].findall(line)
                if len(found) == 1:
                    spellblocks.append([s[1], found[0], [line]])
                    used=True
                    break
            if not used:
                spellblocks[-1][2].append(line)

        results = {"name":title}
        ability_re = re.compile("spellcasting ability is ({})".format("|".join(constants.ABILITIES)), re.IGNORECASE)

        last_line = " ".join(spellblocks[-1][2])
        split = -1
        for i,l in enumerate(last_line.split(",")):
            if len(l) > 5:
                split = i
                break
        if split > 0:
            spellblocks.append(['f', [], spellblocks[-1][2][i:]])
            spellblocks[-2][2] = spellblocks[-2][2][:i]

        for sb in spellblocks:
            #proces headers
            if sb[0] == 'h':
                line = " ".join(sb[2])
                abilities = ability_re.findall(line)
                if len(abilities) == 0:
                    print("WARNING: No spellcasting ability found")
                elif len(abilities) > 1:
                    print("ERROR: Conflicting spellcasting abilities")
                else:
                    results["ability"] = abilities[0].strip()[:3].lower()
                
                line = self._replace_dcs(line)
                line = self._replace_hit(line)
                results["headerEntries"] = [line]

            elif sb[0] == 'f':
                results["footerEntries"] = " ".join(sb[2])

            elif sb[0] == 'constant' or sb[0] == "will":
                spells_names = " ".join(sb[2]).split(":")[1].split(",")
                results[sb[1].lower()] = [
                    "{{@spell {}}}".format(s.lower().strip()) for s in spells_names
                ]
            else:
                spells_names = " ".join(sb[2]).split(":")[1].split(",")
                spell_list = ["{{@spell {}}}".format(s.lower().strip()) for s in spells_names]
                num = sb[1][0] if sb[1][0] != '' else '1'
                if sb[0] == 'x':
                    freq = header_types[sb[1][1].lower()]
                    each = 'e' if sb[1][2] != '' else '' 
                    if freq not in results:
                        results[freq] = {}
                    results[freq][num + each] = spell_list
                else:
                    if "spells" not in results:
                        results["spells"] = {}
                    if sb[0] == 's0':
                        results["spells"]['0'] = {"spells": spell_list}
                    elif sb[0] == 'sx':
                        level = sb[1][0]
                        slots = sb[1][1]
                        results["spells"][level] = {"spells": spell_list}
                        if slots != '':
                            results["spells"][level]["slots"] = slots

        return results
        
    def _replace_damage(self, text):
        return re.sub("\s*([0-9]+\s)?(\()?((?:[+-]?\s*[0-9]+d[0-9]+\s*)+(?:[+-]?\s*[0-9]+)?)(\)?\s+)(({})\s+damage)".format("|".join(constants.DAMAGE_TYPES)),
            " \g<1>\g<2>{@damage \g<3>}\g<4>\g<5>", text, flags=re.IGNORECASE)

    def _replace_dcs(self, text):
        return re.sub("\s+(dc)\s*([0-9]+)([()\s,])".format("|".join(constants.ABILITIES)), " {@dc \g<2>}\g<3>", text, flags=re.IGNORECASE)

    def _replace_hit(self, text):
        return re.sub("\s([+-]?[0-9]+)\s*to\s*hit", " {@hit \g<1>} to hit", text, flags=re.IGNORECASE)

    def _replace_rolls(self, text):
        return re.sub("(?<!damage)\s+([0-9]+d[0-9]+)\s*([+-]\s*[0-9]+)?\s*([^}])", " {@dice \g<1>\g<2>} \g<3>", text)

    def add_action(self, title, text):
        text = " ".join(text)

        text = self._replace_hit(text)
        text = re.sub("Melee\s*Weapon\s*Attack:", "{@atk mw}", text)
        text = re.sub("Ranged\s*Weapon\s*Attack:", "{@atk rw}", text)
        text = self._replace_damage(text)
        text = re.sub("(?:Hit: )([0-9]+)\s", "{@h}\g<1> ", text, flags=re.IGNORECASE)
        text = self._replace_dcs(text)
        text = self._replace_rolls(text)

        self.actions.append({"name":title, "entries":[text]})
        pass

    def add_legendary_action(self, title, text):
        text = " ".join(text)
        if self.legendary_header == None:
            self.legendary_header = title + " " + text
            return self.legendary_header

        text = self._replace_damage(text)
        text = self._replace_dcs(text)
        text = self._replace_rolls(text)

        self.legendary.append({"name":title, "entries":[text]})


    def to_json(self):
        return {
            "name":self.name,
            "size":self.size,
            "type":self.type,
            "source":self.source,
            "alignment":self.align,
            "ac":self.ac,
            "hp": self.hp,
            "speed":self.speed,
            **self.attributes,
            "passive":self.passive_perception,
            "cr":self.cr,
            "senses":self.senses,
            "senseTags":self.senseTags,
            "save":self.saves,
            "skill":self.skills,
            "resist":self.resistances,
            "immune":self.damage_immunities,
            "conditionImmune":self.condition_immunities,
            "languages":self.languages,
            "traits":self.traits,
            "action": self.actions,
            "legendary":self.legendary,
            "legendaryHeader":self.legendary_header,
            "spellcasting":self.spellcasting
        }

    def print(self):
        print(self.name)
        print(self.size, self.type, ",", self.align, "\t\t", self.source)
        print("AC", json.dumps(self.ac))
        if "special" in self.hp:
            print("HP {}".format(self.hp))
        else:
            print("HP", "{} ({})".format(self.hp["average"], self.hp["formula"]))
        print("Speed", ",".join(["{} {}".format(s, self.speed[s]) for s in self.speed]))
        
        print("\n======== Abilities ========")
        print(["{}:{}".format(a, self.attributes[a]) for a in self.attributes])

        print("\n======== Defence ========")
        print("Saving Throws", ", ".join(["{}{}".format(s, self.saves[s]) for s in self.saves]))
        print("Skills", ", ".join(["{}{}".format(s, self.skills[s]) for s in self.skills]))
        print("Damage Resistances {}".format(self.resistances))
        print("Damage Immunities {}".format(self.damage_immunities))
        print("Vulnerabilities {}".format(self.vulnerabilities))
        print("Condition Immunities {}".format(self.condition_immunities))
        print("Senses", ", ".join(self.senses) + ", Passive perception {}".format(self.passive_perception))
        print("Languages", ", ".join(self.languages))
        print("Challenge", self.cr)
        print()
        for f in self.traits:
            print("{}: {}\n".format(f['name'], f['entries'][0]))

        for s in self.spellcasting:
            print("{}: {}".format(s["name"], s["ability"]))
            print(s["headerEntries"][0])
            for freq in ["at will", "constant"]:
                if freq in s:
                    print("{}: {}".format(freq, s[freq]))
            for freq in ["daily","rest","weekly", "spells"]:
                if freq in s:
                    print("{}:".format(freq))
                    for level in s[freq]:
                        print("    {}: {}".format(level, s[freq][level]))
            if "footerEntries" in s:
                print(s["footerEntries"][0])

        if len(self.actions) > 0:
            print("\n======== Actions ========")
            for f in self.actions:
                print("{}: {}\n".format(f['name'], f['entries'][0]))

        if len(self.legendary) > 0:
            print("\n======== Legendary Actions ========")
            print(self.legendary_header + "\n")
            for f in self.legendary:
                print("{}: {}\n".format(f['name'], f['entries'][0]))

    def __init__(self):
        self.name = ""
        self.size = ""
        self.type = ""
        self.source = ""
        self.align = []
        self.ac = []
        self.hp = {}
        self.speed = {}
        self.attributes = {}
        self.passive_perception = []
        self.cr = {}
        self.senses = []
        self.senseTags = []
        self.saves = {}
        self.skills = {}
        self.resistances = []
        self.damage_immunities = []
        self.condition_immunities = []
        self.vulnerabilities = []
        self.languages = []
        self.traits = []
        self.actions = []
        self.legendary = []
        self.legendary_header = None
        self.spellcasting = []