import React, { useState } from 'react'; 
import UploadButton from "./UploadButton";

import { TextField } from "@mui/material";

export default function UploadForm() {

    const [targetFile, setTargetFile] = useState(null);

    return (
        <Paper>
            { targetFile ? 
                <UploadButton /> :
                <div>
                    <TextField label="Title" />
                    <TextField label="Authors" />
                </div>
            }
        </Paper>
    )
}