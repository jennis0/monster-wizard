import React, { useState } from 'react';
import { Grid, Paper, Typography } from "@mui/material";

import Statblock from '../components/EditableStatblock';
import StatblockList, { sortByAlphabet } from '../components/StatblockList';
import UploadButton from '../components/UploadButton';
import PDFDisplay from '../components/PDFDisplay';

import { post_file } from '../libs/api';
import { DataContext } from '../libs/store';



export default function UploadPage() {
    const [selected, setSelected] = useState(1);
    const [source, setSource] = useState(null);
    const [page, setPage] = useState(1);
    const [pdfSource, setPDFSource] = useState(null);
    const [processedData, setProcessedData] = useState(null);

    function loadPDFSource(event) {
        const file = event.target.files[0];
        const reader = new FileReader();
        setSource(event.target.files[0]);
        reader.readAsDataURL(file);
        reader.onload = () => {
          setPDFSource(reader.result);
          var data = new FormData()
          data.append("file", event.target.files[0]);
          post_file(data, (x) => {console.log(x); setProcessedData(x)});
        };
    }
  
    const selectStatblock = (index) => {
        const page = processedData?.statblocks[0].creatures[index].source?.page
        if (page) {
            setPage(page);
        }
        setSelected(index);
    }

    return (
        <Grid container spacing={2}>
            <Grid item xs={12}>
                <Paper elevation={0} sx={{width:"100%", margin:2}}>
                    <Typography variant="h4">File: {processedData?.statblocks[0]?.title}</Typography>
                    <Typography variant="h6">{processedData?.statblocks[0]?.creatures.length} Statblocks Loaded</Typography>
                    <UploadButton onChange={loadPDFSource}>Load New File</UploadButton>
                </Paper>
                
            </Grid>
            <Grid item xs={12} md={6}>
                <Paper elevation={1} sx={{leftMargin:2, padding:2, display:"flex", flexDirection:"row", flexWrap:"nowrap"}}>
                    <StatblockList statblocks={processedData?.statblocks[0]} onClick={selectStatblock} title={processedData?.title} sort={sortByAlphabet} />
                    <Statblock statblock={processedData?.statblocks[0].creatures[selected]}/>
                </Paper>
            </Grid>
            <Grid item xs={12} md={6} >
            <Paper elevation={1} sx={{rightMargin:2, padding:2}}>
                <PDFDisplay pdfContent={pdfSource} processedData={processedData} page={page} setPage={setPage} style={{margin:5}}/>
            </Paper>
            </Grid>
        </Grid>
    )
}