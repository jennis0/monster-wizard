
import {TextField, IconButton, Stack, MenuItem, Box, Button, Paper, Divider, Typography, Select, FormControl, Checkbox, ListSubheader, ButtonGroup, Tooltip} from "@mui/material"
import { SKILL_MAP, SHORT_SKILL_ABILITY_MAP, SKILLS, MEASURES} from "../../constants";
import { AnchorOutlined, ConstructionOutlined, Delete } from "@mui/icons-material";
import { Add } from "@mui/icons-material";
import { useEffect, useState } from "react";


export function LazyTextField({value, onChange, transform=(t) => t, ...props}) {
    const [textValue, setTextValue] = useState(value)
    const onEnter = (e) => {
        if(e.keyCode == 13){
           onChange(e);
        }
     }

     let text = transform(textValue)
     if (!text) {
         text = ""
     }

     return (
        <TextField
            {...props}
            value={text}
            onChange={(e) => setTextValue(e.target.value)}
            onBlur={onChange}
            onKeyDown={onEnter}
        />
     )
}


export function HighlightText ( {editable, onClick, color, ...props} ) {

    return (
        <Box sx={{m:0, p:0, width:"100%", color:color, "&:hover": editable === true ? {backgroundColor:"primary.light", color:"primary.contrastText"} : null, "&:focus":null}} onClick={onClick}>
            <Typography sx={{whiteSpace:"pre-wrap",  "&:selected": {borderWidth:0, color:"blue"}, "&:": {borderWidth:0, color:"blue"}}} variant="statblock" {...props}/>
        </Box>
    )
}


export function StyledCheckbox(props) {

    const labelWidth = props.short ? 60 : 100
    const width = props.width ? props.width : "100%"   

    const error = props.validate ? !props.validate(props.value) : false;
    const bg =  error ? "#fcc" : null
    
    if (error && props.onError) {
        props.onError(props);
    }

    return (
        <Tooltip title={props.tooltip && !props.disabled ? props.tooltip : ""}>
        <Paper
            sx={{ p:0, display: 'flex', alignItems: 'center',  
                    backgroundColor:bg, maxWidth:"151px", height:"40px",
                }}
            variant="outlined"
            onClick={() => props.onCheckChange({target:{checked:!props.checked}})}
            square={true}
            >
            <Box sx={{width:"100px", textAlign:"center"}}>
                <Typography variant="statblock"  sx={{padding:1 ,m:0, ml:0, mr:0.0, textAlign:"center", width:`${labelWidth}px`}}>
                    {props.label}
                </Typography> 
            </Box>
            <Divider orientation="vertical" sx={{height:40, m:0., ml:0, mr:1, p:0}} />
            <Box sx={{width:"40px", alignItems:"center", justifyItems:"center", textJustify:"center"}}>
                <Checkbox sx={{m:0, mr:0,ml:0.6, p:0, alignSelf:"center"}} checked={props.checked === true} onChange={props.onCheckChange}/>         
            </Box>
    </Paper>
    </Tooltip>
    )
    
}

export function StyledRangeField( {range, onChange, short, ...props}) {

    const labelWidth = "100px"
    const width="100%"

    return (
        <Tooltip title={props.tooltip && !props.disabled ? props.tooltip : ""}>
        <Paper
            sx={{ p:0, display: 'flex', alignItems: 'center',  
                    width:width, height:"40px"
                }}
            variant="outlined"
            square={true}
        >
            <Typography variant="statblock"  sx={{padding:0 ,m:0, ml:0, textAlign:"center", width:labelWidth}}>
                Range
            </Typography> 

            {false ? 
                <>
                    <Checkbox sx={{m:0, mr:1,ml:-1.5, p:0, width:"40px"}} checked={props.checked === true} onChange={props.onCheckChange}/>        
                </>
            : <></>} 
        
            <Divider orientation="vertical" sx={{height:40, m:0., ml:0, mr:0, p:0}} />
            
            <TextField
                variant="standard"
                value={range?.short_distance}
                placeholder="Short"
                onChange={onChange("short_distance")}
                InputProps={{disableUnderline:true}}
                inputProps={{style:{alignSelf:"center", textAlign:"center", fontFamily:"Scaly Sans", fontSize:17}}}
                sx={{ m:0, p:0, mb:-0.5, width:"70px" }}
                key={`styledtext-short}-textfield`}
            />

            <Typography variant="statblock" sx={{m:0, textAlign:"center", flex:1}}>/</Typography>
            <TextField
                variant="standard"
                placeholder="Long"
                value={range?.long_distance}
                onChange={onChange("long_distance")}             
                InputProps={{disableUnderline:true}}
                inputProps={{style:{alignSelf:"center", textAlign:"center",fontFamily:"Scaly Sans", fontSize:17}}}
                sx={{ m:0, p:0, mb:-0.5, width:"70px"}}
                key={`styledtext-long-textfield`}
            />

            <Select 
                value={range?.measure} 
                onChange={onChange("measure")}
                disableUnderline={true} 
                variant="standard"
                sx={{m:0, p:0, width:"50px", m:0.5, height:"32px", textAlign:"center", fontFamily:"Scaly Sans", fontSize:17}} 
                key={`styledtext-measure-selectfield`}
                fullWidth
            >
                {MEASURES.map((s) => (
                    <MenuItem key={`range-measure-${s}`} value={s}>{s}</MenuItem>
                ))}
            </Select>
        </Paper>
        </Tooltip>
    )
}

export function StyledTextField(props) {

    const labelWidth = props.short ? 60 : 100
    const width = props.width ? props.width : "100%"   

    const error = props.validate ? !props.validate(props.value) : false;
    const bg =  error ? "#fcc" : null
    
    if (error && props.onError) {
        props.onError(props);
    }

    return (
        <Tooltip title={props.tooltip && !props.disabled ? props.tooltip : ""} disableHoverListener={props.disabled === true}>
        <Paper
            sx={{ p:0, display: 'flex', alignItems: 'center',  
                    backgroundColor:bg, width:width, height:"40px"
                }}
            disabled={props.disabled}
            variant="outlined"
            square={true}
        >
            {props.label ? <>
                <Typography variant="statblock"  
                    sx={{padding:0 ,m:0, ml:0, textAlign:"center", width:`${labelWidth}px`,
                            color: props.disabled ? "#a0a0a0" : null
                        }}>
                    {props.label}
                </Typography> 
            </>
            : <></>}

            {props.checkbox ? 
                <>
                    <Checkbox sx={{m:0, mr:1,ml:-1.5, p:0, width:"40px"}} checked={props.checked === true} onChange={props.onCheckChange}/>        
                </>
            : <></>} 
        
            {props.label && <Divider orientation="vertical" sx={{height:40, m:0., ml:0, mr:1, p:0}} />}

            { props.select ?
            <Select 
                value={props.value} 
                onChange={props.onChange}
                children={props.children} 
                disableUnderline={true} 
                disabled={props.disabled}
                variant="standard"
                sx={{m:0, p:0, flex:1, m:0.5, height:"32px", textAlign:"center", fontFamily:"Scaly Sans", fontSize:17}} 
                key={`styledtext-${props.label}-selectfield-${props.id}`}
                fullWidth/> :
            <LazyTextField
                variant="standard"
                value={props.value}
                onChange={props.onChange}
                disabled={props.disabled}
                InputProps={{disableUnderline:true}}
                inputProps={{style:{alignSelf:"center", fontFamily:"Scaly Sans", fontSize:17}}}
                sx={{ m:0, p:0, mb:-0.5, flex: 1 }}
                fullWidth
                key={`styledtext-${props.label}-textfield`}
                {...props.textProps}
            />
            }

            { props.endButton ? 
                <><Divider orientation="vertical" sx={{height:40, m:0.5}} />
                <ButtonGroup sx={{width:`${27*props.endButton.length}px`, alignItems:"center", ml:-0.5}}>
                {props.endButton.map((eb, i) => {
                    return (
                    <>
                    <Box sx={{display:"flex", flexDirection:"row", alignItems:"center", height:40, width:"27px"}}>
                    <IconButton key={`end-button-${i}`} sx={{margin:0, p:0, borderRadius:0 , height:40, width:"27px"}} 
                        onClick={props.onEndButtonClick[i]} disabled={props.disabled}>
                            {eb}
                    </IconButton>
                    {i < props.endButton.length-1 && <Divider orientation="vertical" sx={{height:40, m:0.}} />}
                    </Box>
                    </>)
                })}
                </ButtonGroup>
                </> : <></>
            }
    </Paper>
    </Tooltip>
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
        <Tooltip title={props.tooltip && !props.disabled ? props.tooltip : ""}>
        <Paper
        sx={{ p: 0, display: 'flex', alignItems: 'center', 
                marginBottom:0., marginTop:0., height:"40px",
                backgroundColor:bg, width:width
            }}
        variant="outlined"
        square={true}
        >
        {props.label ? <>
            <Typography variant="statblock"  sx={{padding:0 ,m:0, ml:0, textAlign:"center", width:`${labelWidth}px`}}>
                {props.label}
            </Typography> 
        </>
         : <></>}
        {props.checkbox ? 
            <>
                <Checkbox sx={{m:0, mr:1,ml:-1.5, p:0, width:"40px"}} checked={props.checked === true} onChange={props.onCheckChange}/>        
            </>
        : <></>} 
        {props.label && <Divider orientation="vertical" sx={{height:40, m:0., ml:0, mr:1, p:0}} />}
        {props.checked || props.checkbox === undefined || props.checkbox === null ? (<>
            {props.preText ? <Typography variant="statblock" sx={{m:0, ml:0.5, marginRight:0.5, mb:0.2,textAlign:"center", p:0}}>{props.preText}</Typography> : <></>}
            <LazyTextField
                variant="standard"
                value={props.textValue}
                onChange={props.onChange}
                InputProps={{disableUnderline:true, style:{height:"32px",borderRadius:0, textAlign:"center"}, type:props.number ? "number":null}}
                inputProps={{style:{alignSelf:"center", fontFamily:"Scaly Sans", fontSize:17, textAlign:"center"}}}
                margin="dense"
                sx={{ m:0.5, p:0, flex: 1, width:textWidth, textAlign:"center" }}
                fullWidth
                {...props.textProps}
            />
            {props.midText ? <Typography sx={{m:0., p:0, ml:1, mr:1}}>{props.midText}</Typography> : <></>}
            <Select 
                value={props.selectValue} 
                onChange={props.onSelectChange}
                disableUnderline={true} 
                variant="standard"
                sx={{m:0., ml:0.5, mr:0.5,p:0, width:textWidth, flex:1, height:"32px", textAlign:"center", fontFamily:"Scaly Sans", fontSize:17}} 
                fullWidth
                {...props.selectProps}
            >
                {props.options.map((s) => (
                    <MenuItem key={`${props.label}-${s}`} value={s}>{s}</MenuItem>
                ))}
            </Select>
            { props.endButton ? 
            <><Divider orientation="vertical" sx={{height:40, m:0.5}} />
            <ButtonGroup sx={{width:`${27*props.endButton.length}px`, alignItems:"center", ml:-0.5}}>
            {props.endButton.map((eb, i) => {
                return (
                <>
                <Box sx={{display:"flex", flexDirection:"row", alignItems:"center", height:40, width:"27px"}}>
                <IconButton key={`end-button-${i}`} sx={{margin:0, p:0, borderRadius:0 , height:40, width:"27px"}} 
                    onClick={props.onEndButtonClick[i]} disabled={props.disabled}>
                        {eb}
                </IconButton>
                {i < props.endButton.length-1 && <Divider orientation="vertical" sx={{height:40, m:0.}} />}
                </Box>
                </>)
            })}
            </ButtonGroup>
            </> : <></>
        }
        </>) : <>
        <TextField
                variant="standard"
                InputProps={{disableUnderline:true, style:{height:"32px",borderRadius:0, textAlign:"center"}}}
                inputProps={{style:{textAlign:"center"}}}
                margin="dense"
                sx={{ m:0.5, p:0, flex: 1, width:textWidth }}
                fullWidth
                disabled
            />
        </>} 
    </Paper>
    </Tooltip>
    )
}


export function StyledDropdown ({ id, label, value, onChange, options, capitalise=true, textFieldProps={}, ...props }) { 
    console.log(value)
    const do_capitalise = (s) => {
      return s.length > 0 ? s[0].toUpperCase() + s.substring(1) : ""
    }
    return (
      <StyledTextField id={id} label={label} select value={value} onChange={onChange} {...textFieldProps} {...props}>
        {!Array.isArray(options) ? 
            Object.keys(options).map(k => {
                return [
                    <ListSubheader height="40px" disableSticky disableGutters
                        sx={{fontFamily:"Scaly Sans", fontSize:18}} 
                        key={`${k}-header`} value={k}>
                        <Divider />
                        <Box sx={{p:0, pl:2, m:-0.5}}>
                            <Typography variant="statblockSection" fontSize={17}>{capitalise ? do_capitalise(k) : k}</Typography>
                        </Box>
                        <Divider />
                    </ListSubheader>,
                    options[k].map(s =>
                        <MenuItem key={`${k}-{label}-${s}`} value={s}>
                            <Typography variant="statblock" fontSize={16} lineHeight={1.2}>{capitalise ? do_capitalise(s) : s}</Typography>
                        </MenuItem>              
                    )
                ]})
             : 
            options.map((s) => 
                    (<MenuItem  key={`${label}-${s}`} value={s}>{capitalise ? do_capitalise(s) : s}</MenuItem>)
        )}
        </StyledTextField>
  )}

export function SkillField ( { skill, is_proficient, is_custom, is_default, default_value, set_value, skill_mod, onSkillChange, onValueChange, tooltip}) {
    
    if (is_proficient === undefined) {
        is_proficient = true
    }
    if (is_default === undefined) {
        is_default = true
    }

    const do_capitalise = (s) => {
        return s.length > 0 ? s[0].toUpperCase() + s.substring(1) : ""
      }

    let ability = SKILL_MAP[skill]
    let short_ability = SHORT_SKILL_ABILITY_MAP[skill]?.toUpperCase()
    if (ability === null || ability === undefined) {
        ability = skill
        short_ability = ""
    } else {
        ability = ability.toLowerCase()
    }

    console.log(skill_mod)
    const prof = is_proficient ? default_value - skill_mod : 0

    return (
        <Tooltip title={tooltip ? tooltip : ""}>
        <Paper
            sx={{ p: '0px 0px', display: 'flex', alignItems: 'center',  height:"40px", width:"100%",
                    marginBottom:0.5, marginTop:0.5, width:"auto",
                }}
            variant="outlined"
            square={true}
        >
            <Box sx={{flex:1, maxWidth:"70%", p:0, mr:1, justifyContent:"center"}}>
            {is_custom ? 
                <LazyTextField
                variant="standard"
                value={ability}
                onChange={onSkillChange}
                InputProps={{disableUnderline:true}}
                inputProps={{style:{alignSelf:"center", fontFamily:"Scaly Sans", fontSize:17}}}
                sx={{ m:0, p:1, mb:-0.5, flex: 1 }}
                fullWidth
                key={`styledtext-${skill.__custom_id}-textfield`}
            />
            :
                <Select
                    value={ability} 
                    onChange={onSkillChange}
                    disableUnderline={true} 
                    variant="standard"
                    sx={{m:0., ml:0.5, mr:0.5,p:0, flex:1, height:"40px", 
                        textAlign:"center", fontFamily:"Scaly Sans", fontSize:17,
                        width:"100%"
                    }} 
                    fullWidth
                >
                    {Object.keys(SKILLS).map(k => {
                        return [
                            <ListSubheader height="40px" disableSticky disableGutters
                                sx={{fontFamily:"Scaly Sans", fontSize:18}} 
                                key={`${k}-header`} value={k}>
                                <Divider />
                                <Box sx={{p:0, pl:2, m:-0.5}}>
                                    <Typography variant="statblockSection" fontSize={17}>{do_capitalise(k)}</Typography>
                                </Box>
                                <Divider />
                            </ListSubheader>,
                            SKILLS[k].map(s =>
                                <MenuItem key={`${k}-{label}-${s}`} value={s}>
                                    <Typography variant="statblock" fontSize={16} lineHeight={1.2}>{do_capitalise(s)}</Typography>
                                </MenuItem>              
                            )]
                    })}
                </Select>
            }
            </Box>
            <Divider orientation="vertical" sx={{height:40, m:0., ml:0, mr:1, p:0, w:5}} />
            <Box sx={{justifyContent:"center", ml:1, mr:1}}>
                <Typography variant="statblock" fontSize={16} lineHeight={1.2}
                    sx={{marginRight:1, textJustify:"left", width:120}}>
                        {`${default_value} (${short_ability}${is_proficient ? ' + ' : ''}${is_proficient ? prof : ""})`}
                </Typography>
            </Box>
            <Divider orientation="vertical" sx={{height:40, m:0., ml:0, mr:1, p:0, w:5}} />
            <TextField
                variant="standard"
                value={is_default ? "" : set_value}
                placeholder="Override"
                onChange={onValueChange}
                InputProps={{disableUnderline:true, color:"red"}}
                inputProps={{style:{textAlign:"center", fontFamily:"Scaly Sans Caps", fontSize:17}}}
                margin="dense"
                sx={{ m:0.6, p:0, pr:1, width:"80px", "& input::placeholder":{fontSize:14}}}
                fullWidth            
            />
        </Paper>
        </Tooltip>
    )
}