import React, { useState, useEffect } from 'react'
import { Paper, Stack, Grid, Typography, Button} from "@mui/material"
import UploadButton from "../components/UploadButton"
import { StyledTextField } from '../components/FormFields'
import ReviewPanel from '../components/ReviewPanel'
import { load_pdf } from '../libs/pdf'
import PDFDisplay from '../components/PDFDisplay'
import { Done } from '@mui/icons-material'


function AddSourcePage( { setSource, pdfContent, setPDFContent }) {
    const [candidateSource, setCandidateSource] = useState({title:"", author:"", filename:"", pages:0, upload:"", version:"", status:"", frontpage:""})
    const [pdfMetadata, setPDFMetadata] = useState(null)

    const updateSource = (field) => (e) => {
        const newSource = {...candidateSource}
        newSource[field] = e.target.value
        setCandidateSource(newSource)
    }

    const setFilename = (e) => {
        let candidate_title = e.target.value.split('\\').pop().split('/').pop().split(".")[0].replace("_"," ").replace("-"," ").trim()
        candidate_title = candidate_title[0] + candidate_title.substring(1)

        setCandidateSource({...candidateSource, filename:e.target.files[0], title:candidate_title})
    }

    const acceptDocument = (e) => {
        setSource(candidateSource)
    }

    useEffect(() => {
        if (candidateSource.filename) {
            load_pdf(candidateSource.filename, setPDFContent)
        }
    }, [candidateSource])

    return (
        <Grid container justifyContent="center" alignContent="center" sx={{height:"100vh"}}>
            <Grid item xs={8} lg={6} justifyContent="center" alignContent="center">
                <Paper square variant="outlined" sx={{width:"100%", p:1, m:0}}>
                    <Grid container direction="row" sx={{height:"500px"}}>
                        <Grid item xs={4}>
                            <Stack justifyContent="center" alignContent="center">
                                <Typography variant="h6">New Source</Typography>
                                <StyledTextField label="Title" onChange={updateSource("title")} value={pdfMetadata && pdfMetadata.title ? pdfMetadata.title : candidateSource["title"]}/>
                                <StyledTextField label="Author(s)" onChange={updateSource("author")} value={pdfMetadata && pdfMetadata.author ? pdfMetadata.author : candidateSource["author"]}/>
                                <StyledTextField label="Pages" value={pdfMetadata?.numPages} />
                                <UploadButton onChange={setFilename} value={candidateSource["pages"]}>Set Document</UploadButton>
                                <Button onClick={acceptDocument} startIcon={<Done />} disabled={!candidateSource.filename}>Confirm</Button>
                            </Stack>
                        </Grid>
                        <Grid item xs={8} justifyContent="center" alignContent="center" textAlign="center">
                            <Stack justifyContent="center" alignContent="center" textAlign="center" spacing={2}>
                                <PDFDisplay pdfContent={pdfContent} page={1} scale={0.55} sendData={setPDFMetadata}/>
                            </Stack>
                        </Grid>
                    </Grid>
                </Paper>
            </Grid>
        </Grid>
    )
}


export default function UploadPage() {
    const [source, setSource] = useState(null)
    const [pdfContent, setPDFContent] = useState(null)

    return (
        source ? <ReviewPanel source={source} pdfContent={pdfContent} /> : <AddSourcePage setSource={setSource} pdfContent={pdfContent} setPDFContent={setPDFContent}/>
    )
}