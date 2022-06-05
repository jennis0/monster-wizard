import React, { useEffect, useState } from 'react'
import { db } from '../libs/db'
import { useLiveQuery } from 'dexie-react-hooks'
import { Paper, TextField, Stack, Box, Container, Grid, Divider, Typography } from '@mui/material'
import StatblockResultList from '../components/StatblockResultList'
import { useLocation, useNavigate } from 'react-router-dom'
import { useSearch, filterCR } from '../libs/search'
import SearchForm from '../components/SearchForm'


export default function SearchPage() {
    const location = useLocation()
    const navigate = useNavigate()
    const [query, setQuery] = useState("")
    const [results, setResults] = useState([])
    const [filters, setFilters] = useState([])

    useEffect(() => {
        const val = new URLSearchParams(location.search).get("query")
        if (val && val !== query) {
            setQuery(val)
        } else {
            setQuery("")
        }
    }, [location])

    const sources = useLiveQuery(() => db.sources.toArray())

    return (
        <Grid container sx={{width:"100%"}}>
            <Grid item xs={2} />
            <Grid item xs={8}>     
            <Paper variant="elevation" sx={{p:2, mt:1, mb:0, backgroundColor:"primary.light", color:"primary.contrastText"}} square>
                <Typography variant="nav" fontSize={30}>Search</Typography>
                <Box sx={{m:0, p:0, width:"100%", justifyContent:"center",
                        display:"flex", flexGrow:1, flex:1, backgroundColor:"primary.light"}}>
                    <SearchForm setResults={setResults} sources={sources}/>
                </Box>
                </Paper>

            <Paper variant="elevation" square
                    sx={{width:"100%", height:"90vh", p:0, m:0}}>
                <StatblockResultList statblocks={results} sources={sources} sx={{width:"100%"}}/>
            </Paper>   
            </Grid>
            <Grid item xs={2} />
        </Grid>
    )
}