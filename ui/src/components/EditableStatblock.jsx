import React, { useState, useEffect } from 'react';
import { FormGroup,  FormControlLabel, TextareaAutosize, Stack, TextField, Paper, Popper, Typography, Divider, Table, TableHead, TableBody, TableRow, TableCell,  Checkbox, styled, Button } from "@mui/material"

import { TYPES, SIZES, MOVEMENT_TYPES, MEASURES, SHORT_ABILITIES, SHORT_SKILLS, SHORT_SKILL_ABILITY_MAP, SKILL_MAP, CRTABLE, DAMAGE_TYPES, CONDITIONS, SENSES, TIME_MEASURES } from '../constants.js';


import { StyledTextField, StyledDropdown, SkillField, HighlightText, CustomSkillField, StyledTextAndOptField, LabelledCheckboxField, EffectField } from './FormFields.jsx';

import * as fmt from '../libs/creature_format.js'
import { Delete } from '@mui/icons-material';
import { Add } from '@mui/icons-material';
import { get_default_skill_bonus, get_proficiency } from '../libs/game.js';




function OptTypography (props) {
  return (
    props.statblock[props.label] ? <Typography>{props.children}</Typography> : <></>
  )
}

function PoppableField( {children, text, textProps, hide=false, openable=true} ) {
  const [anchorEl, setAnchorEl] = useState(null);   

  const handleClick = (event) => {
    setAnchorEl(anchorEl ? null : event.currentTarget);
  }

  return (
    <>
    {!openable && !hide ?
    <Typography {...textProps}>{text}</Typography> :
    <>
      {text && !(hide === true) ? <HighlightText {...textProps} onClick={handleClick}>{text}</HighlightText> : <></>}
      <Popper
        open={Boolean(anchorEl)}
        anchorEl={anchorEl}
        placement="bottom-start"
        keepMounted={false}
      >
        <Paper square={true} sx={{padding:2}}>
            {children}<br />
            <Button sx={{m:0, mb:-1, alignSelf:"end", textAlign:"right", ml:31}} onClick={() => setAnchorEl(null)}>Close</Button>
          </Paper>
      </Popper>
      </>
    }
    </>
  )
}




function RaceTypeAlignmentField({ statblock, setStatblock }) {
  const setSize = (event) => {
    setStatblock((s) => ({...s, size:[event.target.value]}))
  }

  const setType = (event) => {
    setStatblock((s) => {return {...s, creature_type:{...s.creature_type, type:[event.target.value]}}})
  }
  
  const setSwarm = (event) => {
    setStatblock(s => ({...s, creature_type:{...s.creature_type, swarm:event.target.checked}}))
  }

  const setSwarmSize = (event) => {
    const ss = event.target.value !== '-' ? event.target.value : null;
    setStatblock(s=> ({...s, creature_type:{...s.creature_type, swarm:true, swarm_size:ss}}))
  }

  const setAlignment = (event) => {
    setStatblock(s => ({...s, alignment:event.target.value}));
  }

  return (
    <PoppableField text={<i>{fmt.format_race_type_alignment(statblock)}</i>} textProps={{variant:"subtitle2"}}>
        <FormGroup sx={{p:0, marginBottom:-2}}>
          <StyledDropdown id="size-dropdown" label="Size" value={statblock?.size} onChange={setSize} options={SIZES} />
          <FormControlLabel sx={{alignContent:"left", justifyContent:"left"}} labelPlacement="start" control={<Checkbox checked={statblock?.creature_type?.swarm} onChange={setSwarm} />} label="Swarm" />
          {statblock?.creature_type?.swarm === true ? <StyledDropdown label="Swarm Size" value={statblock?.creature_type?.swarm_size ? statblock?.creature_type?.swarm_size : "-"} onChange={setSwarmSize} options={["-"].concat(SIZES)} /> : <></>}
          <StyledDropdown label="Type" value={statblock?.creature_type?.type} onChange={setType} options={TYPES} />
          <StyledTextField label="Alignment" value={statblock?.alignment} onChange={setAlignment} />
        </FormGroup>
    </PoppableField>  
  )
}

function ACField({ statblock, setStatblock }) {
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

  return(
    <PoppableField text={<><b>Armour Class</b> {fmt.format_ac(statblock)}</>}>
        {statblock?.ac?.map((ac, i) => 
          (<Paper key={`ac-set-value-${i}`} square variant="outlined" sx={{padding:1, flexDirection:"column", display:"flex", mb:1}}>
            <StyledTextField label="AC" value={ac.ac} onChange={setACField("ac", i)} number/>
            <StyledTextField label="Conditions" value={ac.condition} onChange={setACField("condition", i)}/>
            {ac.from.map((f,j) =>
              (<StyledTextField key={`ac-set-value-${i}-from-${j}`} label="From" value={f}
                 onChange={setACField("from", i, j)} 
                 endButton={<Delete />}
                 onEndButtonClick={removeACFrom(i,j)} />)
            )}
            <Button startIcon={<Add />} onClick={(addACFrom(i))}>Add AC Source</Button>
            {i > 0 ? <Button startIcon={<Delete />} onClick={removeAC(i)}>Remove AC</Button> : <></>}
            </Paper>
          )
        )}
        <Button startIcon={<Add />} onClick={addAC}>Add Armor Class</Button>
    </PoppableField>
  )
}

function HPField( { statblock, setStatblock }) {
  const setHP = (field) => (e) => {
    setStatblock(s => {
      const hp = s.hp
      s.hp[field] = e.target.value
      return {...s, hp:hp}
    })
  }

  return (
    <PoppableField text={<><b>Hit Points</b> {fmt.format_hp(statblock)}</>}>
      <FormGroup sx={{p:0, m:0, mb:-2.5}}>
      <StyledTextField 
        label="HP Average" 
        value={statblock.hp?.average} 
        onChange={setHP("average")}
        validate={(v) => Number.isInteger(Number(v))}
        number
      />
      <StyledTextField label="HP Formula" value={statblock.hp?.formula} onChange={setHP("formula")} />
      </FormGroup>
    </PoppableField>
  )
}

function DistanceField( { statblock, setStatblock, title, text, options, fmt_func, default_option, singular, min_items=0}) {

  const addEntry = () => {
    setStatblock(s => {
      const val = s[title];
      val.push(default_option)
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


  return (
    <PoppableField text={<><b>{text}</b> {fmt_func(statblock)}</>} >
      {statblock && statblock[title] ? statblock[title].map((s,i) => 
          (<><Paper key={`distance-${title}-set-value-${i}`} square variant="outlined" 
                    sx={{padding:1, flexDirection:"column", display:"flex", mb:1}}>
          <StyledDropdown value={s.type} options={options} label={"Type"} onChange={setField("type", i)} capitalise={false} />
          <StyledTextField label="Value" value={s.distance} onChange={setField("distance", i)} number />
          <StyledDropdown value={s.measure} options={MEASURES} label={"Measure"} capitalise={false} onChange={setField("measure", i)} />
          {i >= min_items ? <Button startIcon={<Delete />} onClick={removeEntry(i)}>Remove {singular}</Button> : <></>}
        </Paper>
        </>) 
      ) : <></> }
      <Button key={`${title}-add-button`} startIcon={<Add />} onClick={addEntry}>Add {singular}</Button>
    </PoppableField>
    
  )
}


function PoppableAttrTable( {statblock, setStatblock}) {
  const [anchorEl, setAnchorEl] = useState(null);   

  const handleClick = (event) => {
    setAnchorEl(anchorEl ? null : event.currentTarget);
  }

  const onChange = (attr) => (event) => {
    setStatblock(s => {
      const newS = {...s}
      newS.abilities[attr] = Number(event.target.value)
      return newS;
    }
      )
  }

  const attrs = fmt.attributes_to_modifiers(statblock);

  const sx = {minWidth: 200, leftMargin:2, rightMargin:2,
     "&:hover": 
            {
            backgroundColor: "#4363EA",
            color: "#FFF !important"
            },
        }

  return (<>
    <Table sx={sx} aria-label="attribute scores" size="small" onClick={handleClick}>
    <TableHead>
      <TableRow key={"attrtitle"}>
        {SHORT_ABILITIES.map(a => {
          return <TableCell key={`attr-title-${a}`} align="center"><b>{a.toUpperCase()}</b></TableCell>
        })}
      </TableRow>
    </TableHead>
    <TableBody>
        <TableRow
          key={"attributes"}
          sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
          {SHORT_ABILITIES.map((a,i) => {
            return (<TableCell key={`attr-value-${a}`} align="center">
              <Typography>{attrs[i]}</Typography>
              </TableCell>)
          })}
        </TableRow>
    </TableBody>
  </Table>
  <Popper
    open={Boolean(anchorEl)}
    anchorEl={anchorEl}
    placement="bottom-start"
  >
    <Paper square={true} sx={{padding:2, width:"164px", display:"flex", flexDirection:"column"}}>
      {SHORT_ABILITIES.map((a, i) => {
        return (<StyledTextField key={`attr-set-value-${a}`} label={a.toUpperCase()} short width={130} value={statblock.abilities && statblock.abilities[a] ? statblock.abilities[a] : "-"} onChange={onChange(a)} number/>);
      })}
        <br />
        <Button sx={{m:0, mb:-1, alignSelf:"end", textAlign:"right", ml:31}} onClick={() => setAnchorEl(null)}>Close</Button>
      </Paper>
  </Popper>
  </>
);
}


function SkillsField( {statblock, setStatblock, editable=true }) {

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
    <PoppableField text={<><b>Skills</b> {skills_text}</>} hide={!editable && skills_text.trim().length === 0}>
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

function ImmVulnField({ statblock, setStatblock, options, title_text, title, fmt_func }) {
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
    <PoppableField text={<><b>{title_text}</b> {fmt_func(statblock)}</>}>
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

function FeaturesField( {statblock, setStatblock, editable}) {

  const setFeatureEffect = (i,j) => (effect) => {
    const newF = {...statblock.features[i]}
    newF.effects[j] = effect
    statblock.features[i] = newF
    setStatblock({...statblock, features:statblock.features})
  }

  const removeFeatureEffect = (i,j) => () => {
    const newF = {...statblock.features[i]}
    newF.effects.splice(j, 1)
    statblock.features[i] = newF
    setStatblock({...statblock, features:statblock.features})
  }

  const addFeatureEffect = (i) => () => {
    const newF = {...statblock.features[i]}
    if (!newF.effects) {
      newF.effects = []
    }
    newF.effects.push({})
    statblock.features[i] = newF
    setStatblock({...statblock, features:statblock.features})
  }

  const setFeatureUses = (i, field, is_num) => (e) => {
    const newFeature = {...statblock.features[i]}
    if (is_num) {
      newFeature.uses[field] = Number(e.target.value)
    } else {
      newFeature.uses[field] = e.target.value
    }
    statblock.features[i] = newFeature
    setStatblock({...statblock, features:statblock.features})
  }

  const addRemoveUses = (i) => (e) => {
    const newFeature = {...statblock.features[i]}
    if (!newFeature.uses) {
      newFeature.uses = {slots:0, period:"day"}
    } else {
      delete newFeature.uses
    }
    statblock.features[i] = newFeature
    setStatblock({...statblock, features:statblock.features})
  }

  const onChange = (i, field) => (e) => {
    const newFeature = {...statblock.features[i]}
    newFeature[field] = e.target.value
    statblock.features[i] = newFeature
    return setStatblock({...statblock, features:statblock.features})
  }

  const addFeature = (e) => {
    let newFs = [];
    if (statblock.features) {
      newFs = [...statblock.features]
    }
    newFs.push({title:"New Feature", text:""})
    return setStatblock({...statblock, features:newFs})
  }

  const deleteFeature = (i) => () => {
    let newFs = statblock.features
    newFs.splice(i, 1)
    return setStatblock({...statblock, features:newFs})
  }

  if (statblock && statblock.features) {
    return (<> 
    <Typography variant="h6">Features</Typography>
    <Divider />
        { statblock.features.map((f,i) => 
            (<PoppableField text={fmt.format_feature(f)} key={`feature-${f.title}-popper-${i}`}>
              <Paper key={`${f.title}-set-value-${i}`} square variant="outlined" 
              sx={{padding:1, flexDirection:"column", display:"flex", mb:1, width:500}}>
                <StyledTextField 
                  label="Title" 
                  value={f.title} 
                  onChange={onChange(i, "title")} 
                  key={`feature-${i}-titlebox`}
                  endButton={<Delete />}
                  onEndButtonClick={deleteFeature(i)}
                />
                <Paper variant="outlined" sx={{p:1}} square>
                <TextField value={f.text} placeholder="Feature Text"
                  multiline
                  maxRows={100}
                  variant="standard"
                  InputProps={{disableUnderline:true}}
                  sx={{width:"100%"}}
                  onChange={onChange(i, "text")}
                  key={`feature-${i}-textbox`}
                />
                </Paper>
                  <StyledTextAndOptField 
                    label="Uses"
                    textValue={f.uses ? f.uses.slots : 0}
                    number
                    short
                    checkbox
                    checked = {f.uses !== undefined}
                    onCheckChange={addRemoveUses(i)}
                    onTextChange={setFeatureUses(i, "slots")}
                    onSelectChange={setFeatureUses(i, "period")}
                    midText="per"
                    selectValue={f.uses ? f.uses.period.replaceAll("_"," "): "-"}
                    options={TIME_MEASURES.map(s =>  s.replaceAll("_"," "))}
                    width="410px"
                    key={`feature-${i}-uses`}
                  >
                </StyledTextAndOptField>
                <Paper square variant="outlined" sx={{p:1, marginTop:1, alignItems:"center"}}>
                
                <Button onClick={addFeatureEffect(i)} startIcon={<Add />} sx={{ borderRadius:0,width:"100%"}}>Add Effect</Button>
                </Paper>
                {f && f.effects ? f.effects.map((e,j) =>
                  <EffectField 
                    effect={e} 
                    setEffect={setFeatureEffect(i,j)} 
                    removeEffect={removeFeatureEffect(i,j)} 
                    key={`feature-${i}-effects-field-${j}`}
                  />
                ) : <></>
                }
              </Paper>
          </PoppableField>))
        }
        {editable && <Button startIcon={<Add />} onClick={addFeature}>Add Feature</Button>}
      </> )
  }
}


function Statblock( { statblock, style, editable=true, splitLength=3000}) {

  const [numColumns, setNumColumns] = useState(1);
  const [sb, setStatblock] = useState(statblock);

  useEffect(() => {
    setStatblock(statblock)
    setNumColumns(JSON.stringify(statblock).length > splitLength ? 2 : 1)
  }, [statblock])


  return (
      <div style={{columnCount:numColumns, width:"100%", padding:2, ...style}} >
          {sb ? <div>
          <HighlightText variant="h5" suppressContentEditableWarning={true} contentEditable={true}>{statblock.name}</HighlightText>
          <RaceTypeAlignmentField editable statblock={sb} setStatblock={setStatblock} />
          <Divider sx={{marginTop:1, marginBottom:1}}/>
          <ACField editable statblock={sb} setStatblock={setStatblock}/>
          <HPField editable statblock={sb} setStatblock={setStatblock}/>
          <DistanceField statblock={sb} setStatblock={setStatblock} title="speed" 
                          text="Speed" singular="Speed" fmt_func={fmt.format_speed} 
                          min_items={1}
                          options={MOVEMENT_TYPES} default_options={{type:"walk",distance:"30",measure:"ft"}} />
          <Divider  sx={{marginTop:1}}/>
          <PoppableAttrTable editable statblock={sb} setStatblock={setStatblock}/>
          <Divider  sx={{marginBottom:1}}/>
          <SkillsField editable statblock={sb} setStatblock={setStatblock}/>
          <ImmVulnField statblock={sb} setStatblock={setStatblock} options={DAMAGE_TYPES} 
                        title_text="Resistances" title="resistances" 
                        fmt_func={fmt.format_resistances}/>
          <ImmVulnField statblock={sb} setStatblock={setStatblock} options={DAMAGE_TYPES} 
                        title_text="Damage Immunities" title="damage_immunities" 
                        fmt_func={fmt.format_damage_immunities}/>
          <ImmVulnField statblock={sb} setStatblock={setStatblock} options={CONDITIONS} 
                        title_text="Condition Immunities" title="condition_immunities" 
                        fmt_func={fmt.format_condition_immunities}/>
          <ImmVulnField statblock={sb} setStatblock={setStatblock} options={DAMAGE_TYPES} 
                        title_text="Vulnerabilities" title="vulnerabilities" 
                        fmt_func={fmt.format_vulnerabilities}/>
          <DistanceField statblock={sb} setStatblock={setStatblock} title="senses" 
                          text="Senses" singular="Sense" fmt_func={fmt.format_senses} 
                          options={SENSES} default_options={{type:"darkvision",distance:"60",measure:"ft"}} />
          <OptTypography label="languages" statblock={statblock}><b>Languages</b> {fmt.format_languages(statblock)}</OptTypography>
          <Typography><b>Challenge</b> {fmt.format_cr(statblock)}</Typography>
          <div style={{marginTop:10}} />
          <FeaturesField statblock={sb} setStatblock={setStatblock} editable />
          {["action", "reaction", "legendary"].map(a => fmt.format_action_block(statblock, a))}
          <div style={{marginTop:10}} />
          <Typography align="right" variant="subtitle2" sx={{margin:1}}><i>Source: {statblock.source.title}, pg.{statblock.source.page}</i></Typography>
        </div>
        : <>{console.log("No creature")}</>}
      </div>
  );
}

export default Statblock;
