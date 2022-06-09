import { db } from "./db";


export function deleteStatblockFromCollection(collection_id, statblock_id) {
    db.transaction('rw', db.collections, async () => {
        const coll = await db.collections.get(collection_id)
        if (coll) {
            const statblocks = coll.statblocks
            db.collections.update(collection_id, 
                {statblocks:statblocks.filter(s => s.id !== statblock_id)}
            )
        }
    })
}

export function addStatblockToCollection(collection_id, statblock_id) {
    db.transaction('rw', db.collections, async () => {
        const coll = await db.collections.get(collection_id)
        if (coll) {
            const statblocks = coll.statblocks.filter(s => s !== null && s !== undefined)
            if (statblocks.indexOf(statblock_id) < 0) {
                statblocks.push(statblock_id)
                db.collections.update(collection_id, 
                    {statblocks:statblocks}
                )
            }
        }
    })
}