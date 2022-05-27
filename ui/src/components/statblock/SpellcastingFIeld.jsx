import PoppableField from "./PoppableField";
import { format_spellcasting } from "../../libs/creature_format";
import { Box } from "@mui/material";



export default function SpellcastingField( {statblock, setStatblock}) {
    console.log(statblock.spellcasting)
    return (<>
        {statblock.spellcasting?.map(sp => {
            return (<>
                <PoppableField text={format_spellcasting(sp)}>
                </PoppableField>
                </>
            )
        })}
    </>)
}