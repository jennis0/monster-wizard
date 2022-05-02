import { Typography, Divider } from "@mui/material"

const CRTABLE = [
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

const SKILLS = {
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

function to_cr(cr) {
    if (cr > 30) { cr = 30; }
    const cr_values = CRTABLE.filter(c => c[0] === cr)[0];
    return `${cr_values[1]} (${cr_values[2]} XP)`
}

function __do_cap(s, stopwords) {
    if (!stopwords.includes(s)) {
        return s[0].toUpperCase() + s.substring(1)
    }
    return s
}

function capitalise(s, all_words=false, stopwords=["and", "the", "of", "in", "at"]) {
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
    const size = capitalise(monster.size[0]);
    const type = capitalise(monster.creature_type.type[0]);

    let parts = []
    if (monster.creature_type.swarm) {
        if (monster.creature_type.swarm_size != null) {
            parts.push(`${size} swarm of ${monster.creature_type.swarm.swarm_size} ${type}s`)
        } else {
            parts.push(`${size} swarm of ${type}s`)
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
        const from_part = ac.from.length > 0 ? `(from ${ac.from.join(",")})` : ""
        return `${ac.ac} ${from_part} ${ac.ac.condition ? ac.ac.condition: ""}`
    }).join(", ")
}

function format_hp(monster) {
    return `${monster.hp?.average} (${monster.hp?.formula})`
}

function format_speed(monster) {
    return monster.speed?.map((s) => {
        return `${s.type} ${s.distance}${s.measure}`
    }).join(", ");
}

function format_attributes(monster) {
    const res = ["str", "dex", "con", "int", "wis", "cha"].map((a) => {
        const attr = monster.abilities ? monster.abilities[a] : null;
        if (!attr) { return "-"}
        const mod = Math.floor((attr - 10) / 2)
        return `${attr} (${mod >= 0 ? '+' : '-'}${mod})`
    })
    return res
}

function format_skills(monster) {
    return monster.skills?.map((s) => {
        let skill_name = SKILLS[s.skill]
        if (!skill_name) {
            skill_name = capitalise(s.skill, true);
        }
        return `${skill_name} ${s.mod >= 0 ? '+' : '-'}${s.mod}`
    }).join(", ")
}

function format_resistances(monster) {
    return monster.resistances?.map(r => handle_type_pre_post(r)).join("; ")
}

function format_damage_immunities(monster) {
    return monster.damage_immunities?.map(r => handle_type_pre_post(r)).join("; ")
}

function format_condition_immunities(monster) {
    return monster.condition_immunities?.map(r => handle_type_pre_post(r)).join("; ")
}

function format_vulnerabilities(monster) {
    return monster.vulnerabilities?.map(r => handle_type_pre_post(r)).join("; ")
}

function format_senses(monster) {
    const senses = monster.senses ? monster.senses.map(s => {
        return `${s.sense} ${s.distance}${s.measure}`
    }) : [];
    if (monster.passive) {
        senses.push(`passive Perception ${monster.passive}`)
    }
    return senses.join(", ")
}

function format_languages(monster) {
    return join_with_and(monster.languages)
}

function format_cr(monster) {
    const lair = monster.cr?.lair ? `(${monster.cr.lair} in its lair)` : ""
    const coven = monster.cr?.coven ? `(${monster.cr.lair} with its coven)` : ""
    const cr = monster.cr ? to_cr(monster.cr.cr) : "Unknown"
    return `${cr} ${lair}${coven}`
}

function format_feature(feature) {
    return (<Typography sx={{marginBottom:1}}><b>{feature.title}.</b> {feature.text}</Typography>)
}

function format_action(action) {
    return (<Typography sx={{marginBottom:1}}><b>{action.title}.</b> {action.text}</Typography>)
}

function format_action_block(monster, type) {
    const actions = monster.action?.filter(a => a.type === type)
    if (!actions || actions.length == 0) { return "" }

    const title = {
        action: "ACTIONS", 
        legendary: "LEGENDARY ACTIONS",
        reaction: "REACTIONS"
    };
    
    return (
        <div style={{marginTop:10}}>
        <Typography variant="h6">{title[type]}</Typography>
        <Divider />
        {
            type === "legendary" ? 
            <Typography sx={{marginBottom:1}}>{monster.legendary_block}</Typography> : ""
        }
        {monster.action.filter(a => a.type == "action").map(format_action)}
        </div>
    );
}

export {
    format_race_type_alignment, 
    format_ac, 
    format_hp, 
    format_speed, 
    format_attributes,
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