import React, { useEffect, useState } from 'react'
import { db } from '../libs/db'
import { useLiveQuery } from 'dexie-react-hooks'
import { Paper, TextField, Stack, Box } from '@mui/material'
import StatblockResultList from '../components/StatblockResultList'
import { useLocation, useNavigate } from 'react-router-dom'

function useSearch (text, deps) {
    return useLiveQuery(() => db.statblocks.filter(sb => sb.data.name.toLowerCase().indexOf(text.toLowerCase()) >= 0).toArray(), deps)
}

export default function SearchPage() {
    const location = useLocation().search
    const navigate = useNavigate()
    let query= new URLSearchParams(location).get("query")
    query = query ? query : ""

    const results = useSearch(query, [query])
    const sources = useLiveQuery(() => db.sources.toArray())

    return (<>
        <Paper variant="outlined" sx={{p:20, height:"10vh", width:"100%", justifyContent:"center"}}>
            <Paper variant="outlined" sx={{display:"flex", flexDirection:"row", width:"600px", justifyContent:"center"}}>  
                <Stack direction="row">
                    <TextField component="form" sx={{width:"600px"}}
                        defaultValue={query} 
                        onSubmit={(e) => {e.preventDefault(); navigate(`/search?query=${e.target[0].value}`)}}>
                    </TextField>
                </Stack>
            </Paper>
        </Paper>
        <Box>
        <StatblockResultList statblocks={results} sources={sources} sx={{width:"50%"}}/>
        </Box>
        </>
    )
}