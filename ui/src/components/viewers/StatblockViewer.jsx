import React, { useState, useEffect, useRef } from 'react';
import { Typography, Divider, Box, Stack, IconButton, Alert, Tooltip} from "@mui/material"
import { AddToPhotos, Lock, Restore, Save } from '@mui/icons-material';
import _ from 'lodash'

import { MOVEMENT_TYPES, DAMAGE_TYPES, CONDITIONS, SENSES } from '../../constants.js';
import * as fmt from '../../libs/creature_format.js'
import { HighlightText } from '../FormFields.jsx';
import RaceTypeAlignmentField from '../statblock/RaceTypeAlignmentField.jsx';
import HPField from '../statblock/HPField.jsx';
import ACField from '../statblock/ACField.jsx';
import DistanceField from '../statblock/DistanceField.jsx';
import SkillsField from '../statblock/SkillsField.jsx';
import AttrTable from '../statblock/AttrTable.jsx';
import ImmVulnField from '../statblock/ImmVulnField.jsx'
import FeaturesField from '../statblock/FeaturesField.jsx';
import LanguagesField from '../statblock/LanguageField.jsx';
import ActionField from '../statblock/ActionField.jsx';
import ChallengeField from '../statblock/ChallengeField.jsx';
import { LockOpen } from '@mui/icons-material';
import { updateStatblock } from '../../libs/db.js';

function StatblockViewer( { statblock, style, allowEdit=false, defaultEdit=false, splitLength=3000, onSave }) {

  const [numColumns, setNumColumns] = useState(1);
  const [editable, setEditable] = useState(allowEdit)
  const [sb, setStatblockWithoutEdit] = useState(null);
  const [edited, setEdited] = useState(false);
  const ref = useRef(null)

  const updateColumns = () => {
    if (statblock) {
      const width = ref.current ? ref.current.offsetWidth : 0
      setStatblockWithoutEdit(sb)
      if (width > 800) {
        setNumColumns(statblock.length > splitLength ? 2 : 1)
      } else {
        setNumColumns(1)
      }
    }
  }

  useEffect(() => {
      updateColumns()
  }, [statblock, ref])

  useEffect(() => {
    setStatblockWithoutEdit(statblock)
    setEditable(defaultEdit)
    setEdited(false)
  },[statblock])

  const resetFunc = (field) => (fieldResetFunc) => {
    const result = _.cloneDeep(fieldResetFunc(statblock))
    setStatblockWithoutEdit(s => {
      const newS = _.cloneDeep(s)
      newS[field] = result
      return newS
    })
  }

  const setStatblock = (sb, test) => {
    console.log("setting statblock")
    setEdited(true)
    setStatblockWithoutEdit(sb)
  }

  const save = () => {
    onSave(sb)
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
  if (Object.keys(statblock?.errors)?.length > 0) {
    const k = Object.keys(statblock.errors)[0]
  }


  return (
  <Stack spacing={1} ref={ref}>
    {Object.keys(statblock?.errors)?.map(k =>
        statblock?.errors[k]?.map((e,i) => {
          let title = k
          if (k === "action" || k === "features") {
            title = `${k[0].toUpperCase()}${k.slice(1)} - ${_.get(statblock, e.key).title}`
          }
          return (
            <Alert severity="warning" key={`alert-${k}-${i}`}>
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
      {allowEdit &&
        <Stack direction="row">
          <Tooltip title="Add to Collection">
            <IconButton>
              <AddToPhotos sx={{fontSize:30, color:"primary.light"}}/>
            </IconButton>
          </Tooltip>
          <Tooltip title="Enable Edit Mode">
            <IconButton onClick={() => setEditable(!editable)}>
              {editable ? <LockOpen sx={{fontSize:30, color:"primary.light"}} /> : <Lock sx={{fontSize:30, color:"primary.light"}}/>}
              </IconButton>
          </Tooltip>
          <Tooltip title="Reset">
            <IconButton disabled={edited ? null : true} onClick={() => {setStatblockWithoutEdit(statblock); setEdited(false)}}>
              <Restore sx={{fontSize:30, color:edited ? "primary.light": null}} />
              </IconButton>
          </Tooltip>
          <Tooltip title="Save Changes">
            <IconButton disabled={edited ? null : true} onClick={save}>
              <Save sx={{fontSize:30, color:edited ? "secondary.main" : null}}/>
            </  IconButton>
          </Tooltip>
        </Stack>
      }
      </Box>
      <Divider sx={{width:1}}/>
      <Box style={{columnCount:numColumns, width:"100%", padding:2, overflow:"auto",...style}} >
          {sb ?<>
          <ACField editable={editable}  statblock={sb} setStatblock={setStatblock} resetFunc={resetFunc("ac")} width={400}/>
          <HPField editable={editable}  statblock={sb} setStatblock={setStatblock} resetFunc={resetFunc("hp")}/>
          <DistanceField editable={editable} statblock={sb} setStatblock={setStatblock} title="speed" 
                          text="Speed" singular="Speed" fmt_func={fmt.format_speed} default_option={{type:"walk", distance:"30", measure:"ft"}}
                          min_items={1}
                          options={MOVEMENT_TYPES} default_options={{type:"walk",distance:"30",measure:"ft"}} resetFunc={resetFunc("speed")} />
          <Divider  sx={{marginTop:1}}/>
          <AttrTable editable={editable} statblock={sb} setStatblock={setStatblock} resetFunc={resetFunc("abilities")}/>
          <Divider  sx={{marginBottom:1}}/>
          <SkillsField editable={editable}  statblock={sb} setStatblock={setStatblock} resetFunc={resetFunc("skills")}/>
          <ImmVulnField statblock={sb} setStatblock={setStatblock} options={DAMAGE_TYPES} 
                        title_text="Resistances" title="resistances"  singular="Resistance"
                        fmt_func={fmt.format_resistances} editable={editable} resetFunc={resetFunc}/>
          <ImmVulnField statblock={sb} setStatblock={setStatblock} options={DAMAGE_TYPES} 
                        title_text="Damage Immunities" title="damage_immunities" singular="Immunity"
                        fmt_func={fmt.format_damage_immunities} editable={editable} resetFunc={resetFunc} />
          <ImmVulnField statblock={sb} setStatblock={setStatblock} options={CONDITIONS} 
                        title_text="Condition Immunities" title="condition_immunities" singular="Immunity"
                        fmt_func={fmt.format_condition_immunities} editable={editable} resetFunc={resetFunc}/>
          <ImmVulnField statblock={sb} setStatblock={setStatblock} options={DAMAGE_TYPES} 
                        title_text="Vulnerabilities" title="vulnerabilities" singular="Vulnerability"
                        fmt_func={fmt.format_vulnerabilities} editable={editable} resetFunc={resetFunc} />
          <DistanceField statblock={sb} setStatblock={setStatblock} title="senses" 
                          text="Senses" fmt_func={fmt.format_senses} singular="Sense"
                          options={SENSES} default_options={{type:"darkvision",distance:"60",measure:"ft"}} editable={editable} resetFunc={resetFunc("senses")}/>
          <LanguagesField statblock={sb} setStatblock={setStatblock} editable={editable} resetFunc={resetFunc("languages")}/>
          <ChallengeField statblock={sb} setStatblock={setStatblock} editable={editable} resetFunc={resetFunc("cr")}/>
          <div style={{marginTop:10}} />
          <FeaturesField statblock={sb} setStatblock={setStatblock} editable={editable}  resetFunc={resetFunc("features")}/>
          <ActionField statblock={sb} setStatblock={setStatblock} editable={editable} resetFunc={resetFunc}/>
          <div style={{marginTop:10}} />
          <Typography align="right" variant="subtitle2" sx={{margin:1}}><i>Source: {statblock.source.title}, pg.{statblock.source.page}</i></Typography>
          </>
        : <></>}
      </Box>
      </Stack>
  );
}

export default StatblockViewer;
