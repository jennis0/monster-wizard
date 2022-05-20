import { CRTABLE, SHORT_SKILL_ABILITY_MAP, SKILL_MAP } from "../constants"

export function get_proficiency(statblock) {
    if (statblock.proficiency) {
      return statblock.proficiency
    }
    if (statblock.cr) { 
      return CRTABLE.filter(cr => cr[0] === statblock.cr.cr)[0][3]
    }
    return 0
}

export function get_default_skill_bonus(statblock, skill, proficient) {
    const ability = SHORT_SKILL_ABILITY_MAP[skill]
    let mod = 0;
    if (ability & statblock.abilities && statblock.abilities) {
        mod = Math.floor((statblock.abilities[ability] - 10) / 2)
    }
    return {skill:skill, mod:(proficient ? 1 : 0) * Number(get_proficiency(statblock)) + Number(mod), default:"true", prof:proficient}
}