import React from 'react'
import { Box, CircularProgress, Typography, Paper, Button, IconButton, Tooltip, LinearProgress } from "@mui/material"
import { Stack } from '@mui/material';
import { Cancel, CancelOutlined, CheckCircleOutline, Replay } from '@mui/icons-material';
import { db, deleteUpload } from '../libs/db';

function CircularProgressWithLabel(props) {
    return (
      <Box sx={{ position: 'relative', display: 'inline-flex' }}>
        <CircularProgress size={100} variant={props.value >= 0 ? "determinate" : "indeterminate"} value={props.value}/>
        <Box
          sx={{
            top: 0,
            left: 0,
            bottom: 0,
            right: 0,
            position: 'absolute',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            p:2
          }}
        >
          <Typography variant="h6" component="div" color="text.secondary">
            {props.value >= 0 ? `${Math.round(props.value)}%`: ""}
          </Typography>
        </Box>
      </Box>
    );
  }

export function ImportProgress ( {upload} ) {

  const onCancel = (e) => {
    deleteUpload(upload.id)
    e.stopPropagation()
    e.preventDefault()
  }

  const error = upload.status === "error"
  const stage_progress = 100* upload.progress[0] / upload.progress[1]

  return (
    <Box sx={{w:"100%"}}>
      <Box sx={{w:"100%", justifyContent:"space-between", display:"flex", flexDirection:"row", alignItems:"center"}}>
        <Typography fontFamily="Scaly Sans" fontSize={12}>{STAGE_TEXT_MAP[upload.status]}</Typography>
        <Typography fontFamily="Scaly Sans" fontSize={12}>{`File: ${upload.file_progress[0]}/${upload.file_progress[1]}`}</Typography>
        <Tooltip title="Cancel import">
          <IconButton sx={{mt:-2}} onClick={onCancel}>
            <CancelOutlined sx={{color:"background.default"}}/>
          </IconButton>
        </Tooltip>
      </Box>
      <LinearProgress value={stage_progress} color={error ? "secondary" : "success"} variant="determinate" />
    </Box>
  )
}
  

  
  const STAGE_TEXT_MAP = {
      "file_upload":"Uploading File...",
      "text_extraction":"Extracting text from file..",
      "finding_statblock_text":"Searching for statblocks...",
      "joining_partial_statblocks":"Joining partial statblocks...",
      "processing_statblocks":"Processing final statblocks...",
      "finished":"Finished",
      "error":"Error"

  }

export default function Loader( {state, setState} ) {
  return (
      <Stack sx={{alignItems:"center", p:2, m:2, textAlign:"center", mt:"30%"}}>
        { state.state != "error" ? <>
        <Stack sx={{alignItems:"center", textAlign:"center"}} >
          <CircularProgressWithLabel 
              value={state?.progress ? 100*state.progress[0] / state.progress[1]: null} />
          <Typography sx={{p:2}} variant="h6">{STAGE_TEXT_MAP[state.state]}</Typography> 
        </Stack>
          </>
          :
          <Paper square sx={{p:1}}>
          <Stack sx={{p:1}}>
            <Typography variant="h6">Processing Error</Typography>

              {state.errors.slice(0,1).map(e => (<Typography sx={{p:1}}><b>Reason:</b> {e}</Typography>)) }
              <Button onClick={() => setState(null)} startIcon={<Replay />}>Return to Upload Page</Button>
            </Stack>
          </Paper>
        }
      </Stack>
  )
}