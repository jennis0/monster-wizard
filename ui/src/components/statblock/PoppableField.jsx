import React, { useEffect, useState } from 'react';
import { Button, Stack, Divider, Box, Grid } from "@mui/material"

import { HighlightText } from './FormFields.jsx';
import { Restore, AutoFixHigh } from '@mui/icons-material';
import { Close } from '@mui/icons-material';

export default function PoppableField( {children, text, textProps, hide=false, editable=true, onReset=null, onGenerate=null} ) {
    const [open, setOpen] = useState(null);   

    useEffect(() => {
      setOpen(false)
    }, [editable])
  
    const handleClick = (event) => {
      setOpen(open ? false : true);
    }

    return (
      <Box sx={{breakInside:"avoid-column", p:0, m:0}}>
          <Grid container spacing={1} width="100%" sx={{width:"100%"}}>
            <Grid xs={12} item>
              {!(hide === true) ? <HighlightText editable={editable} {...textProps} onClick={editable ? handleClick : null}>{text}</HighlightText> : <></>}
            </Grid>
            {open ?
            <>
            <Grid item xs={12}>
              <Divider/>
            </Grid> 
            <Grid item xs={3} >
              {onReset && <Button onClick={onReset} startIcon={<Restore />} sx={{height:"30px", width:"100%", p:0}}>Reset</Button>}
            </Grid>
            <Grid item xs={4} />
            <Grid item xs={5}>
              {onGenerate && <Button onClick={onGenerate} sx={{width:"100%", height:"30px"}} endIcon={<AutoFixHigh />} >Generate Effects</Button>}
            </Grid>
            <Grid xs={12} item container spacing={1} sx={{width:"100%"}}>
                {children}
            </Grid>
            <Grid item xs={9} />
            <Grid item xs={3}>
              <Button 
                sx={{m:0, textAlign:"right", width:"100%", p:0}} 
                onClick={() => setOpen(null)}
                endIcon={<Close />}
              >
                  Close
              </Button>
            </Grid>
            <Grid xs={12}>
              <Divider sx={{mb:1, mt:1}}/>
            </Grid>
            </> : <></>}
          </Grid>
        </Box>
    )
  }