import { format_action } from "../../libs/creature_format"
import TitleField from "./TitleField"

import { Stack } from "@mui/material"
import PoppableField from "./PoppableField"

const action_type_map = {
    "action":"Actions",
    "bonus":"Bonus Actions",
    "legendary":"Legendary Actions",
    "reaction":"Reactions",
    "lair":"Lair Actions",
    "mythic":"Mythic Actions"
}

function ActionTypeField( { type, actions, onAdd, editable}) {
    return (<>
        <TitleField text={action_type_map[type]} editable={editable} onAdd={onAdd} />
        <Stack spacing={2}>
            {actions.map(action => { 
                return (
                    <PoppableField text={format_action(action)} editable={editable} >

                    </PoppableField>
                )
            })}
        </Stack>
        </>
    )
}

export default function ActionField( {statblock, setStatblock, editable } ) {
    return (<>
        {["action", "bonus", "reaction", "legendary"].map(a => {
            if (statblock[a]) {
                return (<>
                    <ActionTypeField type={a} actions={statblock[a]} onAdd={() => {}} editable={editable} />
                    </>
                )
            } else if (editable) {
                return <TitleField text={action_type_map[a]} editable={editable} onAdd={null} />
            }
        })}
    </>)
}