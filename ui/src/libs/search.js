import { useLiveQuery } from "dexie-react-hooks"
import { db } from "./db"

export function filterType(values) {
    console.log("query", values)
    return (query) => 
        query.filter(sb => {
            return values.some(v => sb.modified_data.creature_type?.type.indexOf(v) >= 0)
        })
}

export function filterSize(values) {
    return (query) => 
        query.filter(sb => {
            return values.some(v => sb.modified_data.size?.indexOf(v) >= 0)
        })
}

export function filterSpellcasting() {
    return (query) => 
        query.filter(sb => {
            return sb.modified_data?.spellcasting?.length > 0
        })
}

export function filterCR(crMin, crMax) {
    return (query) =>
        query.filter(sb => {
            return sb.modified_data.cr?.cr >= crMin && sb.modified_data.cr?.cr <= crMax
        })
}

export function filterSource(sources) {
    return (query) => 
        query.filter(sb => sources.some(s => sb.source === s))
}

function doTextSearch(text, options) {
    return (sb) => {
        if (!options || options.name) {
            if (sb.modified_data.name.toLowerCase().indexOf(text) >= 0) {
                return true
            }
        }
        if (options?.feature) {
            if (sb.modified_data.features?.some(f => f.title.toLowerCase().indexOf(text) >= 0)) {
                return true
            }
        }
        if (options?.action) {
            for (const field of ["action", "bonus", "legendary", "reaction"]) {
                if (sb.modified_data[field]?.some(a => a.title.toLowerCase().indexOf(text) >= 0)) {
                    return true
                }
            }
        }
        return false
    }
}

export function searchText(text) {
    return (query) => 
        query.filter(doTextSearch(text.value, text.opts))
}

function createQueryFilters(query) {
    const filterList = []
    if (query.sources) {
        filterList.push(filterSource(query.sources))
    }
    if (query.types && query.types.length > 0) {
        filterList.push(filterType(query.types))
    }
    if (query.sizes && query.sizes.length > 0) {
        filterList.push(filterSize(query.sizes))
    }
    if (query.spellcasting) {
        filterList.push(filterSpellcasting())
    }
    if (query.cr) {
        filterList.push(
            filterCR(query.cr.min ? query.cr.min : -1,
                     query.cr.max ? query.cr.max : 1000)
        )
    }
    if (query.text && query.text.value) {
        console.log("creating text filter")
        filterList.push(searchText(query.text))
    }
    return filterList
}

export function useSearch(query) {
    console.log("query", query)
    console.log("rerunning search")
    return useLiveQuery(() => {
        let sbs = db.statblocks
        for (const filter of createQueryFilters(query)) {
            sbs = filter(sbs)
        }
        return sbs.toArray()
    }, [query])
}


// function useSearch (text, deps) {
//     return useLiveQuery(() => db.statblocks.filter(sb => sb.modified_data.name.toLowerCase().indexOf(text.toLowerCase()) >= 0).toArray(), deps)
// }