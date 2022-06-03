import { Add, Restore } from "@mui/icons-material"
import { IconButton, Typography, Box, Divider, Stack, ButtonGroup } from "@mui/material"


export default function TitleField ( {text, editable, onAdd, onReset} ) {
    return (
        <>
        <Stack direction="row" sx={{width:"100%", justifyContent:"space-between", p:0, m:0, alignItems:"center",}}>
            <Box sx={{display:"flex", flexDirection:"row"}}>
            <Typography variant="statblockSection" sx={{color:"primary.dark"}}>{text}</Typography>
            {editable && onReset && <IconButton onClick={onReset} sx={{p:0., m:0, ml:1, m:0}}><Restore sx={{borderRadius:"0px", fontSize: "24px" }} /></IconButton>}
            </Box>
            {editable && onAdd && <IconButton onClick={onAdd} sx={{p:0., m:0}}><Add sx={{borderRadius:"0px", fontSize: "30px" }} /></IconButton>}
        </Stack>
        <Divider  sx={{marginBottom:1, marginTop:-0.5}}/>
        </>
        )
        
}