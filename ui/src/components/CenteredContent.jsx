
import { Typography, Box, Paper, Stack, Grid } from '@mui/material'
import { useEffect, useRef, useState } from 'react'


export default function CenteredContent( {title, subheader, body}) {
    const headerRef = useRef()
    const boxRef = useRef()
    const [bodyHeight, setBodyHeight] = useState(0)

    useEffect(() => {
        setBodyHeight(
            boxRef.current.clientHeight - headerRef.current.clientHeight - 35
        )
    }, [boxRef, headerRef])
    

    return (
        <Grid container spacing={0}>
            <Grid item xs={0} xl={2} columns={12}/>
            <Grid item xs={12} xl={8}>
                <Box sx={{m:0, ml:0, mr:0, pt:{lg:0, xl:2}, width:"100%", height:"100vh"}} ref={boxRef}>
                    <Paper sx={{p:2, width:"100%", backgroundColor:"primary.light"}} square elevation={3} ref={headerRef}>
                        <Stack spacing={1}>
                            <Typography variant="nav" fontSize={30} color="primary.contrastText">{title}</Typography>
                            {subheader}
                        </Stack>
                    </Paper>
                    <Paper sx={{p:0, width:"100%", maxHeight:bodyHeight, overflowY:"auto"}} square>
                        {body}
                    </Paper>
                </Box>
            </Grid>
        </Grid>
    )
}