import { Button, Paper } from "@mui/material"
import { Add, Delete } from '@mui/icons-material';

import { MEASURES } from '../../constants.js';
import { StyledTextField, StyledDropdown} from './FormFields.jsx';
import PoppableField from "./PoppableField.jsx";


export default function DistanceField( { statblock, setStatblock, title, editable, text, options, fmt_func, default_option, singular, min_items=0}) {

    const addEntry = () => {
      setStatblock(s => {
        const val = s[title];
        val.push(default_option)
        const newS = {...s}
        newS[title] = val;
        return newS
      })
    }
  
    const removeEntry = (i) => () => {
      setStatblock(s => {
        const val = s[title];
        val.splice(i, 1);
        const newS = {...s}
        newS[title] = val;
        return newS
      });
    }
  
    const setField = (field, i) => (event) => {
      setStatblock(s => {
        const val = s[title];
        val[i][field] = event.target.value
        const newS = {...s}
        newS[title] = val;
        return newS
      })
    }
  
    return (
      <PoppableField editable={editable} text={<><b>{text}</b> {fmt_func(statblock)}</>} >
        {statblock && statblock[title] ? statblock[title].map((s,i) => 
            (<><Paper key={`distance-${title}-set-value-${i}`} square variant="outlined" 
                      sx={{padding:1, flexDirection:"column", display:"flex", mb:1}}>
            <StyledDropdown value={s.type} options={options} label={"Type"} onChange={setField("type", i)} capitalise={false} />
            <StyledTextField label="Value" value={s.distance} onChange={setField("distance", i)} number />
            <StyledDropdown value={s.measure} options={MEASURES} label={"Measure"} capitalise={false} onChange={setField("measure", i)} />
            {i >= min_items ? <Button startIcon={<Delete />} onClick={removeEntry(i)}>Remove {singular}</Button> : <></>}
          </Paper>
          </>) 
        ) : <></> }
        <Button key={`${title}-add-button`} startIcon={<Add />} onClick={addEntry}>Add {singular}</Button>
      </PoppableField>
      
    )
  }
  