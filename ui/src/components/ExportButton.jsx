import { Button, CircularProgress } from "@mui/material"
import { useState } from "react"
import { convert } from '../libs/api';

function downloadJSON (filename, data) {
    console.log(data)
    const jsonString = `data:text/json;chatset=utf-8,${encodeURIComponent(
      JSON.stringify(data)
    )}`;
    const link = document.createElement("a");
    link.href = jsonString;
    link.download = filename;
    link.click();
};

function formatTitle(title) {
    return title +".json"
}

export default function ExportButton ( {title, statblocks, ...props} ) {
    const [converting, setConverting] = useState(false)
    
    const onExport = () => {
        setConverting(true)
        convert("fvtt", title, statblocks,
            (r) => {console.log(r); downloadJSON(formatTitle(title), r); setConverting(false)}
        )

    }

    return (
        <Button variant="contained" sx={{width:"150px", height:"50px"}} onClick={onExport} {...props}>
            {converting ? <CircularProgress sx={{color:"primary.light", fontSize:"20px"}} size={30}/> : "Export"}
        </Button>
    )
}