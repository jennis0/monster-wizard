import styled from "@emotion/styled";
import { Upload } from "@mui/icons-material";
import { Grid, Typography, Paper, Button, Stack, Dialog, DialogTitle, Backdrop, Container } from "@mui/material";
import { Box } from "@mui/system";
import { useState } from "react";
import SourceForm from "../components/SourceForm";

const FORMATS = {
    "pdf":{accept:".pdf,.json"},
    "fvtt":{accept:".json"}
}

export default function UploadPage () {

    const [uploadFile, setUploadFile] = useState(null)

    return (
        <Box 
            width="100%" padding={5}   display="flex" height="100vh"
            justifyContent="center" alignItems="center" overflow="auto"
        >
            <Paper sx={{borderRadius:0, p:1, m:1, maxWidth:"1200px"}}>
                <Paper sx={{backgroundColor:"primary.light", m:-1, p:2, mb:1, color:"primary.contrastText"}} square elevation={1} variant="elevated">
                    <Typography variant="nav" fontSize={30}>Import</Typography>
                </Paper>
                <SourceForm />
            </Paper>
        </Box>
    )
}