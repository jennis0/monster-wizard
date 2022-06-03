import React, { useEffect, useMemo, useState } from 'react';
import { Grid, Paper, Typography, Box, Stack, Button, IconButton, Popper, Dialog } from "@mui/material";
import SaveIcon from '@mui/icons-material/Save';
import EditIcon from '@mui/icons-material/Edit';

import Statblock from '../components/statblock/EditableStatblock';
import StatblockList, { sortByAlphabet } from '../components/StatblockList';
import PDFDisplay from '../components/PDFDisplay';
import { StyledTextField } from '../components/statblock/FormFields';
import B64Image from '../components/B64Image';


import { useParams } from 'react-router-dom'
import {db, updateSource, useSource} from '../libs/db'
import { useLiveQuery } from 'dexie-react-hooks';
import { Close, Done } from '@mui/icons-material';


function SourcePagePart( {source_id} ) {

    const statblocks = useLiveQuery(() => db.statblocks.where("source").equals(Number(source_id)).toArray())
    const images = useLiveQuery(() => db.images.where("source").equals(Number(source_id)).toArray())

    const [selected, setSelected] = useState(0);
    const [imageData, setImageData] = useState(null);

    const selectStatblock = (index) => {
        setSelected(index);
    }

    useEffect(() => {
        const options = images?.filter(i => i.reference === statblocks[selected].modified_data.image?.ref)
        if (options && options.length > 0) {
            setImageData(options[0].data)
        } else {
            setImageData(null)
        }
    }, [source_id, images, selected, statblocks])

    return (

    <Grid container item direction="row" spacing={0} height="95%">
    {statblocks && statblocks.length > 0 ? <>
        <Paper variant="elevation" elevation={3} sx={{p:0, m:0, width:"100%", height:"calc(100vh - 100px)", display:"flex"}}>
        <Grid container>
        <Grid item xs={0} lg={1.5}>
            <Paper square variant="outlined" sx={{p:0,m:0, overflowY:"auto", width:"100%", maxHeight:"calc(100vh - 120px)"}}>
                <StatblockList width={200} selected={selected} statblocks={statblocks.map(s => s.modified_data)} onClick={selectStatblock} title="" sort={sortByAlphabet} />
            </Paper>
        </Grid>
        <Grid item md={12} lg={6}>
            <Paper variant="elevation" elevation={0} square sx={{p:2, m:0, overflowY:"auto", height:"100%", width:"100%"}}>
                <Statblock statblock={statblocks[selected].modified_data} allowEdit={true}/>
            </Paper>
        </Grid>
        <Grid item md={12} lg={4}>
            <Paper variant="outlined" square sx={{p:2, m:0, overflowY:"auto", height:"100%", width:"100%"}}>
                {imageData && <B64Image 
                    image_data={imageData}
                    width={500}
                />}
            </Paper>
        </Grid>
        </Grid>
        </Paper>
       </>  : <></>} 
    </Grid>
)
}

function SourceTitlePart( {source} ) {
    const [tmpMeta, setTmpMeta] = useState()
    console.log("fp", source?.frontpage)
    const frontpage = useLiveQuery(() => db.images.where("id").equals(source?.frontpage >= 0 ? source.frontpage : -1).toArray(), [source])

    console.log(frontpage)

    useEffect(() => {
        if (source) {
            setTmpMeta(source)
        }
    }, [source])

    const [anchorEl, setAnchorEl] = useState(null)

    const updateTmpMeta = (field) => (e) => {
        const newMeta = {...tmpMeta}
        newMeta[field] = e.target.value
        setTmpMeta(newMeta)
    }

    const updateSourceMeta = () => {
        console.log("updating source", tmpMeta)
        updateSource(source.id, {title:tmpMeta.title, author:tmpMeta.author}, (e) => console.log(e))
        setAnchorEl(null)
    }

return (<>
        <Dialog
        id={"edit-source-meta-popper"} 
        open={Boolean(anchorEl)} 
        keepMounted={false}
    >
        <Paper 
            square variant="outlined" 
            sx={{p:1, display:"flex", flexDirection:"column", backgroundColor:"white", width:"500px"}}
        >
            <Grid container spacing={1}>
                <Grid item xs={12}>
                    <StyledTextField id="source-meta-update-title-field" 
                        label="Title" 
                        variant="statblockTitle"
                        value={tmpMeta?.title} 
                        onChange={updateTmpMeta("title")}    
                    />
                </Grid>
                <Grid item xs={12}>
                    <StyledTextField id="source-meta-update-author-field" 
                        label="Author" 
                        value={tmpMeta?.author} 
                        onChange={updateTmpMeta("author")}
                    />
                </Grid>
                <Grid item xs={12}>
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
            </Grid>
            </Grid>
        </Paper>
    </Dialog> 
    <Box sx={{height:"100px", width:"100%", p:0, m:0, overflow:"clip"}}>
        <Box
            sx={{height:"200px", position:"relative", leftMargin:-50, left:-50, width:"120%", top:-50, 
                p:1.6, pl:4,m:0, justifyContent:"space-between", display:"flex", flexDirection:"row",
                backgroundColor:"primary.light",
                backgroundImage:`linear-gradient(to bottom, #455a6422, #00000022), url(data:image/webp;base64,${frontpage?.length > 0  ? frontpage[0].data: null})`,
                backgroundSize:"cover", backdropFilter: "contrast(0%)", zIndex:1, filter: "blur(20px)", overflow:"hidden"
            }}
        />
        <Paper square variant="elevation" elevation={5} 
            sx={{position:"absolute", height:"100px", left:220, top:0, backgroundColor:"transparent", width:"100%", zIndex:2,
                p:1.6, pl:4,m:0, justifyContent:"space-between", display:"flex", flexDirection:"row",
            }}
        >
            <Stack>
            <Typography variant="pageTitle" color="primary.contrastText">
                {source?.title} <IconButton id="edit-source-meta-button" onClick={(e) => {console.log(e); setAnchorEl(anchorEl ? undefined : e.currentTarget)}}><EditIcon /></IconButton>
            </Typography>
            <Typography variant="pageSubtitle"  color="primary.contrastText">
                {source?.author}
            </Typography>
            </Stack>
            </Paper>
            </Box>

    </>)
}

export default function SourcePage () {

    const params = useParams();
    const source_id = params.id

    const source = useSource(source_id)

    return (<>
        <Grid container spacing={0} direction="column">
        <Grid item xs={2}>
            <SourceTitlePart source={source} />
        </Grid>
        </Grid>
        {source &&
        <SourcePagePart source_id={source?.id} />
        }
        </>
    )
}