import React, { useEffect, useState } from 'react'
import { db } from '../libs/db'
import { useLiveQuery } from 'dexie-react-hooks'
import { Paper, TextField, Stack, Box, Container, Grid, Divider, Typography } from '@mui/material'
import StatblockResultList from '../components/StatblockResultList'
import { useLocation, useNavigate } from 'react-router-dom'

function useSearch (text, deps) {
    return useLiveQuery(() => db.statblocks.filter(sb => sb.modified_data.name.toLowerCase().indexOf(text.toLowerCase()) >= 0).toArray(), deps)
}

export default function SearchPage() {
    const location = useLocation().search
    const navigate = useNavigate()
    let query= new URLSearchParams(location).get("query")
    query = query ? query : ""

    const results = useSearch(query, [query])
    const sources = useLiveQuery(() => db.sources.toArray())

    return (
        <Grid container sx={{width:"100%"}}>
            <Grid item xs={2} />
            <Grid item xs={8}>     
            <Paper sx={{width:"100%", height:"calc(100vh - 1px)", p:0, m:0}}>
                <Box sx={{m:0, p:0, height:"20vh", width:"100%", justifyContent:"center", display:"flex", flexGrow:1, flex:1, backgroundColor:"#eee"}} color="primary">
                    <Stack sx={{m:0, p:5, width:"100%"}} spacing={2}>
                        <Typography variant="h4">Search Statblocks</Typography>
                        <Divider width="100%"/>
                        <TextField component="form" sx={{width:"80%", p:5, alignSelf:"center"}}
                            placeholder="Search Statblocks"
                            defaultValue={query} 
                            InputProps={{sx:{backgroundColor:"white"}}}
                            onSubmit={(e) => {e.preventDefault(); navigate(`/search?query=${e.target[0].value}`)}}>
                        </TextField>
                    </Stack>
                </Box>
                <Divider sx={{width:"100%"}}/>
                <StatblockResultList statblocks={results} sources={sources} sx={{width:"100%"}}/>
                </Paper>   
            </Grid>
            <Grid item xs={2} />
        </Grid>
    )
}