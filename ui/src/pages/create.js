import { Add, ExpandLess, ExpandMore } from "@mui/icons-material";
import { Button, Dialog, DialogActions, DialogContent, Grid, Paper, Typography, Stack, Box } from "@mui/material";
import { useLiveQuery } from "dexie-react-hooks";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import CenteredContent from "../components/CenteredContent";
import { StyledDropdown, StyledTextField } from "../components/FormFields";
import StatblockList from "../components/StatblockList";
import StatblockResultList from "../components/StatblockResultList";
import { cloneStatblock, createStatblock } from "../libs/create";
import { addSource, db } from "../libs/db";
import { useStatblockSearch } from "../libs/search";


function NewSourceDialog( {open, setOpen, setSource} ) {
    const [title, setTitle] = useState("")
    const [author, setAuthor] = useState("")
    const [image, setImage] = useState("")

    const createSource = () => {
        addSource(title, author, 0, null, null, null, "finished", [], null)
            .then(setSource(title))
        setOpen(false)
    }

    return (
        <Dialog open={open} PaperProps={{square:true, sx:{p:0}}}>
            <DialogContent>
            <Grid container spacing={1}>
                <Grid item xs={12}>
                    <Typography variant="nav">Create New Source</Typography>
                </Grid>
                <Grid item xs={12}>
                    <StyledTextField label="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
                </Grid>
                <Grid item xs={12}>
                    <StyledTextField label="Author" value={author} onChange={(e) => setAuthor(e.target.value)} />
                </Grid>
            </Grid>
            </DialogContent>
            <DialogActions>
                <Button onClick={() => setOpen(false)}>Cancel</Button>
                <Button 
                    disabled={title === "" || author === ""}
                    onClick={createSource}>Create</Button>
            </DialogActions>
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
        <NewSourceDialog open={newSourceOpen} setOpen={setNewSourceOpen} setSource={setSelectedSource}/>
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