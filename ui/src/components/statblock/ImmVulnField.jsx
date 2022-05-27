import { Button, Paper } from "@mui/material"
import { StyledTextField, StyledDropdown } from './FormFields.jsx';
import PoppableField from "./PoppableField.jsx";

import { Delete } from '@mui/icons-material';
import { Add } from '@mui/icons-material';


export default function ImmVulnField({ statblock, setStatblock, options, title_text, title, fmt_func, editable }) {
  const setField = (field, i, j=null) => (event) => {
    console.log("setfield")
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
    console.log("addentry")
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
    console.log("removeentry")
    setStatblock(s => {
      const val = s[title]
      val.splice(i, 1);
      const newS = {...s}
      newS[title] = val
      return newS
    });
  }

  const addType = (i) => () => {
    console.log("addtype")
    setStatblock(s => {
      let val = s[title]
      if (val) {
        val[i].type.push("")
      }
      const newS = {...s}
      newS[title] = val
      console.log("news", newS)
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

  return(
    <PoppableField editable={editable} text={<><b>{title_text}</b> {fmt_func(statblock)}</>}>
        { statblock && statblock[title] ? statblock[title].map((val, i) => {
          return (
            <Paper key={`${title}-set-value-${i}`} square variant="outlined" 
                  sx={{padding:1, flexDirection:"column", display:"flex", mb:1}}>
              <StyledTextField label="Pre-text" value={val.pre_text} 
                                onChange={setField("pre_text", i)}/>
              <StyledDropdown id={`condition-dropdown-${i}-0`} label="Type" 
                value={val.type[0]} onChange={setField("type", i, 0)} options={options} />
              { val.type.length > 1 ? 
                val.type.slice(1).map((v,j) => (
                  <StyledDropdown id={`condition-dropdown-${i}-${j+1}`} label="Type" 
                    value={v} 
                    onChange={setField("type", i, j+1)} 
                    options={options}
                    textFieldProps = {{
                      endButton:<Delete />,
                      onEndButtonClick:removeType(i,j+1)
                    }}
                 />
                )) : <></>
              }
              <Button startIcon={<Add />} onClick={addType(i)}>Add Type</Button>
              <StyledTextField label="Post-text" value={val.post_text} onChange={setField("post_text", i)} />
              <Button startIcon={<Delete />} onClick={removeEntry(i)}>Remove {title_text}</Button>
            </Paper>
          )
        } ) : <></> }
        <Button startIcon={<Add />} onClick={addEntry}>Add {title_text}</Button>
    </PoppableField>
  )
}