import React, { useEffect, useState } from 'react'
import { db } from '../libs/db'
import { useLiveQuery } from 'dexie-react-hooks'
import { Paper, TextField, Stack, Box, Container, Grid, Divider, Typography } from '@mui/material'
import StatblockResultList from '../components/StatblockResultList'
import { useLocation, useNavigate } from 'react-router-dom'
import { useStatblockSearch, filterCR } from '../libs/search'
import SearchForm from '../components/SearchForm'
import CenteredContent from '../components/CenteredContent'


function SearchSubheader({setResults, sources}) {
    return (
        <SearchForm setResults={setResults} sources={sources}/>
    )
}

function SearchBody({results, sources}) {
    return (
            <StatblockResultList statblocks={results} sources={sources} sx={{width:"100%"}}/>
    )
}

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
        <CenteredContent
            title="Search"
            subheader={<SearchSubheader setResults={setResults} source={sources} />}
            body={<SearchBody results={results} sources={sources} />}
        />
    )
}