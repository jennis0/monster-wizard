import { Stack, Button, Paper, Divider, Typography} from "@mui/material"
import {  DAMAGE_TYPES, CONDITIONS, SHORT_ABILITIES } from "../../constants";
import { Add,Delete } from "@mui/icons-material";

import { StyledTextAndOptField, LabelledCheckboxField, StyledDropdown } from "./FormFields";

export function EffectPopper( {effect, setEffect, removeEffect} ) {

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
            delete newEffect[field]
        } else {
            newEffect[field] = default_value
        }
        setEffect(newEffect)
    }

    const addDamage = () => {
        const newEffect = {...effect}
        if (newEffect.damage === null || newEffect.damage === undefined) {
            newEffect.damage = []
        }
        newEffect.damage.push({"damage":{"average":"3", "formula":"1d6"}, "type":"slashing"})
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

    const addStructField = (field, default_value) => () => {
        const newEffect = {...effect}
        if (newEffect[field] === null || newEffect[field] === undefined) {
            newEffect[field] = []
        }
        newEffect[field].push(default_value)
        setEffect(newEffect)
    }

    const updateStructField = (field, i, subfield) => (e) => {
        const newEffect = {...effect}
        newEffect[field][i][subfield] = e.target.value
        setEffect(newEffect)
    }

    const deleteStructField = (field, i) => () => {
        const newEffect = {...effect}
        newEffect[field].splice(i,1)
        setEffect(newEffect)
    }

    console.log(effect)

    return (
        <Paper square variant="outlined" sx={{p:1, marginTop:1, alignItems:"center"}}>                  
                <Stack>
                  <Typography sx={{m:1, ml:0.5}}><b>Effect {1}</b></Typography>
                  <Button startIcon={<Add />} onClick={addStructField("damage")}>Add Damage</Button>
                {effect.damage ? effect.damage.map((ed,i) => (
                <StyledTextAndOptField 
                    label="Damage"
                    textValue={ed.damage.formula}
                    selectValue={ed.type}
                    onTextChange={setValue("damage","damage",true)}
                    onSelectChange={setValue("damage","type",false)}
                    endButton={<Delete />}
                    onEndButtonClick={deleteStructField("damage", i)}
                    options={DAMAGE_TYPES}
                    width="410px"
                    />))  : <></>
                }
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
                  <Button onClick={addStructField("conditions", {"condition":""})} startIcon={<Add />} >Add Condition</Button>
                  {effect.conditions ? effect.conditions.map((c,i) => (
                        <StyledDropdown  
                        label="Condition" 
                        options={CONDITIONS} 
                        value={c.condition}
                        onChange={updateStructField("conditions", i, "condition")}
                        textFieldProps={{endButton:(<Delete />),
                                        onEndButtonClick:deleteStructField("conditions", i)}}
                    />
                  )) : <></>}

                  <Divider />
                  <Button startIcon={<Delete />} sx={{mt:1}} onClick={removeEffect}>Remove Effect</Button>
                  </Stack>
                </Paper>
    )
}
