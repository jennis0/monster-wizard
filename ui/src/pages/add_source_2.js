import { Grid, Typography, Paper, Button, Stack, Divider } from "@mui/material";
import { Box } from "@mui/system";

function ImageButton ( {icon, children, onClick, width="100%", height="100%"}) {
    return (
        <Paper variant="elevation" elevation={2} sx={{height:"100%", width:200, height:150}}>
        <Button variant="contained" sx={{width:width, height:height, p:4, alignItems:"center"}} onClick={onClick}
            >
            <Stack spacing={1.5} sx={{alignItems:"center", height:"100%", justifyContent:"center"}}>
                {icon}
                {children}
            </Stack>
        </Button>
        </Paper>
    )
} 


export default function UploadPage () {
    
    return (
        <Grid container width="100%" height="100vh" direction="row">
            <Grid item xs={0} md={2}></Grid>
            <Grid container xs={8} direction="column" width="100%" alignItems="center">
                <Grid item xs={4}><Box/></Grid>
                <Grid item xs={4} alignItems="center" direction="column" justifyItems="center">
                        <Grid container spacing={2}>
                        <Grid item sx={12} lg={6} alignItems="center" width="100%">
                            <ImageButton icon={<img src={"icons/pdf.png"} width={30}/>} size="large">
                                <Typography variant="statblock" >Import PDF</Typography>
                            </ImageButton>

                        </Grid>
                        <Grid item xs={12} lg={6} alignItems="center" width="100%">
                            <ImageButton icon={<img src={"icons/fvtt.png"} width={30}/>} size="large">
                                <Typography variant="statblock" sx={{lineHeight:1.5}}>Import FoundryVTT Compendium</Typography>
                            </ImageButton>
                        </Grid>
                        </Grid>
                </Grid>
            </Grid>
        </Grid>
    )
}