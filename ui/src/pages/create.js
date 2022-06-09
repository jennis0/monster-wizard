import { Add, ExpandLess, ExpandMore } from "@mui/icons-material";
import { Button, Dialog,  Grid, Typography, Box } from "@mui/material";
import { useLiveQuery } from "dexie-react-hooks";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import CenteredContent from "../components/CenteredContent";
import CreateSource from "../components/CreateSource";
import { StyledDropdown } from "../components/FormFields";
import StatblockList from "../components/StatblockList";
import { cloneStatblock, createStatblock } from "../libs/create";
import { db } from "../libs/db";


function CreateSourceDialog( {open, setOpen, setSource} ) {
    return (
        <Dialog open={open} PaperProps={{square:true, sx:{p:1}}}>
            <CreateSource onClose={() => setOpen(false)} onCreate={(s) => setSource(s.title)} />
        </Dialog>
    )
}

function CreateBody () {

    const sources = useLiveQuery(() => db.sources.toArray())
    const navigate = useNavigate()

    const [usedStatblocks, setUsedStatblocks] = useState([])
    const [selectedSource, setSelectedSource] = useState(null)
    const [copyOpen, setCopyOpen] = useState(false)
    const [newSourceOpen, setNewSourceOpen] = useState(false)

    const onCreate = (sbToCopy=null) => {
        const s_id = sources.filter(s => s.title === selectedSource)[0].id
        if (!sbToCopy) {
            createStatblock(s_id)
        } else {
            cloneStatblock(s_id, sbToCopy)
        }
        
        navigate(`/sources/${s_id}`)
    }

    console.log(usedStatblocks)

    return (<>
        <CreateSourceDialog open={newSourceOpen} setOpen={setNewSourceOpen} setSource={setSelectedSource}/>
        <Grid container spacing={1}>
        <Grid item xs={12}>
        <Typography variant="nav">Set Source</Typography>
        <StyledDropdown
            id={"source-select"} label="Source" options={sources?.map(s => s.title)}
            value={selectedSource} onChange={(e) => setSelectedSource(e.target.value)}
        />
        </Grid>
        <Grid item xs={12} textAlign="end">
        <Button startIcon={<Add />} onClick={() => setNewSourceOpen(true)}>New Source</Button>
        </Grid>
        <Grid item xs={12}>
            <Button sx={{width:"100%"}} 
                endIcon={copyOpen ? <ExpandLess /> : <ExpandMore />} 
                onClick={() => setCopyOpen(!copyOpen)}
                variant="contained"
                disabled={selectedSource === null}
            >
                Copy Existing
            </Button>
            {copyOpen &&
            <StatblockList statblocks={usedStatblocks} sources={sources} onClick={onCreate}
                setStatblocks={setUsedStatblocks} 
                showSources={true} showErrors={false} perPage={10} dense
            />}
        </Grid>

        <Grid item xs={12}>
            <Button sx={{width:"100%"}} 
                variant="contained"
                disabled={selectedSource === null}
                onClick={(e) => onCreate()}
            >
                Create New
            </Button>
        </Grid>
    </Grid>
    </>
    )
}

export default function CreatePage() {


    return (<>
        <CenteredContent
            title="Create New Statblock"
            body={
                <Box sx={{p:2}}>
                <CreateBody />
                </Box>
            }
        />
    </>
    )
}