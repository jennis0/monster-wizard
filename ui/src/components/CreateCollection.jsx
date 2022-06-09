import { Add, Cancel, Close } from "@mui/icons-material";
import { ButtonGroup, Grid, Box, Button, Typography } from "@mui/material";
import { useState } from "react";
import { addCollection } from "../libs/db";
import { StyledTextField } from "./FormFields";
import { LongText } from "./statblock/ComplexParts";


export default function CreateCollection( {open, onClose, onCreate}) {
    const [title, setTitle] = useState("")
    const [description, setDescription] = useState("")

    const createCollection = (callback) => () => {
        addCollection(title, description, null, []).then(callback)
    }

    return (
        <Box>
            <Grid container spacing={1}>
                <Grid item xs={12}>
                    <Typography variant="nav">New Collection</Typography>
                </Grid>
                <Grid item xs={12}>
                    <StyledTextField label="Title" 
                        onChange={(e) => setTitle(e.target.value)} value={title}/>
                </Grid>
                <Grid item xs={12}>
                    <LongText value={description} description="Description" 
                        onChange={(e) => setDescription(e.target.value)} />
                </Grid>
                <Grid item xs={12}>
                    <Box sx={{display:"flex", justifyContent:"end"}}>
                        <Button sx={{mr:1}} startIcon={<Close />} onClick={onClose}>
                            Cancel
                        </Button>
                        <Button startIcon={<Add />}  disabled={title === ""}
                            onClick={createCollection(onCreate)}
                        >
                            Create
                        </Button>
                    </Box>
                </Grid>
            </Grid>
        </Box>
    )
}