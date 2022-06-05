import { addStatblock, db } from "./db"
import _ from 'lodash'

export function createStatblock(source) {
    const sb = {
        name:"New Creature",
        size:["medium"],
        creature_type:{type:["humanoid"], swarm:false, swarm_size:null},
        ac:[{ac:10, from:[], conditions:""}],
        hp:{average:3, formula:"1d6"},
        speed:[{type:"walk", distance:"30", measure:"ft"}],
        abilities:{
            str:10, dex:10, con:10, int:10, wis:10, cha:10
        }
    }
    addStatblock(source, sb)
}

export function cloneStatblock(source_id, sb_id) {
    db.statblocks.where("id").equals(Number(sb_id)).toArray()
    .then(sb => {
            if (sb.length >= 0) {
                addStatblock(source_id, sb[0].modified_data)
            } else {
                console.log(`Couldn't clone as statblock ID ${sb_id} not found`)
            }
        }
    )
    
}