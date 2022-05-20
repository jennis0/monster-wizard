import React, { useEffect, useState } from 'react';
import { Grid, Paper, Typography, Box, Stack, Button, IconButton, Popper } from "@mui/material";
import SaveIcon from '@mui/icons-material/Save';
import EditIcon from '@mui/icons-material/Edit';

import Statblock from '../components/EditableStatblock';
import StatblockList, { sortByAlphabet } from '../components/StatblockList';
import PDFDisplay from '../components/PDFDisplay';
import { StyledTextField } from '../components/FormFields';


import { useParams } from 'react-router-dom'
import {db, updateSource, useSource} from '../libs/db'
import { useLiveQuery } from 'dexie-react-hooks';
import { Close, Done } from '@mui/icons-material';

export default function SourcePage () {

    const params = useParams();
    const source_id = params.id
    const [tmpMeta, setTmpMeta] = useState(null)

    const source = useSource(source_id)
    const statblocks = useLiveQuery(() => db.statblocks.where("source").equals(Number(source_id)).toArray())
    const images = useLiveQuery(() => db.images.where("source").equals(Number(source_id)).toArray())

    useEffect(() => {
        if (source) {
            setTmpMeta(source)
        }
    }, [source])

    const [selected, setSelected] = useState(0);
    const [anchorEl, setAnchorEl] = useState(null)

    const selectStatblock = (index) => {
        setSelected(index);
    }

    const updateTmpMeta = (field) => (e) => {
        const newMeta = {...tmpMeta}
        newMeta[field] = e.target.value
        setTmpMeta(newMeta)
    }

    const updateSourceMeta = () => {
        console.log("updating source", tmpMeta)
        updateSource(source_id, {title:tmpMeta.title, author:tmpMeta.author}, (e) => console.log(e))
        setAnchorEl(null)
    }

    console.log("stats", statblocks, selected, images)

    return (<>
        <Popper 
            id={"edit-source-meta-popper"} 
            open={Boolean(anchorEl)} 
            anchorEl={anchorEl} 
            placement="bottom"
            disablePortal={false}
            keepMounted={false}
            zIndex={100}
        >
            <Paper 
                square variant="outlined" 
                sx={{p:1, display:"flex", flexDirection:"column", backgroundColor:"white", width:"500px"}}
            >
                <StyledTextField id="source-meta-update-title-field" 
                    label="Title" 
                    value={tmpMeta?.title} 
                    onChange={updateTmpMeta("title")}    
                />
                <StyledTextField id="source-meta-update-author-field" 
                    label="Author" 
                    value={tmpMeta?.author} 
                    onChange={updateTmpMeta("author")}
                />
                <Box sx={{display:"flex", flexDirection:"row", justifyContent:"space-between"}}>
                    <Button 
                        startIcon={<Close />} 
                        onClick={() => {setAnchorEl(null); setTmpMeta(source)}}
                    >
                        Cancel
                    </Button>
                    <Button 
                        startIcon={<Done />} 
                        onClick={updateSourceMeta}
                    >
                        Accept
                    </Button>
                </Box>
            </Paper>
        </Popper>
        <Grid container spacing={0} direction="column">
            <Grid item xs={2}>
                <Paper square variant="outlined" sx={{width:"100%", p:2, m:0, justifyContent:"space-between", display:"flex", flexDirection:"row"}}>
                    <Stack>
                    <Typography variant="h5">
                        Source: {source?.title} <IconButton id="edit-source-meta-button" onClick={(e) => {console.log(e); setAnchorEl(anchorEl ? undefined : e.currentTarget)}}><EditIcon /></IconButton>
                    </Typography>
                    <Typography variant="subtitle1">
                        {source?.author}
                    </Typography>
                    </Stack>
                </Paper>
            </Grid>
            <Grid container direction="row" spacing={0} height="95%">
            {statblocks && statblocks.length > 0 ? <>
                <Grid item xs={4} md={2}>
                    <Paper square variant="outlined" sx={{p:0,m:0, overflowY:"auto", width:"100%", maxHeight:"95%"}}>
                        <StatblockList statblocks={statblocks.map(s => s.data)} onClick={selectStatblock} title="" sort={sortByAlphabet} />
                    </Paper>
                </Grid>
                <Grid item xs={4} md={5}>
                    <Paper variant="outlined" square sx={{p:2, m:0, overflowY:"auto", height:"100%", width:"100%"}}>
                        <Statblock statblock={statblocks[selected].data}/>
                    </Paper>
                </Grid>
                <Grid item xs={4} md={5}>
                    <Paper variant="outlined" square sx={{p:2, m:0, overflowY:"auto", height:"100%", width:"100%"}}>
                        <img 
                            src={"data:image/webp;base64," + images.filter(i => i.page === statblocks[selected].data.source.page)[0]?.data}
                        />
                    </Paper>
                </Grid>
               </>  : <></>} 
            </Grid>
        </Grid>
        </>
    )
}