import React, { useState, useEffect } from 'react';
import { FormGroup, Typography, Button, Grid, Checkbox } from "@mui/material"

import { REVERSE_SKILL_MAP, SHORT_SKILLS, SHORT_SKILL_ABILITY_MAP, SKILLS, SKILL_MAP } from '../../constants.js';


import {SkillField, CustomSkillField, StyledTextAndOptField, StyledDropdown, StyledTextField, StyledCheckbox } from '../FormFields.jsx';
import PoppableField from "./PoppableField.jsx";


import * as fmt from '../../libs/creature_format.js'
import { Add } from '@mui/icons-material';
import { get_default_skill_bonus, get_proficiency } from '../../libs/game.js';
import EditBlock from './EditBlock.jsx';


export default function SkillsField( {statblock, setStatblock, editable=true, resetFunc }) {

  const onProfChange = (i) => () => {
      setStatblock(s => {
        let skills = s.skills;
        const skill = skills[i]
        const prof = get_proficiency(s)
        if (skill.prof) {
          skill.mod -=prof
          skill.prof = false 
        } else {
          skill.mod += prof
          skill.prof = true
        }
        skills[i] = skill
        return {...s, skills:skills}
    })
  }
  
  const onCustomChange = (i) => () => {
    setStatblock(s => {
      const skills = [...s.skills]
      const skill = skills[i]
      skill.is_custom = !skill.is_custom
      skill.skill = ""
      skill.mod = 0
      skills[i] = skill
      return {...s, skills:skills}
    })
  }

  const onValueOverride = (i) => (val) => {
    console.log(val)
    setStatblock(s => {
      const skills = [...s.skills]
      if (val === "") {
        console.log("resetting to default")
        console.log(skills[i])
        skills[i].mod = get_default_skill_bonus(s, skills[i].skill, skills[i].prof).mod
        console.log(get_default_skill_bonus(s, skills[i].skill))
        skills[i].default = true
      } else {
        skills[i].mod = Number(val)
        skills[i].default = false
      }
      return {...s, skills:skills}
    })
  }


  const onSkillChange = (i) => (event) => {
    setStatblock(s =>{
      const skills = [...s.skills]
      const skill = skills[i]

      if (skill.is_custom) {
        skill.skill = event.target.value
      } else {
        const skill_name = REVERSE_SKILL_MAP[event.target.value]
        if (skill_name) {
          const dsb_old = get_default_skill_bonus(s, skill.skill, skill.prof)
          skill.skill = skill_name
          const dsb = get_default_skill_bonus(s, skill.skill, skill.prof)
          skill.mod -= dsb_old.skill_mod + dsb.skill_mod
        } else {
          skill.skill = event.target.value
        }
      }
      skills[i] = skill

      return {
        ...s, skills:skills
      }
    })
  }

  const onAddSkill = (i) => () => {
    setStatblock(s =>{
      let skills = []
      if (s.skills) {
        skills = [...s.skills]
      }
      const new_skill = {
        skill:"",
        mod:get_proficiency(statblock),
        default:false,
        prof:true,
      }
      skills.splice(i+1, 0, new_skill)
      return {...s, skills:skills}
    })
  }

  const onDeleteSkill = (i) => () => {
    setStatblock(s => {
      const skills = [...s.skills]
      skills.splice(i, 1)
      return {...s, skills:skills}
    })
  }

  const onReset = () => {
    resetFunc((sb) => {
      return sb.skills
    })
  }

  const skills_text = fmt.format_skills(statblock).map(s => `${s[0]} ${s[1]}`).join(", ");
  
  return ( 
    <PoppableField editable={editable} text={<><b>Skills</b> {skills_text}</>} hide={!editable && skills_text.trim().length === 0} onReset={onReset}>
      <Grid item container spacing={1} xs={12} key={`skills-eb`} sx={{alignItems:"center"}}>
        <EditBlock title="Skill" onAdd={onAddSkill(-1)}>
      {statblock.skills?.map((sk,i) => { 
        let skill_name = SKILL_MAP[sk.skill]?.toLowerCase()
        let short_ability = SHORT_SKILL_ABILITY_MAP[sk.skill]?.toUpperCase()
        if (skill_name === null | skill_name === undefined) {
            skill_name = sk.skill
            short_ability = ""
        }
        const default_skill = get_default_skill_bonus(statblock, sk.skill, sk.prof)            
    
        return (<>
              <Grid item xs={6} xl={2}>
                <StyledCheckbox
                  checked={sk.prof}
                  onCheckChange={onProfChange(i)}
                  label="Proficient" />
              </Grid>
              <Grid item xs={6} xl={2}>
                <StyledCheckbox
                  checked={sk.is_custom}
                  onCheckChange={onCustomChange(i)}
                  label="Custom" />
              </Grid>
              <Grid item xs={12} xl={8}>
                <SkillField skill={sk.skill} set_value={sk.mod} key={`skill-${i}`}
                          is_custom={sk.is_custom}
                          is_proficient={sk.prof} is_default={sk.default} width="400px"
                          default_value={default_skill.mod} skill_mod={default_skill.skill_mod}
                          onSkillChange={onSkillChange(i)}
                          onValueChange={e => onValueOverride(i)(e.target.value)}
                          onAdd={onAddSkill(i)}
                          onDelete={onDeleteSkill(i)}
                        />
              </Grid>
        </>)
      })}
            </EditBlock>
        </Grid>
      </PoppableField>
  );
}