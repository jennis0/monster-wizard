import { Paper,Button, Box, Grid, Divider, ButtonGroup, IconButton } from "@mui/material"

import { StyledTextField } from './FormFields.jsx';
import PoppableField from "./PoppableField.jsx";

import * as fmt from '../../libs/creature_format.js'
import { Delete } from '@mui/icons-material';
import { Add } from '@mui/icons-material';
import { Typography } from "@mui/material";
import EditBlock from "./EditBlock.jsx";

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
        <b>Armour Class</b> {fmt.format_ac(statblock)}</>} 
      >
          {statblock?.ac?.map((ac, i) => 
            (
            <EditBlock title="Armour Class" onAdd={addAC} onDelete={removeAC(i)} first={i === 0}>
              <Grid item xs={12} md={3}>
                <StyledTextField short label="AC" value={ac.ac} onChange={setACField("ac", i)} number/>
              </Grid>
              <Grid item xs={12} md={9}>
                <StyledTextField label="Condition" value={ac.condition} onChange={setACField("condition", i)}/>
              </Grid>
              {ac.from.map((f,j) =>
                (
                <Grid item xs={12}>
                  <StyledTextField key={`ac-set-value-${i}-from-${j}`} label="Source" value={f}
                    onChange={setACField("from", i, j)} 
                    endButton={[<Add />, <Delete />]}
                    onEndButtonClick={[addACFrom(i), removeACFrom(i,j)]} />
                </Grid>
                  )
              )}
              {ac.from.length === 0 ?
              <Grid container item xs={12} justifyContent="flex-end">
                <Grid item xs={4} >
                  <Button 
                    endIcon={<Add />} 
                    onClick={(addACFrom(i))} 
                    sx={{width:"100%"}}
                  >
                    Add Source
                  </Button>
                </Grid>
                </Grid>
                
              : <></>}
            </EditBlock>)
          )}
      </PoppableField>
    )
  }
  