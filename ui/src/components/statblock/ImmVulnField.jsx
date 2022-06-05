import { Button, Grid } from "@mui/material"
import { StyledTextField, StyledDropdown } from '../FormFields.jsx';
import PoppableField from "./PoppableField.jsx";

import { Delete } from '@mui/icons-material';
import { Add } from '@mui/icons-material';
import EditBlock from "./EditBlock.jsx";


export default function ImmVulnField({ statblock, setStatblock, options, title_text, title, singular, fmt_func, editable, resetFunc }) {
  const setField = (field, i, j=null) => (event) => {
    setStatblock(s => {
      const val = s[title]
      if (field === "type") {
        val[i][field][j] = event.target.value
      } else{
        val[i][field] = event.target.value
      } 
      const newS = {...s}
      newS[title] = val
      return newS
    })
  }

  const addEntry = () => {
    setStatblock(s => {
      let val = s[title]
      if (val === null || val === undefined) {
        val = []
      }
      val.push({pre_text:"", type:[], post_text:""})
      const newS = {...s}
      newS[title] = val
      return newS
    })
  }

  const removeEntry = (i) => () => {
    setStatblock(s => {
      const val = s[title]
      val.splice(i, 1);
      const newS = {...s}
      newS[title] = val
      return newS
    });
  }

  const addType = (i, j) => () => {
    setStatblock(s => {
      let val = s[title]
      if (val) {
        if (val[i].type) {
          val[i].type.splice(j+1, 0, "")
        } else {
          val[i].type = [""]
        }
      }
      const newS = {...s}
      newS[title] = val
      return newS
    })
  }

  const removeType = (i, j) => () => {
    setStatblock(s => {
      let val = s[title]
      val[i].type.splice(j, 1)
      const newS = {...s}
      newS[title] = val
      return newS
    })
  }

  const applyReset = () => {
    resetFunc((sb) => {
      return sb[title]
    })
  }

  return(
    <PoppableField editable={editable} text={<><b>{title_text}</b> {fmt_func(statblock)}</>} onReset={applyReset}>
        { statblock && statblock[title] && statblock[title].length > 0 ? statblock[title].map((val, i) => {
          return (
            <EditBlock title={singular} onAdd={addEntry} onDelete={removeEntry(i)} key={`immvun-field-${i}`}>
              <Grid item xs={12}>
                <StyledTextField label="Pre-text" value={val.pre_text} 
                                  onChange={setField("pre_text", i)}/>
              </Grid>
              {val.type.map((v,j) => (
                  <Grid item xs={12} xl={12} key={`cond-dropdown-${i}-${j}`}>
                  <StyledDropdown id={`condition-dropdown-${i}-${j}`} label="Type" 
                    value={v} 
                    short
                    onChange={setField("type", i, j)} 
                    options={options}
                    textFieldProps = {{
                      endButton:[<Add />, <Delete />],
                      onEndButtonClick:[addType(i, j), removeType(i,j)]
                    }}
                 />
                 </Grid>
                ))
              }
              {val.type.length === 0 ?
              <Grid container item xs={12} justifyContent="flex-end">
                <Grid item xs={12}>
                  <Button 
                    endIcon={<Add />} 
                    onClick={(addType(i, 0))} 
                    sx={{width:"100%", height:"40px"}}
                  >
                    {`Add ${singular} Type`}
                  </Button>
                </Grid>
                </Grid>
                
              : <></>}
              <Grid item xs={12}>
                <StyledTextField label="Post-text" value={val.post_text} onChange={setField("post_text", i)} />
              </Grid>
            </EditBlock>
          )
        } ) : 
        <EditBlock title={singular} onAdd={addEntry} onDelete={null} first={true} />
       }
    </PoppableField>
  )
}