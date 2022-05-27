import { Container, Grid, Typography, Paper, Divider, Stack, Box, Skeleton } from '@mui/material'
import React, { useState } from 'react'
import SourceForm from '../components/SourceForm'
import StatblockList from '../components/StatblockList'

export default function UploadPage() {

    const [source, setSource] = useState(null)

    return (
        <Grid container sx={{height:"calc(100vh - 1px)", width:"100%", overflow:"clip", m:0, p:0, border:"0px"}}>
            <Grid item xs={3} />
            <Grid item xs={6} sx={{m:0, p:0}}>
                <Box sx={{height:"100%", width:"100%", m:0, p:0}}>
                    <Paper sx={{width:"100%", p:3, m:0, height:"100%"}}>
                        <Stack spacing={2} sx={{width:"100%"}}>
                            <Typography variant="h4">Upload Source</Typography>
                            <Divider />
                            <SourceForm source={source} setSource={setSource} />
                        </Stack>
                        <Stack spacing={1.5}>
                            {source ? 
                            <Grid container >
                                <Grid item xs={4}>
                                    <StatblockList />
                                </Grid>
                                <Grid item xs={4}>
                                    
                                </Grid>
                            </Grid>
                            : <Typography variant="h6">Theres nothing here yet...</Typography>}
                        </Stack>
                    </Paper>
                </Box>
            </Grid>
            <Grid item xs={3} />
        </Grid>
    )
}