import React, { useState, useEffect } from 'react';
import { FormGroup, Typography, Button } from "@mui/material"

import { LANGUAGES } from '../../constants.js';


import { StyledDropdown, StyledTextField } from './FormFields.jsx';
import PoppableField from "./PoppableField.jsx";


import * as fmt from '../../libs/creature_format.js'
import { Add } from '@mui/icons-material';
import { Delete } from '@mui/icons-material';


export default function LanguagesField( {statblock, setStatblock, editable=true }) {

    const onAddLanguage = () => {
    setStatblock(s =>{
      const languages = s.languages
      languages.push("Common")
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

  return ( 
    <PoppableField editable={editable} text={<><b>Languages</b> {fmt.format_languages(statblock)}</>} hide={!editable && !statblock?.languages?.length > 0}>
      <FormGroup sx={{marginBottom:-4}}>
        <Typography variant="h6">Languages</Typography>
        {statblock.languages?.map((lg, i) => (
            <StyledTextField 
                label="Language" 
                value={lg}
                onChange={onSetLanguage(i)} 
                endButton={<Delete />} 
                onEndButtonClick={onDeleteLanguage(i)}
             />
        ))}
        <Button onClick={onAddLanguage}><Add />Add Language</Button>
      </FormGroup>
      </PoppableField>
  );
} 