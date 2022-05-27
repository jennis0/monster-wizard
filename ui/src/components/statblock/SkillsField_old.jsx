import React, { useState, useEffect } from 'react';
import { FormGroup, Typography, Button } from "@mui/material"

import { SHORT_SKILLS } from '../../constants.js';


import {SkillField, CustomSkillField } from './FormFields.jsx';
import PoppableField from "./PoppableField.jsx";


import * as fmt from '../../libs/creature_format.js'
import { Add } from '@mui/icons-material';
import { get_default_skill_bonus, get_proficiency } from '../../libs/game.js';


export default function SkillsField( {statblock, setStatblock, editable=true }) {

  const [customSkills, setCustomSkills] = useState([])

  const onCheckChange = (skill) => () => {
      setStatblock(s => {
        let skills = s.skills;
        const old_skill = skills.filter(sk => sk.skill === skill)
        if (old_skill.length === 1) {
          skills = skills.filter(sk => sk.skill !== skill)
          if (old_skill[0].prof === false) {
            old_skill[0].prof = true
            old_skill[0].mod = Number(old_skill[0].mod) + get_proficiency(statblock)
            skills.push(old_skill[0])
          } else {
            if (!old_skill[0].default) {
              old_skill[0].prof = false
              old_skill[0].mod = Number(old_skill[0].mod) - get_proficiency(statblock)
              skills.push(old_skill[0])
            }
          }
        } else {
          skills.push(get_default_skill_bonus(statblock, skill, true))
        }
        return {...s, skills:skills}
    })
  }

  const onValueChange = (skill) => (event) => {
    setStatblock(s =>{
      const old_skill = s.skills.filter(sk => sk.skill === skill)
      let skills = s.skills
      if (old_skill.length === 0) {
        if (event.target.value.trim() !== "") {
          skills.push(get_default_skill_bonus(statblock, skill, false))
          skills[-1].mod = event.target.value
          skills[-1].default = false
        } else if (old_skill.__custom_id >= 0) {
          skills.push(old_skill)
          skills[-1].mod = event.target.value
        }
      } else {
        for(const sk of skills) {
          if (sk.skill === skill) {
            if (event.target.value.trim() === "" && !(sk.__custom_id >= 0)) {
              skills = skills.filter(sk => sk.skill != skill)
            } else {
              sk.mod = event.target.value
              sk.default = false
            }
          }
        }
      }
      return {
        ...s, skills:skills
      }
    })
  }

  const onAddSkill = (event) => {
    setStatblock(s =>{
      const skills = s.skills
      skills.push({
        skill:"",
        mod:get_proficiency(statblock),
        default:false,
        prof:true,
        __custom_id:Math.floor(Math.random()*100000)
      })
      return {...s, skills:skills}
    })
  }

  const onDeleteSkill = (id) => (event) => {
    setStatblock(s => 
      {return {...s, skills:s.skills.filter(sk => sk.__custom_id !== id)}}
    )
  }

  const onSetSkillName = (id) => (event) => {
    setStatblock(s => {
      const skills = s.skills
      const sk_index = skills.findIndex(sk => sk.__custom_id === id)
      skills[sk_index].skill = event.target.value;
      return {...s, skills:skills}
    })

  }

  useEffect(() => {
    setCustomSkills(() => 
      statblock.skills?.filter(sk => !SHORT_SKILLS.includes(sk.skill)).map(sk => sk.__custom_id)
    )
  }
  ,[statblock])

  const skills_text = fmt.format_skills(statblock).map(s => `${s[0]} ${s[1]}`).join(", ");
  
  return ( 
    <PoppableField editable={editable} text={<><b>Skills</b> {skills_text}</>} hide={!editable && skills_text.trim().length === 0}>
      <FormGroup sx={{marginBottom:-2}}>
        <Typography variant="h6">Skills</Typography>
        {SHORT_SKILLS.map(s => {
          const current = statblock?.skills?.filter(sk => sk.skill === s); 
          let default_skill = null;
          let sk = null
          if (current?.length === 1) {
            sk = current[0];
            default_skill = get_default_skill_bonus(statblock, s, sk.prof)            
          } else {
            sk = get_default_skill_bonus(statblock, s, false)
            default_skill = sk
          }
          return (
            <SkillField skill={sk.skill} value={sk.mod} key={`skill-${sk.skill}`}
                        checked={sk.prof} is_default={sk.default} width="400px"
                        default_value={default_skill.mod}
                        onCheckChange={onCheckChange(sk.skill)}
                        onValueChange={onValueChange(sk.skill)}/>
        )})}
        {customSkills?.map(s => {
          const sks = statblock?.skills?.filter(sk => sk.__custom_id === s)
          if (sks && sks.length === 1) {
            const sk = sks[0]
          return (<CustomSkillField skill={sk.skill} value={sk.mod} 
                                    onNameChange={onSetSkillName(s)} 
                                    onValueChange={onValueChange(sk.skill)}
                                    onDelete={onDeleteSkill(s)}
                                    id={sk.__custom_id}
                                    key={`custom-skill-field-${sk.__custom_id}`}
          />
            )}
        })}
        <Button onClick={onAddSkill}><Add />Add Custom Skill</Button>
      </FormGroup>
      </PoppableField>
  );
}