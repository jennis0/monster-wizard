import { FormGroup  } from "@mui/material"
import { StyledTextField } from './FormFields.jsx';
import PoppableField from "./PoppableField.jsx";

import * as fmt from '../../libs/creature_format.js'

export default function HPField( { statblock, setStatblock, editable }) {
    const setHP = (field) => (e) => {
      setStatblock(s => {
        const hp = s.hp
        s.hp[field] = e.target.value
        return {...s, hp:hp}
      })
    }
  
    return (
      <PoppableField editable={editable} text={<><b>Hit Points</b> {fmt.format_hp(statblock)}</>}>
        <FormGroup sx={{p:0, m:0, mb:-2.5}}>
        <StyledTextField 
          label="HP Average" 
          value={statblock.hp?.average} 
          onChange={setHP("average")}
          validate={(v) => Number.isInteger(Number(v))}
          number
        />
        <StyledTextField label="HP Formula" value={statblock.hp?.formula} onChange={setHP("formula")} />
        </FormGroup>
      </PoppableField>
    )
  }