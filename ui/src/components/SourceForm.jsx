import { useState } from 'react'

import { Grid, Typography, Stack, Box, Button, ButtonBase } from '@mui/material'
import { Done, Add, Article } from '@mui/icons-material'

import UploadButton from './UploadButton'
import { StyledTextField } from './FormFields'
import PDFDisplay from './PDFDisplay'

function ImageButton ( {icon, children, onClick, width="100%", height="100%"}) {
    return (
        <Button sx={{width:width, height:height, p:4, alignItems:"center"}} onClick={onClick}>
            <Stack spacing={1.5} sx={{alignItems:"center", height:"100%"}}>
                {icon}
                {children}
            </Stack>
        </Button>
    )
} 

export default function SourceForm( {source, setSource, acceptDocument} ) {

    const [pdfMetadata, setPDFMetadata] = useState({numPages:null})

    const updateSourceField = (field) => (e) => {
        const newSource = {...source}
        newSource[field] = e.target.value
        setSource(newSource)
    }

    return (
    <Box sx={{width:"100%", height:"100%", justifyItems:"center", alignItems:"center"}}>
    {source === null || source === undefined ? 
    <Grid container spacing={1}>
        <Grid item xs={6}>
            <ImageButton icon={<img src={"icons/pdf.png"} width={30}/>}>
                <Typography variant="h6">Load PDF</Typography>
            </ImageButton>
        </Grid>
        <Grid item xs={6}>
            <ImageButton icon={<img src={"icons/fvtt.png"} width={30}/>} size="large" sx={{height:292, width:"100%"}}>
                <Typography><b>Load Foundry Compendium</b></Typography>
            </ImageButton>
        </Grid>
    </Grid> :
    <Grid container direction="row" sx={{height:"500px"}}>
        <Grid item xs={4}>
            <Stack justifyContent="center" alignContent="center">
                <Typography variant="h6">New Source</Typography>
                <StyledTextField label="Title" onChange={updateSourceField("title")} value={source.title}/>
                <StyledTextField label="Author(s)" onChange={updateSourceField("author")} value={source.author}/>
                <StyledTextField label="Pages" value={pdfMetadata.numPages} disabled />
                <UploadButton sx={{m:10}} onChange={updateSourceField("filename")}>Set Document</UploadButton>
                <Button onClick={acceptDocument} startIcon={<Done />} disabled={source.file === null || source.file === undefined}>Confirm</Button>
            </Stack>
        </Grid>
        <Grid item xs={8} justifyContent="center" alignContent="center" textAlign="center">
            <Stack justifyContent="center" alignContent="center" textAlign="center" spacing={2}>
                <PDFDisplay pdfContent={source.file} page={1} scale={0.55} sendData={setPDFMetadata}/>
            </Stack>
        </Grid>
    </Grid>
    }
    </Box>)
}