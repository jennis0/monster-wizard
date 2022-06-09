import { Add, Cancel, Close } from "@mui/icons-material"
import { Box, Button, Grid, Typography } from "@mui/material"
import { useState } from "react"
import { addSource } from "../libs/db"
import { StyledTextField } from "./FormFields"

export default function CreateSource({onCreate, onClose}) {
    const [title, setTitle] = useState("")
    const [author, setAuthor] = useState("")
    const [image, setImage] = useState("")

    const createSource = (callback) => () => {
        addSource(title, author, 0, null, null, null, "finished", [], null)
            .then(callback)
    }

    return (
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
            <Grid item xs={12}>
                <Box sx={{display:"flex", justifyContent:"space-between"}}>
                    <Button startIcon={<Close />} onClick={onClose}>Cancel</Button>
                    <Button 
                        elevation={1}
                        startIcon={<Add />}
                        disabled={title === "" || author === ""}
                        onClick={createSource(onCreate)}
                    >
                        Create
                    </Button>
                </Box>
            </Grid>
        </Grid>
    )
}