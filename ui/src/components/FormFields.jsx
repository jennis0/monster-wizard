
import {TextField, IconButton, Stack, MenuItem, Button, Paper, Divider, Typography, Select, FormControl, Checkbox} from "@mui/material"
import styled from "@emotion/styled";
import { SKILL_MAP, SHORT_SKILL_ABILITY_MAP, DAMAGE_TYPES, CONDITIONS, SHORT_ABILITIES } from "../constants";
import { Add,Delete } from "@mui/icons-material";

export const HighlightText = styled(Typography)(({theme}) => (
    {"&:hover": 
      {
      backgroundColor: "#4363EA",
      color: "#FFF !important"
      },
    }
    )
  );

  


export function StyledTextField(props) {

    const labelWidth = props.short ? 50 : 100
    const buttonWidth = props.endButton ? 46 : 0
    const width = props.width ? props.width : "auto"
    const textWidth = props.buttonWidth ? `${width - labelWidth - buttonWidth}px` : null
    

    const error = props.validate ? !props.validate(props.value) : false;
    const bg =  error ? "#fcc" : null
    
    if (error && props.onError) {
        props.onError(props);
    }

    return (
        <FormControl>
        <Paper
            sx={{ p: '2px 4px', display: 'flex', alignItems: 'center', 
                    marginBottom:0.5, marginTop:0.5,
                    backgroundColor:bg, width:width
                }}
            variant="outlined"
            square={true}
            >
        {props.label ? <>
            <Typography  sx={{padding:1, textAlign:"center", width:`${labelWidth}px`, m:0, p:0, color:props.disabled ? '#ccc' : null}}>
                <b>{props.label}</b>
            </Typography> 
            <Divider orientation="vertical" sx={{height:28, m:0.5, mr:1}} /></>
         : <></>}
        { props.select ?
        <Select 
             value={props.value} 
             onChange={props.onChange}
             children={props.children} 
             disableUnderline={true} 
             disabled={props.disabled}
             variant="standard"
             sx={{m:0, p:0, width:textWidth, flex:1, height:"37px"}} 
             key={`styledtext-${props.label}-selectfield-${props.id}`}
             fullWidth/> :
        <TextField
            variant="standard"
            value={props.value}
            onChange={props.onChange}
            disabled={props.disabled}
            InputProps={{disableUnderline:true, type:props.number ? "number":null}}
            margin="dense"
            sx={{ m:0, flex: 1, width:textWidth }}
            fullWidth
            key={`styledtext-${props.label}-textfield-${props.id}`}
            {...props.textProps}
        />
        }
        { props.endButton ? 
            <><Divider orientation="vertical" sx={{height:28, m:0.5}} />
            <IconButton sx={{margin:0}} onClick={props.onEndButtonClick} disabled={props.disabled}>{props.endButton}</IconButton>
            </> : <></>
        }
    </Paper>
    </FormControl>
    )
}

export function StyledTextAndOptField(props) {

    const labelWidth = props.short ? 50 : 100
    const buttonWidth = props.endButton ? 46 : 0
    const width = props.width ? props.width : "100%"
    const textWidth = props.buttonWidth ? `${width - labelWidth - buttonWidth}px` : null
    

    const error = props.validate ? !props.validate(props.value) : false;
    const bg =  error ? "#fcc" : null
    
    if (error && props.onError) {
        props.onError(props);
    }

    return (
        <FormControl>
 <Paper
      sx={{ p: 0, display: 'flex', alignItems: 'center', pl:0.5, 
            marginBottom:0.5, marginTop:0.5,
            backgroundColor:bg, width:"100%"
        }}
      variant="outlined"
      square={true}
    >
        {props.label ? <>
            <Typography  sx={{padding:-1 ,m:0, textAlign:"center", width:`${labelWidth}px`}}>
                <b>{props.label}</b>
            </Typography> 
            <Divider orientation="vertical" sx={{height:28, m:0., ml:0.5, mr:1, p:0}} />
        </>
         : <></>}
        {props.checkbox ? 
            <>
                <Checkbox sx={{m:0, mr:0.5, p:0}} checked={props.checked === true} onChange={props.onCheckChange}/>        
                <Divider orientation="vertical" sx={{height:28, m:0.5, mr:1.5}} />
            </>
        : <></>} 
        {props.checked || props.checkbox === undefined || props.checkbox === null ? (<>
            {props.preText ? <Typography sx={{m:0, marginRight:1, mb:0.2,textAlign:"center", p:0}}>{props.preText}</Typography> : <></>}
            <TextField
                variant="outlined"
                value={props.textValue}
                onChange={props.onTextChange}
                InputProps={{disableUnderline:true, style:{height:"32px",borderRadius:0, textAlign:"center"}, type:props.number ? "number":null}}
                inputProps={{style:{textAlign:"center"}}}
                margin="dense"
                sx={{ m:1, flex: 1, width:textWidth, }}
                fullWidth
                {...props.textProps}
            />
            {props.midText ? <Typography sx={{m:1, p:0}}>{props.midText}</Typography> : <></>}
            <Select 
                value={props.selectValue} 
                onChange={props.onSelectChange}
                disableUnderline={true} 
                variant="standard"
                sx={{m:0, ml:1, mr:0.5,p:0, width:textWidth, flex:1, height:"37px"}} 
                fullWidth
                {...props.selectProps}
            >
                {props.options.map((s) => (
                    <MenuItem key={`${props.label}-${s}`} value={s}>{s}</MenuItem>
                ))}
            </Select>
            { props.endButton ? 
                <><Divider orientation="vertical" sx={{height:28, m:0.5}} />
                <IconButton sx={{margin:0}} onClick={props.onEndButtonClick}>{props.endButton}</IconButton>
                </> : <></>
            }
        </>) : <><TextField 
            variant="standard" 
            fullWidth
            InputProps={{disableUnderline:true, style:{height:"32px",borderRadius:0, textAlign:"center"}, 
                type:props.number ? "number":null}}
            disabled
            sx={{ m:1, flex: 1, width:textWidth, }}

             ></TextField></>} 
    </Paper>
    </FormControl>

    )
}


export function StyledDropdown ({ id, label, value, onChange, options, capitalise=true, textFieldProps={} }) { 
    console.log(value)
    const do_capitalise = (s) => {
      return s.length > 0 ? s[0].toUpperCase() + s.substring(1) : ""
    }
    return (
      <StyledTextField id={id} label={label} select value={value} onChange={onChange} {...textFieldProps}>
        {options.map((s) => (
          <MenuItem key={`${label}-${s}`} value={s}>{capitalise ? do_capitalise(s) : s}</MenuItem>
        ))}
        </StyledTextField>
  )}

export function SkillField ( { checked, skill, is_default, default_value, onCheckChange, onValueChange, value, textProps, width }) {
    
    if (checked === undefined) {
        checked = true
    }
    if (is_default === undefined) {
        is_default = true
    }

    return (
        <FormControl>
        <Stack direction="row" sx={{alignItems:"center", width:330}} spacing={1}>
        <Paper
            sx={{ p: '0px 0px', display: 'flex', alignItems: 'center',  
                    marginBottom:0.5, marginTop:0.5, width:"auto", borderColor: is_default ? null : "#c0c"
                }}
            variant="outlined"
            square={true}
        >
            <Stack direction="row" sx={{alignItems:"center", width:250}} 
                divider={ <Divider orientation="vertical" sx={{height:28, m:0.5, mr:1}} />}>
                <Checkbox checked={checked} id={`checkbox-${skill}`} onClick={onCheckChange} 
                    sx={{marginRight:-0}}/>
                    <>
                <Typography
                    sx={{ m:0, marginLeft:0, flex: 1, width:"300px"}}
                    {...textProps} 
                >
                    {SKILL_MAP[skill]}
                </Typography>
                <Typography 
                    sx={{marginRight:1, textJustify:"left", color:"#ccc", width:50}}>
                        {`${SHORT_SKILL_ABILITY_MAP[skill].toUpperCase()} ${default_value >= 0 ? '+' : ''}${default_value}`}
                </Typography>
                </>
            </Stack>
        </Paper>
        <Paper
      sx={{ p: '0px 0px', display: 'flex', alignItems: 'center',  
            marginBottom:0.5, marginTop:0.5, width:"auto", borderColor: is_default ? null : "#c0c"
        }}
        variant="outlined"
        square={true}
      >
            <TextField
                variant="standard"
                value={is_default ? "" : value}
                placeholder="OVERRIDE"
                onChange={onValueChange}
                InputProps={{disableUnderline:true, color:"red"}}
                margin="dense"
                inputProps={{min: 0, style: { textAlign: 'center',  }}}
                sx={{ m:0.6, marginRight:1, flex: 1, width:"auto", "& input::placeholder":{fontSize:"9px"}}}
                fullWidth            
        />
        </Paper>
        </Stack>
    </FormControl>

    )
}

export function CustomSkillField ( { id, skill, value, onNameChange, onValueChange, onDelete, textProps, width }) {
    return (
        <FormControl>
        <Stack direction="row" sx={{alignItems:"center", width:330}} spacing={1}>
        <Paper
            sx={{ p: '0px 0px', display: 'flex', alignItems: 'center',  
                    marginBottom:0.5, marginTop:0.5, width:"auto"
                }}
            variant="outlined"
            square={true}
            >
        <Stack direction="row" sx={{alignItems:"center", width:250}} 
            divider={ <Divider orientation="vertical" sx={{height:28, m:0.5, mr:1}} />}>
            <Checkbox checked={true} disabled id={`checkbox-${skill}`}
                sx={{marginRight:-0}}/>
                <>
            <TextField
                key={`custom-skill-id-${id}`}
                variant="standard"
                placeholder="SKILL"
                value={skill}
                onChange={onNameChange}
                InputProps={{disableUnderline:true, color:"red"}}
                margin="dense"
                inputProps={{min: 0, style: { textAlign: 'left',  }}}
                sx={{ marginTop:0.6, marginBottom:0.6, marginRight:1, flex: 1, width:250, "& input::placeholder":{fontSize:"13px"}}}
                fullWidth   
                {...textProps} />
            <Button onClick={onDelete} sx={{marginLeft:0}}><Delete /></Button>
            </>
        </Stack>

            </Paper>
        <Paper
      sx={{ p: '0px 0px', display: 'flex', alignItems: 'center',  
            marginBottom:0.5, marginTop:0.5, width:"auto"
        }}
        variant="outlined"
        square={true}
      >
            <TextField
                variant="standard"
                value={value}
                placeholder="MODIFIER"
                onChange={onValueChange}
                InputProps={{disableUnderline:true, color:"red"}}
                margin="dense"
                inputProps={{min: 0, style: { textAlign: 'center',  }}}
                sx={{ m:0.6, marginRight:1, flex: 1, width:"auto", "& input::placeholder":{fontSize:"9px"}}}
                fullWidth            
        />
        </Paper>
        </Stack>
    </FormControl>

    )
}

export function LabelledCheckboxField ( { checked, label, onChange, textProps, width }) {
    
    if (checked === undefined) {
        checked = false
    }

    return (
        <FormControl>
        <Paper
            sx={{ p: '0px 0px', display: 'flex', alignItems: 'center',  
                    marginBottom:0.5, marginTop:0.5, width:"100%", 
                }}
            variant="outlined"
            square={true}
        >
            <Stack direction="row" sx={{alignItems:"center", width:"100%"}} spacing={0}
                divider={ <Divider orientation="vertical" sx={{height:28, m:0.5, mr:1}} />}>
                <Checkbox checked={checked} id={`checkbox-${label}`} onClick={onChange} 
                    sx={{marginRight:-0, ml:0.5}} />
                <Typography
                    sx={{ m:0, marginLeft:1, flex: 1, width:100}}
                    {...textProps} 
                >
                    {label}
                </Typography>

            </Stack>
        </Paper>
    </FormControl>
    )
}

export function EffectField( {effect, setEffect, removeEffect} ) {

    const setValue = (field, subfield, is_num) => (e) => {
        const newEffect = {...effect}
        if (is_num) {
            newEffect[field][subfield] = Number(e.target.value)
        } else {
            newEffect[field][subfield] = e.target.value
        }
        setEffect(newEffect)
    }

    const addRemoveField = (field, default_value) => () => {
        const newEffect = {...effect}
        console.log(newEffect)
        if (newEffect[field]) {
            console.log("deleting")
            delete newEffect[field]
        } else {
            newEffect[field] = default_value
        }
        console.log(newEffect)
        setEffect(newEffect)
    }

    const setHalfDamage = () => {
        const newEffect = {...effect}
        if (newEffect.on_save) {
            if (newEffect.on_save == "half") {
                newEffect.on_save = "none"
            } else {
                newEffect.on_save = "half"
            }
        } else {
            newEffect.on_save = "half"
        }
        setEffect(newEffect)
    }

    const addCondition = () => {
        console.log(effect)
        const newEffect = {...effect}
        if (newEffect.conditions === null || newEffect.conditions === undefined) {
            newEffect.conditions = []
        }
        newEffect.conditions.push({"condition":""})
        setEffect(newEffect)
    }

    const updateCondition = (i) => (e) => {
        const newEffect = {...effect}
        newEffect.conditions[i]["condition"] = e.target.value
        setEffect(newEffect)
    }

    const deleteCondition = (i) => () => {
        const newEffect = {...effect}
        newEffect.conditions.splice(i,1)
        setEffect(newEffect)
    }

    return (
        <Paper square variant="outlined" sx={{p:1, marginTop:1, alignItems:"center"}}>                  
                <Stack>
                  <Typography sx={{m:1, ml:0.5}}><b>Effect {1}</b></Typography>
                <StyledTextAndOptField 
                    label="Damage"
                    checkbox
                    checked={effect.damage !== undefined && effect.damage !== null}
                    textValue={effect.damage ? effect.damage.damage : ""}
                    selectValue={effect.damage ? effect.damage.type : ""}
                    onTextChange={setValue("damage","damage",true)}
                    onSelectChange={setValue("damage","type",false)}
                    onCheckChange={addRemoveField("damage", {"damage":0, "type":"bludgeoning"})}
                    options={DAMAGE_TYPES}
                    width="410px"
                    />
                  <StyledTextAndOptField 
                    label="Save"
                    checkbox
                    checked={effect.save != undefined}
                    preText={"DC"}
                    textValue={effect.save ? effect.save.value : ""}
                    selectValue={effect.save ? effect.save.ability.toUpperCase() : ""}
                    onTextChange={setValue("save","value",true)}
                    onSelectChange={setValue("save","ability",false)}
                    onCheckChange={addRemoveField("save", {"value":10, "ability":"wis"})}
                    options={SHORT_ABILITIES.map(a => a.toUpperCase())}
                    width="410px"
                    />
                    <StyledTextAndOptField 
                    label="Save to End"
                    checkbox
                    checked={effect.end_save != undefined}
                    preText={"DC"}
                    textValue={effect.end_save ? effect.end_save.value : ""}
                    selectValue={effect.end_save ? effect.end_save.ability.toUpperCase() : ""}
                    onTextChange={setValue("end_save","value",true)}
                    onSelectChange={setValue("end_save","ability",false)}
                    onCheckChange={addRemoveField("end_save", {"value":10, "ability":"wis"})}
                    options={SHORT_ABILITIES.map(a => a.toUpperCase())}
                    width="410px"
                    />
                  <LabelledCheckboxField 
                    label="Half damage on save" 
                    checked={effect.on_save ? effect.on_save === "half" : false}
                    onChange={setHalfDamage}
                  />
                  <Button onClick={addCondition} startIcon={<Add />} >Add Condition</Button>
                  {effect.conditions ? effect.conditions.map((c,i) => (
                        <StyledDropdown  
                        label="Condition" 
                        options={CONDITIONS} 
                        value={c.condition}
                        onChange={updateCondition(i)}
                        textFieldProps={{endButton:(<Delete />),
                                        onEndButtonClick:deleteCondition(i)}}
                    />
                  )) : <></>}

                  <Divider />
                  <Button startIcon={<Delete />} sx={{mt:1}} onClick={removeEffect}>Remove Effect</Button>
                  </Stack>
                </Paper>
    )
}
