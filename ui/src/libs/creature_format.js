import { Typography, Divider } from "@mui/material"
import { PLURAL_TYPES, SHORT_ABILITIES, TYPES, SKILL_MAP, CRTABLE } from "../constants";

function to_cr(cr) {
    if (cr > 30) { cr = 30; }
    const cr_values = CRTABLE.filter(c => c[0] === cr)[0];
    return `${cr_values[1]} (${cr_values[2]} XP)`
}

function __do_cap(s, stopwords) {
    if (s && s.length > 0 && !stopwords.includes(s)) {
        return s[0].toUpperCase() + s.substring(1)
    }
    return s
}

export function capitalise(s, all_words=false, stopwords=["and", "the", "of", "in", "at"]) {
    if (all_words) {
        return s.split(" ").map(sp => __do_cap(sp, stopwords)).join(" ")
    }
    if (s != null) {
        return __do_cap(s, stopwords)
    }
    return "";
}

function join_with_and(ss) {
    if (!ss || ss.length === 0) {
        return "";
    }
    if (ss.length === 1) {
        return ss[0];
    }
        return `${ss.slice(0, ss.length-1).join(", ")}${ss.length > 2 ? "," : ""} and ${ss[ss.length-1]}`
}

function handle_type_pre_post(s) {
    return `${s.pre_text.length > 0 ? s.pre_text + " " : ""}${join_with_and(s.type.map(capitalise))}${s.post_text.length > 0 ? " " + s.post_text : ""}`
}

function format_race_type_alignment(monster) {
    if (!monster) {
        return ""
    }

    const size = capitalise(monster.size ? monster.size[0] : "");
    const type = capitalise(monster.creature_type ? monster?.creature_type?.type[0] : "");

    let parts = []
    if (monster.creature_type?.swarm) {
        if (monster.creature_type.swarm.swarm_size != null) {
            parts.push(`${size} swarm of ${monster.creature_type.swarm.swarm_size} ${type}s`)
        } else {
            console.log(type)
            const tIndex = TYPES.findIndex(t => t === type.toLowerCase());
            const pluralType = PLURAL_TYPES[tIndex];
            parts.push(`${size} swarm of ${capitalise(pluralType)}`)
        }
    } else {
        parts.push(`${size} ${type}`)
    }

    if (monster.alignment && monster.alignment.length > 0) {
        parts.push(capitalise(monster.alignment, true))
    }

    return parts.join(", ")
}

function format_ac(monster) {
    return monster.ac?.map((ac) => {
        const from_part = (ac.from.length > 0 ? `from ${join_with_and(ac.from)}` : "") + " " + ac.condition;
        return `${ac.ac} ${from_part !== " "? `(${from_part.trim()})`:""}`.trim()
    }).join(", ")
}

function format_hp(monster) {
    if (!monster) {
        return ""
    }
    return `${monster.hp?.average} (${monster.hp?.formula})`
}

function format_speed(monster) {
    if (!monster) {
        return ""
    }
    return monster.speed?.map((s) => {
        return `${s.type} ${s.distance}${s.measure}`
    }).join(", ");
}

function attributes_to_modifiers(monster) {
    if (!monster) {
        return ""
    }

    const res = SHORT_ABILITIES.map((a) => {
        const attr = monster.abilities ? monster.abilities[a] : null;
        if (!attr) { return "-"}
        const mod = Math.floor((attr - 10) / 2)
        return `${attr} (${mod >= 0 ? '+' : ''}${mod})`
    })
    return res
}

function format_skills(monster) {
    if (!monster) {
        return ""
    }

    return monster.skills ? monster.skills?.map((s) => {
        let skill_name = SKILL_MAP[s.skill]
        if (!skill_name) {
            skill_name = capitalise(s.skill, true);
        }
        return [skill_name, `${s.mod >= 0 ? '+' : ''}${s.mod}`]
    }) : []
}

function format_resistances(monster) {
    return monster?.resistances?.map(r => handle_type_pre_post(r)).join("; ")
}

function format_damage_immunities(monster) {
    return monster?.damage_immunities?.map(r => handle_type_pre_post(r)).join("; ")
}

function format_condition_immunities(monster) {
    return monster?.condition_immunities?.map(r => handle_type_pre_post(r)).join("; ")
}

function format_vulnerabilities(monster) {
    return monster?.vulnerabilities?.map(r => handle_type_pre_post(r)).join("; ")
}

function format_senses(monster) {
    const senses = monster?.senses ? monster.senses.map(s => {
        return `${s.type} ${s.distance}${s.measure}`
    }) : [];
    if (monster?.passive) {
        senses.push(`passive Perception ${monster.passive}`)
    }
    return senses.join(", ")
}

function format_languages(monster) {
    return join_with_and(monster?.languages)
}

function format_cr(monster) {
    if (!monster) {
        return ""
    }

    const lair = monster.cr?.lair ? `(${monster.cr.lair} in its lair)` : ""
    const coven = monster.cr?.coven ? `(${monster.cr.lair} with its coven)` : ""
    const cr = monster.cr ? to_cr(monster.cr.cr) : "Unknown"
    return `${cr} ${lair}${coven}`
}

function title_with_uses(feat) {
    if (feat.uses) {
        return `${feat.title} (${feat.uses.slots}/${feat.uses.period.replace("_"," ")})`
    }
    if (feat.recharge) {
        if (Number(feat.recharge.to) === 6) {
            return `${feat.title} Recharge ${feat.recharge.from}`
        } else {
            return `${feat.title} Recharge ${feat.recharge.from}-${feat.rechange.to}`
        }
    }
    return feat.title
}

function format_feature(feature) {
    return (<Typography sx={{marginBottom:1}}><b>{title_with_uses(feature)}.</b> {feature.text}</Typography>)
}

function format_action(action) {
    return (<Typography key={`action-${action.title}`} sx={{marginBottom:1}}><b>{title_with_uses(action)}.</b> {action.text}</Typography>)
}

function format_action_block(monster, type) {
    if (!monster) {
        return ""
    }

    const actions = monster.action?.filter(a => a.type === type)
    if (!actions || actions.length === 0) { return "" }

    const title = {
        action: "ACTIONS", 
        legendary: "LEGENDARY ACTIONS",
        reaction: "REACTIONS"
    };
    
    return (
        <div key={`action-block-${title.type}`} style={{marginTop:10}}>
        <Typography variant="h6">{title.type}</Typography>
        <Divider />
        {
            type === "legendary" ? 
            <Typography sx={{marginBottom:1}}>{monster.legendary_block}</Typography> : ""
        }
        {monster.action.filter(a => a.type === "action").map(format_action)}
        </div>
    );
}

export {
    format_race_type_alignment, 
    format_ac, 
    format_hp, 
    format_speed, 
    attributes_to_modifiers,
    format_skills,
    format_resistances,
    format_condition_immunities,
    format_damage_immunities,
    format_vulnerabilities,
    format_languages,
    format_senses,
    format_cr,
    format_feature,
    format_action,
    format_action_block
};