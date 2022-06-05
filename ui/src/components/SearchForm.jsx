import { Button, Divider, Grid, IconButton, Stack, TextField, Typography } from "@mui/material"
import { Box } from "@mui/system"
import { useEffect, useState } from "react"
import { filterCR, filterType, filterSource, useStatblockSearch } from "../libs/search"
import { LazyTextField, StyledCheckbox, StyledMultiSelect, StyledTextField } from "./FormFields"

import { SIZES, TYPES } from "../constants"

import _ from 'lodash'
import { Clear, ExpandMore, Filter, FilterList } from "@mui/icons-material"


export default function SearchForm( 
    {
        defaultQuery={text:{value:"", opts:{name:true, action:true, feature:true}}}, 
        setResults, 
        sources,
        disabled=[]
    }) 
{
    const [filters, setFilters] = useState([]) 
    const [complexQuery, setComplexQuery] = useState(defaultQuery)
    const [open, setOpen] = useState(false)

    const results = useStatblockSearch(complexQuery)

    useEffect(() => {
        setResults(results)
    }, [results])

    const updateCQ = (key, is_list=false) => (val) => {
        console.log(val)
        setComplexQuery(cq => {
            const newCQ = {...cq}
            if (val && (!is_list || val.length > 0)) {
                _.set(newCQ, key, val)
            } else {
                _.unset(newCQ, key)
            }
            return newCQ
        })
    }

    const setTextOption = (opt) => () => {
        setComplexQuery(cq => {
            const newCQ = {...cq}
            if (!cq.text.opts) {
                newCQ.text.opts = {name:true, action:true, feature:true}
            }
            newCQ.text.opts[opt] = !newCQ.text.opts[opt]
            return newCQ
        })

    }

    
    console.log("cq", complexQuery)
    console.log(sources)

    return (
        <Stack sx={{m:0, p:0, width:"100%"}} spacing={2}>
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <Stack sx={{alignItems:"center", justifyContent:"end"}} direction="row" spacing={1}>
                        <StyledTextField
                            placeholder="Search Statblocks"
                            variant="standard"
                            sx={{ m:0, p:0, mb:-0.5, flex: 1 }}
                            fullWidth
                            defaultValue={complexQuery.text?.value} 
                            textProps={{placeholder:"Search Statblocks"}}
                            center={false}
                            onChange={(e) => {updateCQ("text.value")(e.target.value.toLowerCase())}}
                            endButton= {[
                                <FilterList sx={{color:"primary.main"}}/>
                            ]}
                            onEndButtonClick={[
                                () => setOpen(!open)
                            ]}
                        />

                    </Stack>
                </Grid> 
                {open && <>
                <Grid item xs={"auto"}>
                    <StyledCheckbox label="Search Name" long onCheckChange={setTextOption("name")} 
                    checked={complexQuery.text?.opts?.name}/>
                </Grid>
                <Grid item xs={"auto"}>
                    <StyledCheckbox label="Search Features"  long onCheckChange={setTextOption("feature")}
                    checked={complexQuery.text?.opts?.feature}/>
                </Grid>
                <Grid item xs={"auto"}>
                    <StyledCheckbox label="Search Actions"  long onCheckChange={setTextOption("action")}
                    checked={complexQuery.text?.opts?.action}/>
                </Grid>
                <Grid item xs={12}>
                    <Divider />
                </Grid>
                <Grid item width="250px" >
                    <Stack direction="row" spacing={2}>
                        <StyledTextField short label="Min CR" number value={complexQuery?.cr?.min} 
                            center={true}
                            disabled={disabled.indexOf("cr") >= 0}
                            onChange={e => updateCQ("cr.min")(Number(e.target.value))}/>
                        <StyledTextField short label="Max CR" number value={complexQuery?.cr?.max} 
                            center={true}
                            disabled={disabled.indexOf("cr") >= 0}
                            onChange={e => updateCQ("cr.max")(Number(e.target.value))}/>
                    </Stack>
                </Grid>
                <Grid item width="160px">
                    <StyledCheckbox label="Spellcasting" checked={complexQuery?.spellcasting} long
                        disabled={disabled.indexOf("spellcasting") >= 0}
                        onCheckChange={() => updateCQ("spellcasting")(complexQuery.spellcasting ? null : true)}
                    />
                </Grid>
                <Grid item minWidth="200px" maxWidth="100%">
                    <StyledMultiSelect short label="Type" options={TYPES} selected={complexQuery?.types}
                    disabled={disabled.indexOf("type") >= 0}
                        setSelected={s => updateCQ("types")(s)} 
                        endButton={[<Clear />]} onEndButtonClick={[() => updateCQ("types")(null)]}
                    />
                </Grid>
                <Grid item minWidth="200px" maxWidth="100%">
                    <StyledMultiSelect short label="Size" options={SIZES} selected={complexQuery?.sizes}
                        setSelected={s => updateCQ("sizes", true)(s)} 
                        disabled={disabled.indexOf("size") >= 0}
                        endButton={[<Clear />]} onEndButtonClick={[() => updateCQ("sizes")(null)]}
                    />
                </Grid>
                <Grid item minWidth="200px" maxWidth="100%">
                    <StyledMultiSelect short label="Source" options={sources?.map(s => s.title)} 
                        disabled={disabled.indexOf("source") >= 0}
                        selected={
                            sources?.filter(s => complexQuery.sources?.indexOf(s.id) >= 0).map(s => s.title)
                        }
                        setSelected={s => updateCQ("sources", true)(
                            s.map(title => sources?.filter(source => source.title === title)[0]).map(source => source.id)
                        )} 
                        endButton={[<Clear />]} onEndButtonClick={[() => updateCQ("sources")(null)]}
                    />
                </Grid>
                <Grid item xs={12}>
                <Divider />
                </Grid>
                </>}
            </Grid>
        </Stack>
    )
}