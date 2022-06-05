import React, { useState } from 'react';
import { Divider, Paper, List, ListItem, ListItemText, ListItemButton } from "@mui/material";

import Statblock from '../components/Statblock';
import StatblockList from '../components/StatblockList';
import UploadButton from '../components/UploadButton';



export default function Explorer() {
    const [selected, setSelected] = useState(null);
    const [source, setSource] = useState(null);

    const setNewSource = ((event) => {
        const reader = new FileReader();
        reader.onload = (event) => {
            const text = JSON.parse(reader.result)
            text.map(r => r.creatures.sort(c => c.source.page))
            setSource(text[0])
        }
        reader.readAsText(event.target.files[0])
    });
  
    return (
        <Paper sx={{display:"flex"}}>
        <div style={{display:"flex", "flexDirection":"column"}}>
            <StatblockList statblocks={source} onClick={setSelected} title={source?.title} />
            <UploadButton onChange={setNewSource}/>
        </div>
        <Statblock statblock={source?.creatures[selected]} style={{margin:2}}/>
        </Paper>
    )
}