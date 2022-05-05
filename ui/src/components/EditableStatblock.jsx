import React, { useState, useRef, useEffect, useContext } from 'react';
import { FormGroup, FormControlLabel, Paper, Popper, Typography, Divider, Table, TableHead, TableBody, TableRow, TableCell, FormControl, Checkbox, TextField, styled, DialogTitle, DialogContent, Button, DialogActions, MenuItem } from "@mui/material"

import { TYPES, PLURAL_TYPES, SIZES } from '../constants.js';

import { LocalContext } from '../libs/store.js';

import * as fmt from '../libs/creature_format.js'


function AttrTable(attrs) {
  return (
      <Table sx={{ minWidth: 200, leftMargin:2, rightMargin:2 }} aria-label="attribute scores" size="small">
        <TableHead>
          <TableRow>
            {["STR", "DEX", "CON", "INT", "WIS", "CHA"].map(a => {
              return <TableCell align="center"><b>{a}</b></TableCell>
            })}
          </TableRow>
        </TableHead>
        <TableBody>
            <TableRow
              key={"attributes"}
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
              {attrs.children.map(a => {
                return (<TableCell align="center"><b>{a}</b></TableCell>)
              })}
            </TableRow>
        </TableBody>
      </Table>
  );
}

const HighlightText = styled(Typography)(({theme}) => (
  {"&:hover": 
    {
    backgroundColor: "#4363EA",
    color: "#FFF !important"
    },
  }
  )
);

function OptTypography (props) {
  return (
    props.statblock[props.label] ? <Typography>{props.children}</Typography> : <></>
  )
}

function RaceTypeAlignmentField({ statblock, setStatblock }) {
  const [anchorEl, setAnchorEl] = useState(null);   
  const [isSwarm, setIsSwarm] = useState(null)

  const handleClick = (event) => {
    setAnchorEl(anchorEl ? null : event.currentTarget);
  }

  const setSize = (event) => {
    setStatblock((s) => ({...s, size:[event.target.value]}))
  }

  const setType = (event) => {
    setStatblock((s) => {return {...s, creature_type:{swarm:false, type:[event.target.value]}}})
  }
  
  const setSwarm = (event) => {
    setStatblock(s => ({...s, creature_type:{...s.creature_type, swarm:{...s.creature_type.swarm, swarm:event.target.checked}}}))
  }

  const setSwarmSize = (event) => {
    console.log(event.target.value)
    const ss = event.target.value !== '-' ? event.target.value : null;
    console.log(ss);
    setStatblock(s=> ({...s, creature_type:{...s.creature_type, swarm:{swarm:true, swarm_size:ss}}}))
  }

  const setAlignment = (event) => {
    setStatblock(s => s.alignment=event.target.value);
  }

  useEffect(() => {
    if (statblock) {
      setIsSwarm(statblock.creature_type.swarm)
    }
  }, [statblock])

  const LabelledDropdown = ({ label, value, onChange, options }) => (
      <FormControlLabel sx={{alignContent:"left", justifyContent:"left"}} label={label} labelPlacement="start" control={
        <TextField select variant="filled" value={value} onChange={onChange} style={{ paddingLeft: '20px', width: "150px" }}>
          {options.map((s) => (
            <MenuItem key={`${label}-${s}`} value={s}>{s[0].toUpperCase() + s.substring(1)}</MenuItem>
          ))}
        </TextField>}
      />
  )

  const LabelledTextField = ({ label, value, onChange }) => (
    <FormControlLabel sx={{alignContent:"left", justifyContent:"left"}} label={label} labelPlacement="start" control={
      <TextField variant="filled" value={value} onChange={value} style={{ paddingLeft: '20px', width: "150px" }} />
    }
    />
  )


  const dialog = (statblock) => (
    <>
    <Typography variant="h6">Set Size, Type & Alignment</Typography>
    <FormControl>
      <LabelledDropdown label="Size" value={statblock?.size} onChange={setSize} options={SIZES} />
      <FormGroup>
        <FormControlLabel sx={{alignContent:"left", justifyContent:"left"}} labelPlacement="start" control={<Checkbox value={isSwarm} onChange={setSwarm} />} label="Swarm" />
        {isSwarm ? <LabelledDropdown label="Swarm Size" value={statblock?.creature_type.swarm?.swarm_size} onChange={setSwarmSize} options={["-"].concat(SIZES)} /> : <></>}
        <LabelledDropdown label="Type" value={statblock?.creature_type.type} onChange={setType} options={TYPES} />
      </FormGroup>
      <LabelledTextField label="Alignment" value={statblock?.alignment} onChange={setAlignment} />
    </FormControl>
    </>
  );

  return (
    <>
    <HighlightText variant="subtitle2" onClick={handleClick}><i>{fmt.format_race_type_alignment(statblock)}</i></HighlightText>
    <Popper
      open={Boolean(anchorEl)}
      anchorEl={anchorEl}
      placement="bottom-start"
    >
      <Paper square={true} sx={{padding:2}}>{dialog(statblock)}</Paper>
    </Popper>
    </>
  )
}

function Statblock( { statblock, style }) {

  const [numColumns, setNumColumns] = useState(1);
  const [sb, setStatblock] = useState(statblock);

  useEffect(() => {
    setStatblock(statblock)
  }, [statblock])

  console.log("sb", sb)

  return (
      <div style={{columnCount: {numColumns}, width:"60vw", padding:2, ...style}} >
          {sb ? <div>
          <HighlightText variant="h5" suppressContentEditableWarning={true} contentEditable={true}>{statblock.name}</HighlightText>
          <RaceTypeAlignmentField statblock={sb} setStatblock={setStatblock} />
          <Divider sx={{marginTop:1, marginBottom:1}}/>
          <Typography><b>Armor Class</b> {fmt.format_ac(statblock)}</Typography>
          <Typography><b>Hit Points</b> {fmt.format_hp(statblock)}</Typography>
          <Typography><b>Speed</b> {fmt.format_speed(statblock)}</Typography>
          <Divider  sx={{marginTop:1}}/>
          <AttrTable>{fmt.format_attributes(statblock)}</AttrTable>
          <Divider  sx={{marginBottom:1}}/>
          <OptTypography label="skills" statblock={statblock}><b>Skills</b> {fmt.format_skills(statblock)}</OptTypography>
          <OptTypography label="resistances" statblock={statblock}><b>Resistances</b> {fmt.format_resistances(statblock)}</OptTypography>
          <OptTypography label="damage_immunities" statblock={statblock}><b>Damage Immunities</b> {fmt.format_damage_immunities(statblock)}</OptTypography>
          <OptTypography label="condition_immunities" statblock={statblock}><b>Condition Immunities</b> {fmt.format_condition_immunities(statblock)}</OptTypography>
          <OptTypography label="vulnerabilities" statblock={statblock}><b>Vulnerabilities</b> {fmt.format_vulnerabilities(statblock)}</OptTypography>
          <OptTypography label="senses" statblock={statblock}><b>Senses</b> {fmt.format_senses(statblock)}</OptTypography>
          <OptTypography label="languages" statblock={statblock}><b>Languages</b> {fmt.format_languages(statblock)}</OptTypography>
          <Typography><b>Challenge</b> {fmt.format_cr(statblock)}</Typography>
          <Divider sx={{marginTop:1, marginBottom:1}}/>
          {statblock.features?.map(f => fmt.format_feature(f))}
          {["action", "reaction", "legendary"].map(a => fmt.format_action_block(statblock, a))}
          <div style={{marginTop:10}} />
          <Typography align="right" variant="subtitle2" sx={{margin:1}}><i>Source: {statblock.source.title}, pg.{statblock.source.page}</i></Typography>
        </div>
        : <>{console.log("No creature")}</>}
      </div>
  );
}

export default Statblock;
