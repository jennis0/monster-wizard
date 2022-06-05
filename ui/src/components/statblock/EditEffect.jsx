import { Button, Divider, Grid, Typography} from "@mui/material"
import {  DAMAGE_TYPES, CONDITIONS, SHORT_ABILITIES } from "../../constants";
import { Add,Delete } from "@mui/icons-material";

import { StyledTextAndOptField, StyledDropdown, StyledCheckbox, StyledTextField } from "../FormFields";
import { Damage, Roll } from "./ComplexParts";

export function EditEffect( {effect, setEffect, removeEffect} ) {

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
        if (newEffect[field]) {
            delete newEffect[field]
        } else {
            newEffect[field] = default_value
        }
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

    const setEffectPart = (part) => (val) => {
        const newEffect = {...effect}
        newEffect[part] = val
        setEffect(newEffect)
    }

    return (
            <>
                <Damage damage={effect.damage} setDamage={setEffectPart("damage")} />
                <Roll roll={effect.rolls} setRoll={setEffectPart("rolls")} />
                {effect.save ? 
                <Grid item xs={12} xl={8}>
                  <StyledTextAndOptField 
                    label="Save"
                    short
                    preText={"DC"}
                    textValue={effect.save ? effect.save.value : ""}
                    selectValue={effect.save ? effect.save.ability.toUpperCase() : ""}
                    onTextChange={setValue("save","value",true)}
                    onSelectChange={setValue("save","ability",false)}
                    options={SHORT_ABILITIES.map(a => a.toUpperCase())}
                    endButton={[<Delete />]}
                    onEndButtonClick={[addRemoveField("save", {"value":10, "ability":"wis"})]}
                   />
                </Grid> :
                <Grid item xs={6}>
                   <Button sx={{height:"40px"}} startIcon={<Add />} 
                        onClick={addRemoveField("save", {"value":10, "ability":"wis"})}>Add Save</Button>
                </Grid>
                }
                {effect.save ? 
                <Grid item xs={12} xl={4}>
                  <StyledCheckbox
                    label="Half damage on save" 
                    checked={effect.on_save ? effect.on_save === "half" : false}
                    onCheckChange={setHalfDamage}
                  /> 
                </Grid> : <></>}
                {effect.end_save ? 
                <Grid item xs={12}>
                    <StyledTextAndOptField 
                    label="Save to End"
                    preText={"DC"}
                    textValue={effect.end_save ? effect.end_save.value : ""}
                    selectValue={effect.end_save ? effect.end_save.ability.toUpperCase() : ""}
                    onTextChange={setValue("end_save","value",true)}
                    onSelectChange={setValue("end_save","ability",false)}
                    onCheckChange={addRemoveField("end_save", {"value":10, "ability":"wis"})}
                    options={SHORT_ABILITIES.map(a => a.toUpperCase())}
                    endButton={[<Delete />]}
                    onEndButtonClick={[addRemoveField("end_save", {"value":10, "ability":"wis"})]}
                    /> 
                </Grid>:
                <Grid item xs={6}>
                    <Button sx={{height:"40px"}} startIcon={<Add />}
                        onClick={addRemoveField("end_save", {"value":10, "ability":"wis"})}>Add Save to End
                    </Button>
                </Grid>
                    }


                {effect.conditions && effect.conditions.length > 0 ? effect.conditions.map((c,i) => (
                    <Grid item xs={12}>
                        <StyledDropdown  
                        label="Condition" 
                        options={CONDITIONS} 
                        value={c.condition}
                        onChange={updateStructField("conditions", i, "condition")}
                        textFieldProps={{endButton:[<Add />,<Delete />],
                                        onEndButtonClick:[addStructField("conditions", {"condition":""}), deleteStructField("conditions", i)]}}
                        />
                    </Grid>
                  )) : 
                  <Grid item xs={6}>
                    <Button sx={{height:"40px"}} label="test" onClick={addStructField("conditions", {"condition":""})} startIcon={<Add />} >Add Condition</Button>
                  </Grid>
                  }
                  
                  </>
    )
}
