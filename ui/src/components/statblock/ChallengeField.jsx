import { useEffect, useState } from "react";

import { format_cr } from "../../libs/creature_format";
import { StyledTextField } from "./FormFields";
import PoppableField from "./PoppableField";
import { Grid } from "@mui/material";
import EditBlock from "./EditBlock";

export default function ChallengeField ( {statblock, setStatblock, editable, resetFunc }) {

    const [lastState, setLastState] = useState(statblock.cr)

    useEffect(() => {
        setLastState(statblock.cr)
    }, [statblock])

    const onUpdateValue = (field) => (e) => {
        const cr = {...lastState}
        cr[field] = e.target.value

        if (isNaN(cr[field])) {
            cr[field] = 0
        }

        if (e.target.value.indexOf("/") > 0) {
            const parts = e.target.value.split("/")
            if (parts.length === 2 && parts[1].length > 0 && parts[0] === "1") {
                console.log(parts)
                cr[field] = Number(parts[0]) / Number(parts[1])
                console.log(cr[field])
                setStatblock({...statblock, cr:cr})
            } else {
                cr[field] = e.target.value
                setLastState(cr)
            }
        } else {
            cr[field] = Math.min(Number(e.target.value), 30)
            setStatblock({...statblock, cr:cr})
        }
    }

    const toggleField = (field) => () => {
        const cr = {...statblock.cr}
        if (cr[field] !== null && cr[field] !== undefined) {
            delete cr[field]
        } else {
            cr[field] = cr.cr
        }
        console.log(cr)
        setStatblock({...statblock, cr:cr})
    }

    const onReset = () => {
        resetFunc((sb) => {
            return sb.cr
          })
    }

    const challenge_text = (<><b>Challenge</b> {format_cr(statblock)}</>)
    return (
        <PoppableField text={challenge_text} editable={editable} onReset={onReset}>
            <EditBlock title="Challenge Rating">
                <Grid item xs={12} md={12} lg={3}>
                    <StyledTextField short label="CR" value={lastState?.cr} width="100%" onChange={onUpdateValue("cr")}/>
                </Grid>
                <Grid item xs={12} lg={4.5}>
                    <StyledTextField short checkbox checked={statblock.cr?.lair >= 0} onCheckChange={toggleField("lair")} label="Lair" value={lastState?.lair} onChange={onUpdateValue("lair")}/>
                </Grid>
                <Grid item xs={12} lg={4.5}>
                    <StyledTextField checkbox checked={statblock.cr?.coven >= 0} onCheckChange={toggleField("coven")} label="Coven" value={lastState?.coven} onChange={onUpdateValue("coven")}/>
                </Grid>
            </EditBlock>
        </PoppableField>
    )
}