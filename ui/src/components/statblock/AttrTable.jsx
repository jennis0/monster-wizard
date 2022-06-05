import React, { useState } from 'react';
import { Typography, Table, TableHead, TableBody, TableRow, Button, Popper, Paper, Box, Divider, Stack } from "@mui/material"
import { Close, Restore } from '@mui/icons-material';
import TableCell, { tableCellClasses } from "@mui/material/TableCell";
import {SHORT_ABILITIES} from '../../constants.js';
import { StyledTextField } from '../FormFields.jsx';

import * as fmt from '../../libs/creature_format.js'

function AttrTableValue( {statblock, editable, handleClick }) {

  const attrs = fmt.attributes_to_modifiers(statblock);

  const sx = {leftMargin:2, rightMargin:2, width:"100%",
     "&:hover": editable ? 
            {
            backgroundColor: "primary.light",
            color: "primary.contrastText"
            } : null,
    [`& .${tableCellClasses.root}`]: {
                borderBottom: "none",
              }
    }

  return  (
    <Table sx={sx} aria-label="attribute scores" size="small" onClick={editable ? handleClick : null}>
    <TableHead>
      <TableRow key={"attrtitle"}>
        {SHORT_ABILITIES.map(a => {
          return <TableCell sx={{p:1, m:0, pb:0, pt:1.5}} key={`attr-title-${a}`} align="center"><Typography variant="statblock"><b>{a.toUpperCase()}</b></Typography></TableCell>
        })}
      </TableRow>
    </TableHead>
    <TableBody>
        <TableRow
          key={"attributes"}
          sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
          {SHORT_ABILITIES.map((a,i) => {
            return (<TableCell sx={{p:1, pt:0.5, pb:1.5}} key={`attr-value-${a}`} align="center">
              <Typography variant="statblockTable">{attrs[i]}</Typography>
              </TableCell>)
          })}
        </TableRow>
    </TableBody>
  </Table>
  )
}

export default function AttrTable( {statblock, setStatblock, editable, onReset} ) {
  const [anchorEl, setAnchorEl] = useState(null);  
  const [open, setOpen] = useState(false); 

  const handleClick = () => {
    setOpen(!open)
  }

  const onChange = (attr) => (event) => {
    setStatblock(s => {
      const newS = {...s}
      newS.abilities[attr] = Number(event.target.value)
      return newS;
    }
      )
  }

  return (<>
    <AttrTableValue statblock={statblock} editable={editable} handleClick={handleClick} />
    {open ? 
    <> 
      <Divider sx={{mt:1, mb:0}}/>
      <Stack spacing={0.} width="100%" sx={{backgroundColor:"primary.", p:1, m:0}}>
        <Stack direction="row" sx={{justifyItems:"left", pt:0, pb:0}}>
          {onReset && <Button onClick={onReset} startIcon={<Restore />} sx={{p:1, mt:-0.5}}>Reset</Button>}
        </Stack> 
        <Box square={true} sx={{padding:1, width:"100%", display:"flex", flexDirection:"column"}}>
          <Box sx={{width:"100%", columnCount:2, m:0, p:0}}>
            {SHORT_ABILITIES.map((a, i) => {
              return (<StyledTextField key={`attr-set-value-${a}`} label={a.toUpperCase()} short width={130} value={statblock.abilities && statblock.abilities[a] ? statblock.abilities[a] : "-"} onChange={onChange(a)} number/>);
            })}
          </Box>
        </Box>
        <Button 
          sx={{m:0, alignSelf:"end", textAlign:"right", ml:31}} 
          onClick={() => setOpen(null)}
          startIcon={<Close />}
        >
            Close
        </Button>
      </Stack>
    </>
      : <></>}
        </>
);
}