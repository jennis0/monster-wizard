import React, { useState } from 'react';
import { Popper, Paper, Button, Stack, Typography, Divider } from "@mui/material"

import { HighlightText } from './FormFields.jsx';
import { Restore, AutoFixHigh } from '@mui/icons-material';
import { Close } from '@mui/icons-material';

export default function PoppableField( {children, text, textProps, hide=false, editable=true, onReset=null, onGenerate=null} ) {
    const [open, setOpen] = useState(null);   
  
    const handleClick = (event) => {
      setOpen(open ? false : true);
    }

    let justify="space-between"
    if (onGenerate !== null && onReset === null) {
      justify="right"
    }
  
    return (
      <>
        {!(hide === true) ? <HighlightText editable={editable} {...textProps} onClick={editable ? handleClick : null}>{text}</HighlightText> : <></>}
        {open ?
                   <> 
          <Divider sx={{mt:1, mb:0}}/>
          <Stack spacing={0.} width="100%" sx={{backgroundColor:"primary.", p:1, m:0}}>
            <Stack direction="row" sx={{justifyItems:justify, pt:0, pb:0}}>
              {onReset && <Button onClick={onReset} startIcon={<Restore />} sx={{p:1, mt:-0.5}}>Reset</Button>}
              {onGenerate && <Button onClick={onGenerate} startIcon={<AutoFixHigh />} sx={{p:1, pt:0}}>Generate Effects</Button>}
            </Stack>
              
              {children}
              <Button 
                sx={{m:0, alignSelf:"end", textAlign:"right", ml:31}} 
                onClick={() => setOpen(null)}
                startIcon={<Close />}
              >
                  Close
              </Button>
              
              </Stack>
              <Divider sx={{mb:1, mt:0}}/> </>
               : <></>}
        </>
    )
  }