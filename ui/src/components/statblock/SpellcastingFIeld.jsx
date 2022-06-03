import PoppableField from "./PoppableField";
import { format_spellcasting } from "../../libs/creature_format";
import { Grid, Button } from "@mui/material";

import EditBlock from "./EditBlock";
import { LongText, Title } from "./ComplexParts";
import { StyledCheckbox, StyledDropdown, StyledTextField } from "./FormFields";
import { SHORT_ABILITIES } from "../../constants";
import { Add, Delete } from "@mui/icons-material";



const SPELL_LEVELS = ["cantrip", '1','2','3','4','5','6','7','8','9']
const SPELL_FREQUENCIES = ["will", "encounter", "daily", "rest", "weekly", "cantrip"]
function SpellLevelEdit( {spellLevel, setSpellLevel} ) {

    const setSpellLevelPart = (part) => (val) => {
        const sl = {...spellLevel}
        sl[part] = val
        setSpellLevel(sl)
    }
    
    const addSpell = (i) => () => {
        const spells = [...spellLevel.spells]
        spells.splice(i+1, 0, {name:""})
        setSpellLevelPart("spells")(spells)
    }

    const removeSpell = (i) => () => {
        const spells = [...spellLevel.spells]
        spells.splice(i, 1)
        setSpellLevelPart("spells")(spells)
    }

    const editSpell = (i, field) => (val) => {
        const spells = [...spellLevel.spells]
        spells[i][field] = val
        setSpellLevelPart("spells")(spells)
    }

    const is_levelled = spellLevel.level !== "unlevelled"

    console.log(spellLevel)
    return (<>
        {is_levelled ?<>
        <Grid item xs={4}>
            <StyledDropdown 
                label="Level" 
                options={SPELL_LEVELS} 
                value={spellLevel.level} 
                onChange={(e) => setSpellLevelPart("level")(e.target.value)}
            /> 
        </Grid>
        </>:
        <Grid item xs={4}>
            <StyledDropdown
                label="Frequency"
                options={SPELL_FREQUENCIES}
                value={spellLevel.frequency}
                onChange={(e) => setSpellLevelPart("frequency")(e.target.value)}
            />
        </Grid>
        }
        <Grid item xs={4}>
            <StyledTextField
                label="Slots"
                number
                value={spellLevel.slots}
                onChange={(e) => setSpellLevelPart("slots")(e.target.value)}
            />
        </Grid>
        <Grid item xs={4}>
            <StyledCheckbox
                label="Each"
                checked={spellLevel.each}
                onCheckChange={(e) => setSpellLevelPart("each")(e.target.checked)}
            />
        </Grid>
        {spellLevel.spells && spellLevel.spells.length > 0 ? <>
            {spellLevel.spells.map((sp,i) => {
                return (
                <Grid item container xs={12}>
                    <Grid item xs={6}>
                        <StyledTextField
                            label="Spell"
                            short
                            value={sp.name}
                            endButton={[<Add />, <Delete />]}
                            onEndButtonClick={[addSpell(i), removeSpell(i)]}
                            onChange={(e) => editSpell(i, "name")(e.target.value)}
                        />
                    </Grid>
                    <Grid item xs={3}>
                        {!is_levelled && <>
                            {sp.level !== null && sp.level !== undefined  ? 
                            <StyledDropdown
                                label="Level"
                                value={sp.level}
                                options={SPELL_LEVELS}
                                onChange={(e) => editSpell(i, "level")(e.target.value)}
                                endButton={[<Delete />]}
                                onEndButtonClick={[() => editSpell(i, "level")(undefined)]}
                            /> :
                            <Button sx={{height:"40px"}} startIcon={<Add />} 
                                    onClick={() => editSpell(i, "level")("1")}>Set Level</Button>
                        }</>}
                    </Grid>

                        {sp.post_text !== null && sp.post_text !== undefined  ?
                        <Grid item xs={12}>
                            <StyledTextField
                                label="Text"
                                short
                                value={sp.post_text}
                                onChange={(e) => editSpell(i, "post_text")(e.target.value)}
                                endButton={[<Delete />]}
                                onEndButtonClick={[() => editSpell(i, "post_text")(undefined)]}
                            /> 
                        </Grid>:
                        <Grid item xs={3}>
                            <Button sx={{height:"40px"}} startIcon={<Add />} 
                                onClick={() => editSpell(i, "post_text")("")}>Add Text</Button>
                        </Grid>
                        }
                    
                </Grid>)
            })}</>
            :
            <Grid item xs={4}>
                <Button sx={{height:"40px"}} startIcon={<Add />} 
                onClick={addSpell(0)}>Add Spell</Button>
            </Grid>
        }
    </>)
}

export default function SpellcastingField( {statblock, setStatblock, editable, resetFunc}) {
    

    const onReset = (i) => () => {
        resetFunc("spellcasting")(s => {
            const spells = [...statblock.spellcasting]
            spells[i] = s.spellcasting[i]
            return spells
        })
    }

    const setSpellPart = (i, part) => (val) => {
        setStatblock(s => {
            const spells = [...statblock.spellcasting]
            spells[i][part] = val
            return {...s, spellcasting:spells}
        })
    }

    const addSpellLevel = (i) => (j) => () => {
        const levels = [...statblock.spellcasting[i].levels]
        levels.splice(j+1, 0, {level:"cantrip", spells:[], frequency:"levelled"})
        setSpellPart(i, "levels")(levels)
    }

    const removeSpellLevel = (i) => (j) => () => {
        const levels = [...statblock.spellcasting[i].levels]
        levels.splice(j, 1)
        setSpellPart(i, "levels")(levels)
    }

    const setSpellLevel = (i) => (j) => (val) => {
        const levels = [...statblock.spellcasting[i].levels]
        levels[j] = val
        setSpellPart(i, "levels")(levels)
    }
    

    return (<>
        {statblock.spellcasting?.map((sp,i) => {
            return (<>
                <PoppableField text={format_spellcasting(sp)} editable={editable} onReset={onReset(i)}>
                    <EditBlock title="Spellcasting Configuration">
                        <Title title={sp.title} setTitle={setSpellPart(i, "title")} />
                        <LongText text={sp.text} setText={setSpellPart(i, "text")} />
                        <Grid item xs={4}>
                            <StyledDropdown
                                label="Ability"
                                value={sp.mod}
                                options={SHORT_ABILITIES}
                                onChange={(e) => setSpellPart(i, "mod")(e.target.value)}
                            />
                        </Grid>
                        <Grid item xs={4}>
                            <StyledTextField
                                label="Level"
                                value={sp.spellcastingLevel}
                                onChange={(e) => setSpellPart(i, "spellcastingLevel")(e.target.value)}
                            />
                        </Grid>
                        <Grid item xs={4}>
                            <StyledTextField
                                label="Save"
                                value={sp.save}
                                onChange={(e) => setSpellPart(i, "save")(e.target.value)}
                            />
                        </Grid>
                        <LongText text={sp.post_text} setText={setSpellPart(i, "post_text")} description="Final Text" />

                        {sp.levels && sp.levels.length > 0 ? 
                        <Grid item container spacing={0.3} xs={12}>
                            {sp.levels.map((sl,j) =>
                                <EditBlock title="Spell Configuration" onAdd={addSpellLevel(i)(j)} onDelete={removeSpellLevel(i)(j)}>
                                    <SpellLevelEdit spellLevel={sl} setSpellLevel={setSpellLevel(i)(j)} />
                                </EditBlock>
                            )}
                        </Grid> :
                        <Grid item xs={4}>
                            <Button sx={{height:"40px"}} startIcon={<Add />} 
                            onClick={addSpellLevel(i)(0)}>Add Spells</Button>
                        </Grid>
                        }

                    </EditBlock>
                </PoppableField>
                </>
            )
        })}
    </>)
}