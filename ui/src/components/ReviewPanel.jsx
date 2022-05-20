import React, { useEffect, useState } from 'react';
import { Grid, Paper, Typography, Box, Stack, Button, IconButton } from "@mui/material";
import SaveIcon from '@mui/icons-material/Save';
import EditIcon from '@mui/icons-material/Edit';

import Statblock from './EditableStatblock';
import StatblockList, { sortByAlphabet } from './StatblockList';
import UploadButton from './UploadButton';
import PDFDisplay from './PDFDisplay';


import { post_file } from '../libs/api';
import { addSource, addStatblock, addImage } from '../libs/db';
import { useNavigate } from 'react-router-dom';



export default function ReviewPanel( {source} ) {
    const [selected, setSelected] = useState(0);
    const [page, setPage] = useState(1);
    const [pdfSource, setPDFSource] = useState(null);
    const [processedData, setProcessedData] = useState(null);
    const navigate = useNavigate()

    useEffect(() => {
        setSelected(1)
        setPage(1)
        setPDFSource(null)
        setProcessedData(null)
        const file = source.filename;
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
          setPDFSource(reader.result);
          var data = new FormData()
          data.append("file", source.filename);
          post_file(data, (x) => {console.log("setting statblock", x); setProcessedData(x)});
        };
    }, [source])
  
    const selectStatblock = (index) => {
        const page = processedData?.statblocks[index].source?.page
        if (page) {
            setPage(page);
        }
        setSelected(index);
    }

    const onSave = () => {
        addSource(source.title, source.author, 1, source.filename.name, Date.toString(), source.version, "finished", processedData.frontpage).then(
            (id) => {
            for (const sb of processedData.statblocks) {
                addStatblock(id, sb, sb)
            }
            for (let i = 0; i < processedData.images.length; i+=1) {
                if(processedData.images[i].length > 0) {
                    for (const image of processedData.images[i]) {
                        addImage(id, i+1, image)
                    }
                }
            }
            navigate("/sources")
        })
    }

    return (
        <Grid container spacing={0} direction="column">
            <Grid item xs={2}>
                <Paper square variant="outlined" sx={{width:"100%", p:2, m:0, justifyContent:"space-between", display:"flex", flexDirection:"row"}}>
                    <Stack>
                    <Typography variant="h5">Review: {source.title} <IconButton><EditIcon /></IconButton></Typography>
                    <Typography variant="subtitle1">{source.filename.name}</Typography>
                    </Stack>
                    <Button onClick={onSave} startIcon={<SaveIcon />} variant="contained" disableElevation color="secondary" sx={{p:1, m:1, mr:5, pl:2, pr:2}} size="large">Save Statblocks</Button>
                </Paper>
            </Grid>
            <Grid container direction="row" spacing={0} height="95%">
            {processedData && processedData.statblocks ? <>
                <Grid item xs={4} md={2}>
                    <Paper square variant="outlined" sx={{p:0,m:0, overflowY:"auto", width:"100%", maxHeight:"95%"}}>
                        <StatblockList statblocks={processedData?.statblocks} onClick={selectStatblock} title="" sort={sortByAlphabet} />
                    </Paper>
                </Grid>
                <Grid item xs={4} md={5}>
                    <Paper variant="outlined" square sx={{p:2, m:0, overflowY:"auto", height:"100%", width:"100%"}}>
                        <Statblock statblock={processedData?.statblocks[selected]}/>
                    </Paper>
                </Grid>
                <Grid item xs={4} md={5} >
                    <Paper square variant="outlined" sx={{width:"100%", p:0, m:0, height:"93vh"}}>
                        <PDFDisplay pdfContent={pdfSource} processedData={processedData} page={page} setPage={setPage} style={{margin:5}} scale={1}/>
                    </Paper>
                </Grid></>  : <></>} 
            </Grid>
        </Grid>
    )
}