import styled from "@emotion/styled";
import { Upload } from "@mui/icons-material";
import { Grid, Typography, Paper, Button, Stack, Dialog, DialogTitle, Backdrop, Container } from "@mui/material";
import { Box } from "@mui/system";
import { useState } from "react";
import CenteredContent from "../components/CenteredContent";
import SourceForm from "../components/SourceForm";

const FORMATS = {
    "pdf":{accept:".pdf,.json"},
    "fvtt":{accept:".json"}
}

export default function UploadPage () {
    return (
        <CenteredContent
            title="Import"
            body={<SourceForm />}
        />
    )
}