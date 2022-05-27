import { Add } from "@mui/icons-material"
import { IconButton, Typography, Box, Divider, Stack } from "@mui/material"


export default function TitleField ( {text, editable, onAdd} ) {
    return (
        <>
        <Stack direction="row" sx={{width:"100%", justifyContent:"space-between", p:0, m:0, alignItems:"center",}}>
            <Typography variant="statblockSection" sx={{color:"primary.dark"}}>{text}</Typography>
            {editable && <IconButton shape="rounded" onClick={onAdd} sx={{p:0., m:0}}><Add sx={{ fontSize: "30px" }} /></IconButton>}
        </Stack>
        <Divider  sx={{marginBottom:1, marginTop:-0.5}}/>
        </>
        )
        
}