import { Paper,Button, Box } from "@mui/material"

import { StyledTextField } from './FormFields.jsx';
import PoppableField from "./PoppableField.jsx";

import * as fmt from '../../libs/creature_format.js'
import { Delete } from '@mui/icons-material';
import { Add } from '@mui/icons-material';
import { Typography } from "@mui/material";

export default function ACField({ statblock, setStatblock, editable, resetFunc, width }) {
    const setACField = (field, i, j=null) => (event) => {
      setStatblock(s => {
        const ac = s.ac
        if (field === "from") {
          s.ac[i][field][j] = event.target.value
        } else {
          s.ac[i][field] = event.target.value
        }
        return {...s, ac:ac}
      })
    }
  
    const addACFrom = (i) => () => {
      setStatblock(s => {
        const ac = s.ac;
        ac[i].from.push("");
        return {...s, ac:ac}
      });
    }
  
    const removeACFrom = (i, j) => (event) => {
      setStatblock(s => {
        const ac = s.ac;
        ac[i].from.splice(j, 1);
        return {...s, ac:ac}
      });
    }
  
    const addAC = () => {
      setStatblock(s => {
        const ac = s.ac;
        ac.push({ac:10, from:[], condition:""})
        return {...s, ac:ac}
      })
    }
  
    const removeAC = (i) => () => {
      setStatblock(s => {
        const ac = s.ac;
        ac.splice(i, 1);
        return {...s, ac:ac}
      });
    }

    const applyReset = () => (
      resetFunc((sb) => {
        return sb.ac
      })
    )
  
    return(
      <PoppableField editable={editable} onReset={applyReset} text={<>
      <b>Armour Class</b> {fmt.format_ac(statblock)}</>} >
          {statblock?.ac?.map((ac, i) => 
            (<Box key={`ac-set-value-${i}`} 
              sx={{flexDirection:"column", display:"flex", mb:0, mt:0, width:"100%"}}
            >
              <StyledTextField label="AC" value={ac.ac} onChange={setACField("ac", i)} number/>
              <StyledTextField label="Conditions" value={ac.condition} onChange={setACField("condition", i)}/>
              {ac.from.map((f,j) =>
                (<StyledTextField key={`ac-set-value-${i}-from-${j}`} label="From" value={f}
                   onChange={setACField("from", i, j)} 
                   endButton={<Delete />}
                   onEndButtonClick={removeACFrom(i,j)} />)
              )}
              <Button 
                variant="contained"
                startIcon={<Add />} 
                onClick={(addACFrom(i))} 
                sx={{width:200, textAlign:"left"}}
              >
                Add AC Source
              </Button>
              {i > 0 ? 
              <Button 
                startIcon={<Delete />} 
                variant="contained"
                onClick={removeAC(i)}
                sx={{width:200, alignItems:"left"}}
              >Remove AC</Button> : <></>}
              </Box>
            )
          )}
          <Button variant="contained" startIcon={<Add />} sx={{width:200, textAlign:"left"}} onClick={addAC}>Add Armor Class</Button>
      </PoppableField>
    )
  }
  