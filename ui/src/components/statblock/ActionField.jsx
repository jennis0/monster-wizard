import { format_action, title_with_uses } from "../../libs/creature_format"
import TitleField from "./TitleField"

import { Grid, Stack } from "@mui/material"
import PoppableField from "./PoppableField"
import { useEffect } from "react"
import EditBlock from "./EditBlock"
import { Attack, Cost, LongText, OptionalEffects, Recharge, Title, Uses } from "./ComplexParts"
import { StyledDropdown } from "./FormFields"
import { reparse_action } from "../../libs/api"


const action_type_map = {
    "action":"Actions",
    "bonus":"Bonus Actions",
    "legendary":"Legendary Actions",
    "reaction":"Reactions",
    "lair":"Lair Actions",
    "mythic":"Mythic Actions"
}

function make_new_action(actionType) {
    return {
        "title":`New ${action_type_map[actionType].slice(0, -1)}`,
        "text":"",
        "type":actionType
    }
}

function ActionEditBlock( {action, setAction} ) {

    const setActionPart = (part) => (val) => {
        console.log("setting action part")
        const newAction = {...action}
        newAction[part] = val
        setAction(newAction)
    }

    return (
        <>
        <Title title={action.title} setTitle={setActionPart("title")} />
        <LongText text={action.text} setText={setActionPart("text")} />
        {action.type === "legendary" && <Cost cost={action.cost} setCost={setActionPart("cost")} />}
        <Uses uses={action.uses} setUses={setActionPart("uses")} />
        <Recharge recharge={action.recharge} setRecharge={setActionPart("recharge")} />
        <Attack attack={action.attack} setAttack={setActionPart("attack")} />
        <OptionalEffects effects={action.effects} setEffects={setActionPart("effects")} postText={"On Action"} />
        </>
    )
}

function ActionTypeField( { type, setAction, actions, onAdd, onDelete, editable, onReset, onResetAll}) {

    const regenerateEffects = (i) => () => {
        const title = title_with_uses(actions[i])
        reparse_action(type, title, actions[i].text, 
            (r => {
                console.log(r)
                setAction(i)(r)
            }))
        }

    return (<>
        <TitleField text={action_type_map[type]} editable={editable} onAdd={onAdd(actions.length)} onReset={onResetAll}/>
        <Stack spacing={2}>
            {actions.map((action, i) => { 
                return (
                    <PoppableField text={format_action(action)} editable={editable} onReset={onReset(i)} onGenerate={regenerateEffects(i)}>
                        <EditBlock title={"Action"} onDelete={onDelete(i)}>
                            <ActionEditBlock action={action} setAction={setAction(i)} />
                        </EditBlock>
                    </PoppableField>
                )
            })}
        </Stack>
        </>
    )
}

export default function ActionField( {statblock, setStatblock, editable, resetFunc } ) {

    useEffect(() => {
        if (!statblock.deleted_actions) {
            console.log("Resetting deleted actions")
            setStatblock(s => {
                return {...s, deleted_actions:{"action":{}, "bonus":{}, "reaction":{}, "legendary":{}}}
            })
        }
    },[statblock])

    const onReset = (resetFunc, actionType) => (i) => () => {
        resetFunc(s => {
            const actions = [...statblock[actionType]]
            actions[i] = s[actionType][i]
            return actions
        })
    }

    const onResetAll = (resetFunc, actionType) => () => {
        resetFunc(sb => {
            setStatblock(s => {
                const del_a = {...s.deleted_actions}
                del_a[actionType] = {}
                return {...s, deleted_actions: del_a}
            })
            return sb[actionType]
        })
    }

    const addAction = (actionType) => (i) => () => {
        setStatblock(s => {
            const newS = {...s}
            if (!newS[actionType]) {
                newS[actionType] = [make_new_action(actionType)]
            } else {
                newS[actionType].splice(i+1, 0, make_new_action(actionType))
            }
            return {...newS}
        })
    }

    const removeAction = (actionType) => (i) => () => {
        setStatblock(s => {
            const newS = {...s}
            newS[actionType].splice(i, 1)
            return {...newS}
        })
    }

    const setAction = (actionType) => (i) => (val) => {
        console.log("setting action")
        const newSb = {...statblock}
        newSb[actionType][i] = val
        setStatblock({...newSb})
    }

    return (<>
        {["action", "bonus", "reaction", "legendary"].map(a => {
            if (statblock[a]) {
                return (
                    <ActionTypeField 
                        type={a} 
                        actions={statblock[a]} 
                        editable={editable} 
                        onReset={onReset(resetFunc(a), a)}
                        onResetAll={onResetAll(resetFunc(a), a)}
                        onAdd={addAction(a)}
                        onDelete={removeAction(a)}
                        setAction={setAction(a)}
                    /> 
                )
            } else if (editable) {
                return <TitleField text={action_type_map[a]} editable={editable} onAdd={addAction(a)(0)} onReset={onResetAll(a)} />
            }
        })}
    </>)
}