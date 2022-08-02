import { Button, Grid, Typography } from "@mui/material"
import { Add, Delete } from '@mui/icons-material';

import { MEASURES } from '../../constants.js';
import { StyledTextAndOptField, StyledDropdown} from '../FormFields.jsx';
import PoppableField from "./PoppableField.jsx";
import EditBlock from "./EditBlock.jsx";


export default function DistanceField( { statblock, setStatblock, title, editable, text, options, singular, fmt_func, default_option, resetFunc}) {

    const addEntry = () => {
      setStatblock(s => {
        let val = s[title];
        if (!val) {
          val = [default_option]
        } else {
          val.push(default_option)
        }
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

    const applyReset = () => (
      resetFunc((sb) => {
        return sb[title]
      })
    )
  
    return (
      <PoppableField editable={editable} text={<><b>{text}</b> {fmt_func(statblock)}</>} onReset={applyReset}>
          {statblock && statblock[title] && statblock[title].length > 0 ? statblock[title].map((s,i) => 
              (<EditBlock title={singular} onAdd={addEntry} onDelete={removeEntry(i)} first={false} key={`df-eb-${i}`}>
                <Grid item xs={6}>
                  <StyledDropdown short value={s.type} options={options} label={"Type"} onChange={setField("type", i)} capitalise={false} />
                </Grid>
                <Grid item xs={6}>
                  <StyledTextAndOptField short label="Value" 
                      textValue={s.distance} 
                      onTextChange={setField("distance", i)} 
                      options={MEASURES} 
                      selectValue={s.measure}
                      onSelectChange={setField("measure", i)}
                />
                </Grid>
              </EditBlock>) 
          ):
          <EditBlock title={singular} onAdd={addEntry} onDelete={null} first={true} />
          }
      </PoppableField>
      
    )
  }
  