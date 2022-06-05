import { Box } from "@mui/material";
import { LazyTextField } from "../FormFields";
import _ from 'lodash'


export default function StatblockTitle( {statblock, setStatblock, editable} ) {

    const onChange = (e) => {
        setStatblock(s => {
            const newS = _.cloneDeep(s)
            newS.name = e.target.value
            return newS
        })
    }

    console.log(statblock?.name)

    return (
        <Box width="100%" sx={{"&:hover": editable ? {backgroundColor:"primary.light"} : null}}>
            <LazyTextField
                  variant="standard"
                  placeholder="Title"
                  value={statblock?.name}
                  onChange={onChange}     
                  editable={editable}    
                  InputProps={{disableUnderline:true}}
                  inputProps={{
                      style:{ alignSelf:"left", fontFamily:"Mr Eaves Small Caps", 
                            fontSize:34, lineHeight:1}
                    }}
                  sx={{ m:0, p:0, mb:-0.5, width:"100%", 
                            input:{color:"primary.main", 
                                    "&:hover":editable ? {color:"primary.contrastText"}: null}}}
                  key={`styledtext-titlefield`}
            />
        </Box>
    )
}