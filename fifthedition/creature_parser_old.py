from fifthedition.creature import Creature

from utils.datatypes import Line, Section

class CreatureParser(object):

    def __init__(self):
        pass

    def __set_feature(self, creature: Creature, line: Section) -> bool:
        in_feature = False
        if "senses" in line.attributes:
            creature.set_senses(line)
            in_feature=True
        if "cr" in line.attributes:
            creature.set_cr(line)
            in_feature=True
        if "skills" in line.attributes:
            creature.set_skills(line)
            in_feature=True
        if "resistances" in line.attributes:
            creature.set_resistances(line)
            in_feature=True
        if "vulnerabilities" in line.attributes:
            creature.set_vulnerabilities(line)
            in_feature=True
        if "languages" in line.attributes:
            creature.set_languages(line)
            in_feature=True
        if "saves" in line.attributes:
            creature.set_saves(line)
            in_feature=True
        if "dam_immunities" in line.attributes:
            creature.set_immunities(line)
            in_feature=True
            pass
        if "con_immunities" in line.attributes:
            creature.set_condition_immunities(line)
            in_feature=True
            pass
        if "vulnerabilities" in line.attributes:
            creature.set_vulnerabilities(line)
            in_feature=True
            pass
        
        if in_feature:
            return True
        else:
            return False

    def parse_defence_block(self, creature: Creature, current_block: Section, line: Line):

        block_finished = False
        state = 3

        #Check if the next line is offset from the current, but still within the same column
        is_offset = len(current_block) > 0 and bound["left"] > current_block[2]["left"] + 5 and current_block[2]["left"] + current_block[2]["width"] > bound["left"]

        next_current_block = [attrib, [line.strip()], bound]

        if len(current_block) > 0  and ("cr" in current_block[0] or "proficiency" in current_block[0]):
            block_finished = True
            next_current_block = []
            state = 4
        elif is_offset or len(attrib) == 0:
            if current_block == []:
                return [[], [line.strip()], bound], 3
            else:
                current_block[1].append(line)
                return current_block, 3
        else:
            if len(current_block) > 0:
                if len(attrib) > 0:
                    block_finished = True

        if block_finished:
            l = " ".join(current_block[1])
            a = current_block[0]
            if not self.__set_features(creature, l, a):
                state = 4

        return next_current_block, state


def parse_feature_block(char, current_block, line, bound, attrib):

    parts = line.split(".")
    tag = parts[0]

    if len(parts) == 2:
        text = parts[1]
    else:
        text = ".".join(parts[1:])

    new_block = len(current_block) == 0 #Easy case, new block
    #Check first sentence is less than 6 words (not including anything in brackets) and starts with a capital
    has_title = len(line.split()) > 5 and len(tag.split("(")[0].split()) < 6 and tag[0].isupper() and tag.split()[0].lower() not in constants.ABILITIES
    is_end = "end" in attrib
    
    #Does the line finish early (aka end of paragraph). Ignore this for spell blocks
    is_short = len(current_block) > 0 and (bound["width"] < current_block[2]["width"] * 0.8) and "spellcasting" not in current_block[0].lower()

    spell_list = False
    if len(current_block) > 0 and "spellcasting" in current_block[0].lower():
        if re.match("(cantrip|1st|2nd|3rd|[4-9]th)", line, re.IGNORECASE):
            spell_list = True

    #Check if we're at the start of a new feature
    if not spell_list and (new_block or has_title or is_end):
        if len(current_block) > 0:
            char.add_feature(current_block[0], current_block[1])
            current_block = []
        current_block = [tag, [text.strip()], bound]
    else:
        current_block[1].append(line.strip())
        if is_short:
            char.add_feature(current_block[0], current_block[1])
            current_block = []

    return current_block

def parse_action_block(char, current_block, line, bound, attrib):
    parts = line.split(".")
    tag = parts[0]
    text = ".".join(parts[min(1, len(parts)):])

    new_block = len(current_block) == 0 #Easy case, new block
    #Check first sentence is less than 6 words (not including anything in brackets) and starts with a capital
    has_title = len(line.split()) > 5 and len(tag.split("(")[0].split()) < 6 and tag[0].isupper() and tag.split()[0].lower() not in constants.ABILITIES
    #Does the line finish early (aka end of paragraph). Ignore this for spell blocks
    is_short = False#len(current_block) > 0 and (bound["width"] < current_block[2]["width"] * 0.75)
    is_attack_start = "melee_attack" in attrib or "ranged_attack" in attrib
    is_end = "end" in attrib
    is_table = len(line) > 0 and line[0].isnumeric()

    #Check if we're at the start of a new feature
    if not is_table and (new_block or has_title or is_attack_start or is_end):
        if len(current_block) > 0:
            char.add_action(current_block[0], current_block[1])
            current_block = []
        current_block = [tag, [text.strip()], bound]
    else:
        if is_table:
            current_block[1].append("\n" + line.strip())
        else:
            current_block[1].append(line.strip())
        # if is_short:
        #     char.add_action(current_block[0], current_block[1])
        #     current_block = []

    return current_block

def parse_legendary_action_block(char, current_block, line, bound, attrib):
    parts = line.split(".")
    tag = parts[0]
    text = ".".join(parts[min(1, len(parts)):])

    new_block = len(current_block) == 0 #Easy case, new block
    #Check first sentence is less than 6 words (not including anything in brackets) and starts with a capital
    has_title = len(line.split()) > 5 and len(tag.split("(")[0].split()) < 6 and tag[0].isupper() 
    #Does the line finish early (aka end of paragraph). Ignore this for spell blocks
    is_short = False#len(current_block) > 0 and (bound["width"] < current_block[2]["width"] * 0.75)
    is_end = "end" in attrib
    is_table = len(line) > 0 and line[0].isnumeric()

    #Check if we're at the start of a new feature
    if not is_table and (new_block or has_title or is_end):
        if len(current_block) > 0:
            char.add_legendary_action(current_block[0], current_block[1])
            current_block = []
        current_block = [tag, [text.strip()], bound]
    else:
        if is_table:
            current_block[1].append("\n" + line.strip())
        else:
            current_block[1].append(line.strip())
        # if is_short:
        #     char.add_action(current_block[0], current_block[1])
        #     current_block = []

    return current_block


def parse_statblock(lines):

    char = creature.Creature()

    states = [
        0, #title,
        1, #defence
        2, #attributes
        3, #flavour
        4, #features
        5, #actions
        6, #legendary actions
    ]

    attrib_vals = ["array_values", "array_title"]
    flavour_vals = ["senses", "cr", "languages", "skills", "resistances", "saves"]

    current_block = []
    state = 0

    for i in range(len(lines)):
        #print(lines[i])
        line,bound,attrib = lines[i]
        #line = line.replace("\n", " ")

        print(line)
        print(attrib)
        #print()

        ### Look ahead to join lines
        if state < 3 and i+2 < len(lines):
            while len(lines[i+1][2]) == 0:
                line += " " + lines[i+1][0]
                i += 1
                print(i, lines[i+1])

        #print(line, attrib)

        ### Force Switch to Later States:
        if state < 2:
            for a in attrib: 
                if a in attrib_vals:
                    print("WARNING. Did not find complete defence block")
                    state = 2
                    break

        if state < 3:
            for a in attrib:
                if a in flavour_vals:
                    print("WARNING. Did not find attributes")
                    state = 2
                    break

        if state < 5:
            if "action_title" in attrib:
                state = 5
                if len(current_block) > 0:
                    char.add_feature(current_block[0], current_block[1])
                    current_block = []
                continue

        if state < 6:
            if "legendary_action_title" in attrib:
                state = 6
                if len(current_block) > 0:
                    char.add_action(current_block[0], current_block[1])
                    current_block = []
                continue

        ### Header Block
        if state == 0 and "statblock_title" in attrib:
            char.set_name(line)
        elif state == 0 and "race_type_header" in attrib:
            char.set_size_type_alignment(line)
            state = 1

        ### Defense Block
        if state == 1:
            if "hp" in attrib:
                char.set_hp(line)
            if "speed" in attrib:
                char.set_speed(line)
            if "ac" in attrib:
                char.set_ac(line)

            if len(char.hp) > 0 and len(char.speed) > 0 and len(char.ac) > 0:
                state = 2
                continue

        ### Attributes
        if state == 2:
            if "array_values" in attrib:
                char.set_attributes(line)
                state = 3
                continue

        ### Flavour
        if state == 3:
            current_block, state = parse_defence_block(char, current_block, line, bound, attrib)
            if state > 3 and len(current_block) > 0:
                line = " ".join(current_block[1])
                bound = current_block[2]
                attrib = current_block[0]
                current_block = []

        ### Features
        if state == 4:
            current_block = parse_feature_block(char, current_block, line, bound, attrib)

        ### Actions
        if state == 5:
            current_block = parse_action_block(char, current_block, line, bound, attrib)

        ### Legendary Actions
        if state == 6:
            current_block = parse_legendary_action_block(char, current_block, line, bound, attrib)



    #for a in char.to_json()["action"]:
    #    print(a)  
    return char

