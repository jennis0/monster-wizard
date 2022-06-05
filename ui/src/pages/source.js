import React, { useEffect, useMemo, useState } from 'react';
import { Grid, Paper, Typography, Box, Stack, Button, IconButton, Popper, Dialog, Tab, CircularProgress } from "@mui/material";
import SaveIcon from '@mui/icons-material/Save';
import EditIcon from '@mui/icons-material/Edit';

import StatblockViewer from '../components/viewers/StatblockViewer';
import StatblockList, { sortByAlphabet } from '../components/StatblockList';
import PDFViewer from '../components/viewers/PDFViewer';
import { StyledTextField } from '../components/FormFields';


import { Navigate, useParams } from 'react-router-dom'
import {db, updateSource, updateStatblock, useSource} from '../libs/db'
import { useLiveQuery } from 'dexie-react-hooks';
import { Add, Close, Done } from '@mui/icons-material';
import ImageViewer from '../components/viewers/ImageViewer';
import TabContext from '@mui/lab/TabContext';
import TabPanel from '@mui/lab/TabPanel';
import TabList from '@mui/lab/TabList';
import { useStatblockSearch } from '../libs/search';
import ExportButton from '../components/ExportButton';
import { createStatblock } from '../libs/create';

function AdditionalDataTabs( {image, imageOptions, pdf, page} ) {
    const [value, setValue] = useState("image")

    const handleChange = (event, newValue) => {
        setValue(newValue)
    }

    return (
        <Box sx={{with:"100%", typography:'smallNav'}}>
            <TabContext value={value} onChange={handleChange}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider', width:"100%", pl:0, pr:0, ml:0, mr:0}}>
                    <TabList onChange={handleChange} 
                        aria-label="Additional statblock information"
                        scrollButtons="false"
                    >
                        <Tab label={"Image"} value={"image"} key={`image-tab-label`}/>
                        <Tab label={"PDF"} value={"pdf"} key={`pdf-tab-label`}/>
                    
                    </TabList>
                </Box>
                <TabPanel value={"image"} key={"image-tab"}>
                    <ImageViewer image={image} imageOptions={imageOptions} allowEdit={true} defaultEdit={false} />
                </TabPanel>
                <TabPanel value={"pdf"} key={"pdf-tab"}>
                    <PDFViewer pdfContent={pdf} startPage={page} />
                </TabPanel>
            </TabContext>
        </Box>
    )
}


function SourcePagePart( {source_id, source, statblocks, setStatblocks} ) {

    const images = useLiveQuery(() => db.images.where("source").equals(Number(source_id)).toArray(), [source_id])
    const raws = useLiveQuery(() => db.pdfs.where("source").equals(Number(source_id)).toArray(), [source_id])

    const [selected, setSelected] = useState(0);
    const [currentImage, setCurrentImage] = useState(null);
    const [currentSource, setCurrentSource] = useState(null);

    const selectStatblock = (id) => {
        const candidates = statblocks.map((s,i) => [s, i]).filter(s => s[0].id === id)
        if (candidates.length >= 0) {
            setSelected(candidates[0][1])
        }
        //setSelected(index);
    }

    useEffect(() => {
        if (statblocks && statblocks[selected]) {
            const options = images?.filter(i => i.reference === statblocks[selected].modified_data.image?.ref)
            if (options && options.length > 0) {
                setCurrentImage(options[0])
            } else {
                setCurrentImage(null)
            }

            if (statblocks && statblocks[selected]) {
                console.log(raws)
                const candidates = raws?.filter(r => r.title.startsWith(statblocks[selected].modified_data.source.title))
                console.log("candidates", candidates.length)
                if (candidates?.length > 0) {
                    setCurrentSource([candidates[0], statblocks[selected].modified_data.source.page])
                }
            } else {
                setCurrentSource(null)
            }
        }
    }, [source_id, images, selected, statblocks])


    const onSave = (id) => (sb) => {
        updateStatblock(id, sb)
    }

    console.log("current source", currentSource, statblocks?.length)

    return (

    <Grid container item direction="row" spacing={0} height="calc(100vh-100px)">
        <Paper variant="elevation" elevation={3} sx={{p:0, m:0, width:"100%", height:"calc(100vh - 100px)", display:"flex"}}>
            <Grid container>
                <Grid item xs={0} lg={2.5}>
                    <Paper square variant="outlined" sx={{p:0,m:0, overflowY:"auto", width:"100%", height:"calc(100vh - 100px)"}}>
                        <StatblockList width={250} 
                            selected={selected} 
                            statblocks={statblocks} 
                            onClick={selectStatblock} 
                            title="" 
                            sort={sortByAlphabet} 
                            setStatblocks={setStatblocks}
                            defaultQuery={{sources:[Number(source_id)]}} 
                            sources={[source]}
                            disabled={["source"]}
                        />
                    </Paper>
                </Grid>
                <Grid item md={12} lg={4.5}>
                    <Paper variant="elevation" elevation={0} square sx={{p:2, m:0, overflowY:"auto", height:"calc(100vh - 100px)", width:"100%"}}>
                        {statblocks && <StatblockViewer statblockId={statblocks[selected]?.id} statblock={statblocks[selected]?.modified_data} allowEdit={true} onSave={onSave(statblocks[selected]?.id)}/>}
                    </Paper>
                </Grid>
                <Grid item sx={12} lg={5}>
                    <Paper variant="outlined" square sx={{p:2, m:0, overflowY:"auto", height:"100%", width:"100%"}}>
                        <AdditionalDataTabs 
                            image={currentImage} 
                            imageOptions={images} 
                            pdf={currentSource ? currentSource[0].file : null} 
                            page={currentSource ? currentSource[1] : null} />
                    </Paper>
                </Grid>
            </Grid>
        </Paper>
    </Grid>
)
}

function SourceTitlePart( {source, statblocks} ) {
    const [tmpMeta, setTmpMeta] = useState()
    const frontpage = null
    // const frontpage = useLiveQuery(() => db.images.where("id").equals(source?.frontpage >= 0 ? source.frontpage : -1).toArray(), [source])

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
        <Paper square variant="elevation" elevation={1} 
            sx={{position:"absolute", height:"100px", left:220, top:0, 
                backgroundColor:"transparent", width:"calc(100% - 220px)", zIndex:2,
                p:1.6, pl:4,m:0,  display:"flex", flexDirection:"row", justifyContent:"space-between"
            }}
        >
            <Stack>
                <Typography variant="pageTitle" color="primary.contrastText">
                    {source?.title} <IconButton id="edit-source-meta-button" onClick={(e) => {setAnchorEl(anchorEl ? undefined : e.currentTarget)}}><EditIcon /></IconButton>
                </Typography>
                <Typography variant="pageSubtitle"  color="primary.contrastText">
                    {source?.author}
                </Typography>
            </Stack>
            
            <Box sx={{alignContent:"center", pt:1.5, pr:1}}>
                <Button
                    variant="contained"
                    disabled={!source}
                    startIcon={<Add />}
                    sx={{height:"50px", mr:2}}
                    width={200}
                    onClick={() => createStatblock(source?.id)}
                >
                    Add Statblock
                </Button>
                <ExportButton title={source?.title} statblocks={statblocks} width={200} />
            </Box>
        </Paper>
    </Box>

    </>)
}

export default function SourcePage () {

    const params = useParams();
    const source_id = params.id

    const [statblocks, setStatblocks] = useState([])

    const source = useSource(source_id)

    return (<>
        <Grid container spacing={0} direction="column">
        <Grid item xs={2}>
            <SourceTitlePart source={source} statblocks={statblocks} />
        </Grid>
        </Grid>
        <SourcePagePart source_id={source_id} source={source} statblocks={statblocks} setStatblocks={setStatblocks}/>
        </>
    )
}