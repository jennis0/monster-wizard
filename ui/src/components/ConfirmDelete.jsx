import { Delete, Close } from "@mui/icons-material";
import { Box, Button, Dialog, Grid, Typography } from "@mui/material";



export default function ConfirmDelete( {open, title, setOpen, onDelete} ) {
    return (
        <Dialog open={open} PaperProps={{square:true, sx:{p:2, width:"400px"}}}>
            <Grid container spacing={1}>
                <Grid item xs={12}>
                    <Typography variant="nav" fontSize={24}>{`Delete ${title}?`}</Typography>
                </Grid>
                <Grid item xs={12}>
                    <Box sx={{display:"flex", justifyContent:"space-between"}}>
                        <Button startIcon={<Close />} onClick={() => setOpen(false)}>Cancel</Button>
                        <Button 
                            variant="contained"
                            elevation={1}
                            color="secondary"
                            startIcon={<Delete />}
                            onClick={() => {setOpen(false); onDelete()}}
                        >
                            Delete
                        </Button>
                    </Box>
                </Grid>
            </Grid>
        </Dialog>
    )
}