import { Add, Delete } from "@mui/icons-material"
import { Grid, Button, Paper, TextField } from "@mui/material"
import { DAMAGE_TYPES, MEASURES, TIME_MEASURES } from "../../constants"
import EditBlock from "./EditBlock"
import { EditEffect } from "./EditEffect"
import { StyledTextAndOptField, StyledTextField, StyledDropdown, StyledRangeField, LazyTextField } from "./FormFields"

const DEFAULT_ROLL = {formula:"0", average:"0"}
export function Roll( {roll, setRoll }) {

    const addRoll = (i) => () => {
        if (!roll) {
            setRoll([{...DEFAULT_ROLL}])
        } else {
            const newRoll = [...roll]
            newRoll.splice(i+1, 0, {...DEFAULT_ROLL})
            setRoll(newRoll)
        }
    }

    const removeRoll = (i) => () => {
        const newRoll = [...roll]
        newRoll.splice(i, 1)
        setRoll(newRoll)
    }

    const updateRoll = (i, field, is_num) => (e) => {
        const newRoll = [...roll]
        if (is_num) {
            newRoll[i][field] = Number(e.target.value)
        } else {
            newRoll[i][field] = e.target.value
        }
        setRoll(newRoll)
    }

    return (<>
        {roll && roll.length > 0 ? roll.map((ed,i) => (
            <Grid item xs={12}>
                <StyledTextField 
                    label="Roll"
                    textValue={ed.formula}
                    onTextChange={updateRoll("roll",true)}
                    endButton={[<Add />,<Delete />]}
                    onEndButtonClick={[addRoll(i), removeRoll(i)]}
                />
            </Grid>))  :                   
            (<Grid item xs={6}>
                <Button sx={{height:"40px"}} startIcon={<Add />} 
                        onClick={addRoll(0)}>Add Roll</Button>
            </Grid>)}
        </>
    )
}

const DEFAULT_DAMAGE = {damage:{formula:"0", average:"0"}, type:""}
export function Damage( {damage, setDamage, versatile=false}) {

    const addDamage = (i) => () => {
        if (!damage) {
            setDamage([{...DEFAULT_DAMAGE}])
        } else {
            const newDamage = [...damage]
            newDamage.splice(i+1, 0, {...DEFAULT_DAMAGE})
            setDamage(newDamage)
        }
    }

    const removeDamage = (i) => () => {
        const newDamage = [...damage]
        newDamage.splice(i, 1)
        setDamage(newDamage)
    }

    const updateDamage = (i, field, is_num) => (e) => {
        const newDamage = [...damage]
        if (is_num) {
            newDamage[i][field] = Number(e.target.value)
        } else {
            newDamage[i][field] = e.target.value
        }
        setDamage(newDamage)
    }

    return (<>
        {damage && damage.length > 0 ? damage.map((ed,i) => (
            <Grid item xs={12}>
                <StyledTextAndOptField 
                    label={versatile ? "Versatile" : "Damage"}
                    textValue={ed.damage.formula}
                    selectValue={ed.type}
                    onTextChange={updateDamage("damage",true)}
                    onSelectChange={updateDamage("type",false)}
                    endButton={[<Add />,<Delete />]}
                    onEndButtonClick={[addDamage(i), removeDamage(i)]}
                    options={DAMAGE_TYPES}
                />
            </Grid>))  :                   
            (<Grid item xs={6}>
                <Button sx={{height:"40px"}} startIcon={<Add />} 
                        onClick={addDamage(0)}>{versatile ? "Add Versatile Damage" : "Add Damage"}</Button>
            </Grid>)}
        </>
    )
}

export function Uses( {uses, setUses}) {

    const addRemoveUses = (e) => {
        if (uses) {
            setUses(null)
        } else {
            setUses({slots:0, period:"day"})
        }
    }

    const updateUses = (field, is_num) => (e) => {
        const newUses = {...uses}
        if (is_num) {
          uses[field] = Number(e.target.value)
        } else {
          uses[field] = e.target.value
        }
        setUses(newUses)
    }

    return (<>
        {uses ? 
        <Grid item xs={12} lg={6}>
            <StyledTextAndOptField 
                label="Uses"
                textValue={uses.slots}
                number
                short
                onCheckChange={addRemoveUses}
                onTextChange={updateUses("slots")}
                onSelectChange={updateUses("period")}
                midText="per"
                selectValue={uses.period.replaceAll("_"," ")}
                options={TIME_MEASURES.map(s =>  s.replaceAll("_"," "))}
                width="100%"
                key={`field-uses`}
                endButton={[<Delete />]}
                onEndButtonClick={[addRemoveUses]}
                />
        </Grid> :
        <Grid item xs={12} lg={6}>
            <Button sx={{height:"40px"}} startIcon={<Add />} 
                    onClick={addRemoveUses}>Add Uses</Button>
        </Grid>
        }</>
    )
}

export function Recharge( {recharge, setRecharge}) {

    const addRemoveRecharge = (e) => {
        if (recharge) {
            setRecharge(null)
        } else {
            setRecharge({from:6, to:6})
        }
    }

    const updateRecharge = (e) => {
        const newRecharge = {...recharge}
        recharge["from"] = Number(e.target.value)
        setRecharge(newRecharge)
    }

    return (<>
        {recharge ? 
        <Grid item xs={12} lg={6}>
            <StyledTextField 
                label="Recharge"
                value={recharge.from}
                onCheckChange={addRemoveRecharge}
                onTextChange={updateRecharge}
                midText="per"
                width="100%"
                key={`field-recharge`}
                endButton={[<Delete />]}
                onEndButtonClick={[addRemoveRecharge]}
                />
        </Grid> :
        <Grid item xs={12} lg={6}>
            <Button sx={{height:"40px"}} startIcon={<Add />} 
                    onClick={addRemoveRecharge}>Add Recharge</Button>
        </Grid>
        }</>
    )
}

export function Cost( {cost, setCost}) {

    const addRemoveCost = (e) => {
        if (cost) {
            setCost(null)
        } else {
            setCost(1)
        }
    }

    const updateCost = (e) => {
        const newCost = {...cost}
        cost["from"] = Number(e.target.value)
        setCost(newCost)
    }

    return (<>
        {cost ? 
        <Grid item xs={12} lg={6}>
            <StyledTextField 
                label="Cost"
                value={cost}
                onCheckChange={addRemoveCost}
                onTextChange={updateCost}
                midText="per"
                width="100%"
                key={`field-cost`}
                endButton={[<Delete />]}
                onEndButtonClick={[addRemoveCost]}
                />
        </Grid> :
        <Grid item xs={12} lg={6}>
            <Button sx={{height:"40px"}} startIcon={<Add />} 
                    onClick={addRemoveCost}>Add Cost</Button>
        </Grid>
        }</>
    )
}

export function Title( {title, setTitle }) {

    const updateTitle = (e) => {
        setTitle(e.target.value)
    }

    return (
        <Grid item xs={12}>
        <StyledTextField 
            id="field-title-text"
            placeholder="Title"
            short
            label="Title" 
            value={title} 
            onChange={updateTitle} 
            key={`field-titlebox`}
            width="100%"
        />
    </Grid>
    )
}

export function LongText( {text, setText, description="Descriptive Text"} ) {
    const updateText = (e) => {
        setText(e.target.value)
    }

    return (
        <Grid item xs={12}>
        <Paper variant="outlined" sx={{p:1}} square>
            <LazyTextField
                value={text} 
                placeholder={description}
                multiline
                maxRows={100}
                variant="standard"
                InputProps={{disableUnderline:true}}
                sx={{width:"100%"}}
                onChange={updateText}
                key={`field-textbox`}
            />
        </Paper>
    </Grid>
    )
}


export function OptionalEffects ( { effects, setEffects, postText="", preTitle="" } ) {

    const addEffect = (i) => () => {
        if (!effects) {
            setEffects([{}])
        } else {
            const newEffects = [...effects]
            newEffects.splice(i+1, 0, {})
            setEffects(newEffects)
        }
    }

    const removeEffect = (i) => () => {
        const newEffects = [...effects]
        newEffects.splice(i, 1)
        setEffects(newEffects)
    }

    const updateEffect = (i) => (e) => {
        const newEffects = [...effects]
        newEffects[i] = e
        setEffects(newEffects)
    }

    console.log("effects", effects)

    return (<>
        {effects && effects.length > 0 ? 
        <Grid item container spacing={0.3} xs={12}>
            {effects.map((e,j) =>
                <EditBlock title={`${preTitle}Effect ${j+1}`} onAdd={addEffect(j)} onDelete={removeEffect(j)}>
                    <EditEffect 
                        effect={e} 
                        setEffect={updateEffect(j)} 
                        removeEffect={removeEffect(j)} 
                        key={`effects-field-${j}`}
                    />
                </EditBlock>
            )}
        </Grid> :
               <Grid item xs={12} lg={6}>
               <Button sx={{height:"40px"}} startIcon={<Add />} 
                       onClick={addEffect(0)}>Add Effect {postText}</Button>
           </Grid>
        }
        </>
    )
}

export function Attack ( {attack, setAttack} ) {

    const removeAttack = () => {
        setAttack(null)
    }

    const addAttack = () => {
        setAttack({
            "type":"melee",
            "weapon":"weapon",
            "reach":{distance:5, "measure":"ft"},
            "hit":0,
            "target":{count:1},
        })
    }

    const setAttackPart = (part) => (val) => {
        const newAttack = {...attack}
        newAttack[part] = val
        setAttack(newAttack)
    }

    const setAttackType = (val) => {
        const newAttack = {...attack}
        newAttack.type = val
        if (val === "melee") {
            if (attack.range) {
                delete newAttack.range
            }
        }
        if (val === "ranged") {
            if (attack.reach) {
                delete newAttack.reach
            }
        }
        if (val === "ranged" || val === "both") {
            if (!attack.range) {
                newAttack.range = {short_distance:30, long_distance:120, measure:"ft"}
            }
        }
        if (val === "melee" || val === "both") {
            if (!attack.reach) {
                newAttack.reach = {distance:5, measure:"ft"}
            }
        }
        setAttack(newAttack)
    }

    const setRange = (field) => (e) => {
        const range = attack.range
        if (!range) {
            setAttackPart("range")({short_distance:30, long_distance:120, measure:"ft"})
        } else {
            const newRange = {...range}
            newRange[field] = e.target.value
            setAttackPart("range")(newRange)
        }
    }

    const setTarget = (field) => (e) => {
        let newTarget = {}
        if (attack.target) {
            newTarget = {...attack.target}
        } else {
            newTarget = {count:1, type:"target"}
        }
        newTarget[field] = e.target.value
        setAttackPart("target")(newTarget)
    }

    console.log("attack", attack)

    return (<>
        {attack ?
        <EditBlock title="Attack Configuration" onDelete={removeAttack}>
        <Grid item xs={6}>
            <StyledDropdown 
                label="Type" 
                options={["melee", "ranged", "both"]} 
                value={attack.type}
                onChange={(e) => setAttackType(e.target.value)}
            />
        </Grid>
        <Grid item xs={6}>
            <StyledDropdown 
                label="Weapon" 
                options={["weapon", "spell"]}
                value={attack.weapon}
                onChange={(e) => setAttackPart("weapon")(e.target.value)}
             />
        </Grid>
        <Grid item xs={3}>
            <StyledTextField
                label="To Hit"
                value={attack.hit}
                onChange={(e) => setAttackPart("hit")(e.target.value)}
            />
        </Grid>
        {attack.type === "melee" || attack.type === "both" ? 
        <Grid item xs={4}>
        <StyledTextAndOptField 
            label="Reach"
            textValue={attack.reach.distance}
            selectValue={attack.reach.measure}
            options={MEASURES}
        /> </Grid>:
         <></>
        }
        {attack.type === "ranged" || attack.type === "both" ? 
        <Grid item xs={6}>
        <StyledRangeField
            range={attack.range}
            onChange={setRange}
        />
        </Grid>:
         <></>
        }

        <Grid item xs={5}>
            <StyledTextAndOptField 
                label="Target"
                textValue={attack.target?.count}
                onTextChange={setTarget("count")}
                selectValue={attack.target?.type}
                onSelectChange={setTarget("type")}
                options={["creature", "target", "object"]}
            />
        </Grid>
        <Damage damage={attack.damage} setDamage={setAttackPart("damage")} />
        <Damage damage={attack.versatile} setDamage={setAttackPart("versatile")} versatile />
        <OptionalEffects effects={attack.effects} setEffects={setAttackPart("effects")} 
            postText={" On Attack"} preTitle={"Attack "}/>
        </EditBlock> :
        <Grid item xs={6}>
            <Button sx={{height:"40px"}} startIcon={<Add />} 
                       onClick={addAttack}>Add Attack</Button>
        </Grid>
        }</>
    )
}