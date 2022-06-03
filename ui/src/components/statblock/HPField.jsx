import { Grid  } from "@mui/material"
import { StyledTextField } from './FormFields.jsx';
import PoppableField from "./PoppableField.jsx";

import * as fmt from '../../libs/creature_format.js'
import EditBlock from "./EditBlock.jsx";

export default function HPField( { statblock, setStatblock, editable, resetFunc }) {
    const setHP = (field) => (e) => {
      setStatblock(s => {
        const hp = s.hp
        s.hp[field] = e.target.value
        return {...s, hp:hp}
      })
    }

    const applyReset = () => (
      resetFunc((sb) => {
        return sb.hp
      })
    )
  
    return (
      <PoppableField editable={editable} text={<><b>Hit Points</b> {fmt.format_hp(statblock)}</>} onReset={applyReset}>
        <EditBlock title="Hit Points">
          <Grid item xs={12}>
            <StyledTextField 
              label="HP Average" 
              value={statblock.hp?.average} 
              onChange={setHP("average")}
              validate={(v) => Number.isInteger(Number(v))}
              number
            />
          </Grid>
          <Grid item xs={12}>
            <StyledTextField label="HP Formula" value={statblock.hp?.formula} onChange={setHP("formula")} />
          </Grid>
        </EditBlock>
      </PoppableField>
    )
  }