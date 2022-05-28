import React, { useState, useEffect, useRef } from 'react';
import { Typography, Divider, Box, Stack, IconButton, Alert} from "@mui/material"
import { Lock } from '@mui/icons-material';
import _ from 'lodash'

import { MOVEMENT_TYPES, DAMAGE_TYPES, CONDITIONS, SENSES } from '../../constants.js';
import * as fmt from '../../libs/creature_format.js'
import { HighlightText } from './FormFields.jsx';
import RaceTypeAlignmentField from './RaceTypeAlignmentField.jsx';
import HPField from './HPField.jsx';
import ACField from './ACField.jsx';
import DistanceField from './DistanceField.jsx';
import SkillsField from './SkillsField_old.jsx';
import AttrTable from './AttrTable.jsx';
import ImmVulnField from './ImmVulnField.jsx'
import FeaturesField from './FeaturesField.jsx';
import LanguagesField from './LanguageField.jsx';
import ActionField from './ActionField.jsx';
import ChallengeField from './ChallengeField.jsx';
import { LockOpen } from '@mui/icons-material';

function Statblock( { statblock, style, allowEdit=false, defaultEdit=false, splitLength=3000 }) {

  const [numColumns, setNumColumns] = useState(1);
  const [editable, setEditable] = useState(allowEdit)
  const [sb, setStatblock] = useState(statblock);
  const ref = useRef(null)

  const updateColumns = () => {
    if (statblock) {
      const width = ref.current ? ref.current.offsetWidth : 0
      console.log(width)
      setStatblock(JSON.parse(JSON.stringify(statblock)))
      if (width > 800) {
        setNumColumns(JSON.stringify(statblock).length > splitLength ? 2 : 1)
      } else {
        setNumColumns(1)
      }
    }
  }

  useEffect(() => {
      updateColumns()
  }, [statblock, ref])

  useEffect(() => {
    setEditable(defaultEdit)
  },[statblock])

  const resetFunc = (field) => (fieldResetFunc) => {
    const newStatblock = {...sb}
    newStatblock[field] = fieldResetFunc(statblock)
    setStatblock(newStatblock)
  }

 

  useEffect(() => {
    let timeoutId = null;
    const resizeListener = () => {
      // prevent execution of previous setTimeout
      clearTimeout(timeoutId);
      // change width from the state object after 150 milliseconds
      timeoutId = setTimeout(() => updateColumns(), 150);
    };
    window.addEventListener('resize', resizeListener)  

    return () => {
      window.removeEventListener("resize", resizeListener)
    }
  }, [])

  console.log(statblock)
  console.log("errors", statblock?.errors)
  if (Object.keys(statblock?.errors)?.length > 0) {
    const k = Object.keys(statblock.errors)[0]
    console.log(k)
    console.log("test", _.get(statblock, statblock.errors[k].key))
  }

  console.log("action", _.get(statblock, "action[0]"))

  return (
  <Stack spacing={1} ref={ref}>
    {Object.keys(statblock?.errors)?.map(k =>
        statblock?.errors[k]?.map(e => {
          let title = k
          if (k === "action" || k === "features") {
            title = `${k[0].toUpperCase()}${k.slice(1)} - ${_.get(statblock, e.key).title}`
          }
          return (
            <Alert severity="warning">
              <Typography variant="statblock">
                {`Unexpected error in ${title}: ${e.error} - ${e.detail}`}
              </Typography>
            </Alert>)
        })
    )}
    <Box sx ={{display:"flex", flexDirection:"row", justifyContent:"space-between"}}>
      <Stack style={{width:"100%", padding:2, display:"flex", flexDirection:"column", ...style}} >
                  <HighlightText sx={{m:0}} color="primary.main" editable={editable} variant="statblockTitle" suppressContentEditableWarning={editable} contentEditable={editable}>{statblock?.name}</HighlightText>
                  <RaceTypeAlignmentField editable={editable} statblock={sb} setStatblock={setStatblock} />
      </Stack>
      {allowEdit ? <IconButton onClick={() => setEditable(!editable)}>{editable ? <LockOpen sx={{fontSize:40, color:"primary.light"}} /> : <Lock sx={{fontSize:40, color:"primary.light"}}/>}</IconButton> : <></>}
      </Box>
      <Divider sx={{width:1}}/>
      <Box style={{columnCount:numColumns, width:"100%", padding:2, ...style}} >
          {sb ?<>
          <ACField editable={editable}  statblock={sb} setStatblock={setStatblock} resetFunc={resetFunc("ac")} width={400}/>
          <HPField editable={editable}  statblock={sb} setStatblock={setStatblock} resetFunc={resetFunc("hp")}/>
          <DistanceField editable={editable} statblock={sb} setStatblock={setStatblock} title="speed" 
                          text="Speed" singular="Speed" fmt_func={fmt.format_speed} 
                          min_items={1}
                          options={MOVEMENT_TYPES} default_options={{type:"walk",distance:"30",measure:"ft"}} resetFunc={resetFunc("speed")} />
          <Divider  sx={{marginTop:1}}/>
          <AttrTable editable={editable} statblock={sb} setStatblock={setStatblock} resetFunc={resetFunc("abilities")}/>
          <Divider  sx={{marginBottom:1}}/>
          <SkillsField editable={editable}  statblock={sb} setStatblock={setStatblock} resetFunc={resetFunc("skills")}/>
          <ImmVulnField statblock={sb} setStatblock={setStatblock} options={DAMAGE_TYPES} 
                        title_text="Resistances" title="resistances" 
                        fmt_func={fmt.format_resistances} editable={editable} resetFunc={resetFunc}/>
          <ImmVulnField statblock={sb} setStatblock={setStatblock} options={DAMAGE_TYPES} 
                        title_text="Damage Immunities" title="damage_immunities" 
                        fmt_func={fmt.format_damage_immunities} editable={editable} resetFunc={resetFunc} />
          <ImmVulnField statblock={sb} setStatblock={setStatblock} options={CONDITIONS} 
                        title_text="Condition Immunities" title="condition_immunities" 
                        fmt_func={fmt.format_condition_immunities} editable={editable} resetFunc={resetFunc}/>
          <ImmVulnField statblock={sb} setStatblock={setStatblock} options={DAMAGE_TYPES} 
                        title_text="Vulnerabilities" title="vulnerabilities" 
                        fmt_func={fmt.format_vulnerabilities} editable={editable} resetFunc={resetFunc} />
          <DistanceField statblock={sb} setStatblock={setStatblock} title="senses" 
                          text="Senses" singular="Sense" fmt_func={fmt.format_senses} 
                          options={SENSES} default_options={{type:"darkvision",distance:"60",measure:"ft"}} editable={editable} resetFunc={resetFunc("senses")}/>
          <LanguagesField statblock={sb} setStatblock={setStatblock} editable={editable} resetFunc={resetFunc("languages")}/>
          <ChallengeField statblock={sb} setStatblock={setStatblock} editable={editable} resetFunc={resetFunc("cr")}/>
          <div style={{marginTop:10}} />
          <FeaturesField statblock={sb} setStatblock={setStatblock} editable={editable}  resetFunc={resetFunc}/>
          <ActionField statblock={sb} setStatblock={setStatblock} editable={editable} resetFunc={resetFunc}/>
          <div style={{marginTop:10}} />
          <Typography align="right" variant="subtitle2" sx={{margin:1}}><i>Source: {statblock.source.title}, pg.{statblock.source.page}</i></Typography>
          </>
        : <>{console.log("No creature")}</>}
      </Box>
      </Stack>
  );
}

export default Statblock;
