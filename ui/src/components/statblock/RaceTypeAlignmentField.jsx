import { FormGroup,  FormControlLabel,  Checkbox,  } from "@mui/material"
import { TYPES, SIZES,  } from '../../constants.js';
import { StyledTextField, StyledDropdown } from './FormFields.jsx';
import PoppableField from "./PoppableField.jsx";

import * as fmt from '../../libs/creature_format.js'

export default function RaceTypeAlignmentField({ statblock, setStatblock, editable, props }) {
    const setSize = (event) => {
      setStatblock((s) => ({...s, size:[event.target.value]}))
    }
  
    const setType = (event) => {
      setStatblock((s) => {return {...s, creature_type:{...s.creature_type, type:[event.target.value]}}})
    }
    
    const setSwarm = (event) => {
      setStatblock(s => ({...s, creature_type:{...s.creature_type, swarm:event.target.checked}}))
    }
  
    const setSwarmSize = (event) => {
      const ss = event.target.value !== '-' ? event.target.value : null;
      setStatblock(s=> ({...s, creature_type:{...s.creature_type, swarm:true, swarm_size:ss}}))
    }
  
    const setAlignment = (event) => {
      setStatblock(s => ({...s, alignment:event.target.value}));
    }
  
    return (
      <PoppableField editable={editable} textProps={{variant:"statblockRaceType"}} text={(<i>{fmt.format_race_type_alignment(statblock)}</i>)} {...props}>
          <FormGroup sx={{p:0, marginBottom:0}}>
            <StyledDropdown id="size-dropdown" label="Size" value={statblock?.size} onChange={setSize} options={SIZES} />
            <FormControlLabel sx={{alignContent:"left", justifyContent:"left"}} labelPlacement="start" control={<Checkbox checked={statblock?.creature_type?.swarm} onChange={setSwarm} />} label="Swarm" />
            {statblock?.creature_type?.swarm === true ? <StyledDropdown label="Swarm Size" value={statblock?.creature_type?.swarm_size ? statblock?.creature_type?.swarm_size : "-"} onChange={setSwarmSize} options={["-"].concat(SIZES)} /> : <></>}
            <StyledDropdown label="Type" value={statblock?.creature_type?.type} onChange={setType} options={TYPES} />
            <StyledTextField label="Alignment" value={statblock?.alignment} onChange={setAlignment} />
          </FormGroup>
      </PoppableField>  
    )
  }