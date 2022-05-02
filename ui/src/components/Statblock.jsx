import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Paper, Typography, Divider, Table, TableHead, TableBody, TableRow, TableCell } from "@mui/material"

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

function OptTypography (props) {
  return (
    props.statblock[props.label] ? <Typography>{props.children}</Typography> : <></>
  )
}

function Statblock( { statblock, style }) {

  const [numColumns, setNumColumns] = useState(1);

  return (
      <div style={{columnCount: {numColumns}, width:"60vw", padding:2, ...style}} >
          {statblock ? <div>
          <Typography variant="h5">{statblock.name}</Typography>
          <Typography variant="subtitle2"><i>{fmt.format_race_type_alignment(statblock)}</i></Typography>
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
