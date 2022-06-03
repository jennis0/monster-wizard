import React, { useState, useEffect } from 'react';
import { FormGroup, Typography, Button, Grid } from "@mui/material"

import { LANGUAGES } from '../../constants.js';


import { StyledDropdown, StyledTextField } from './FormFields.jsx';
import PoppableField from "./PoppableField.jsx";


import * as fmt from '../../libs/creature_format.js'
import { Add } from '@mui/icons-material';
import { Delete } from '@mui/icons-material';
import EditBlock from './EditBlock.jsx';


export default function LanguagesField( {statblock, setStatblock, editable=true, resetFunc }) {

    const onAddLanguage = (i) => () => {
    setStatblock(s =>{
      const languages = s.languages
      languages.splice(i+1, 0, "Common")
      return {...s, languages:languages}
    })
  }

  const onDeleteLanguage = (i) => (event) => {
    setStatblock(s => {
        const languages = s.languages
        languages.splice(i, 1)
        return {...s, languages:languages}
    })
  }

  const onSetLanguage = (i) => (event) => {
    setStatblock(s => {
      const languages = s.languages
      languages[i] = event.target.value;
      return {...s, languages:languages}
    })

  }

  const onReset = () => {
    resetFunc((sb) => {
      return sb.languages
    })
  }

  return ( 
    <PoppableField editable={editable} text={<><b>Languages</b> {fmt.format_languages(statblock)}</>} 
                    hide={!editable && !statblock?.languages?.length > 0} onReset={onReset}>
        <EditBlock title="Languages">
        {statblock.languages?.map((lg, i) => (
          <Grid item xs={12}>
            <StyledTextField 
                label="Language" 
                value={lg}
                onChange={onSetLanguage(i)} 
                endButton={[<Add />, <Delete />]} 
                onEndButtonClick={[onAddLanguage(i), onDeleteLanguage(i)]}
             />
          </Grid>
        ))}
        </EditBlock>
      </PoppableField>
  );
} 