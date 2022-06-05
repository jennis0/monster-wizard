import React, { useEffect, useState, useRef } from 'react';
import { Divider, List, ListItem, ListItemText, ListItemButton, ListSubheader, Pagination } from "@mui/material";
import SearchForm from './SearchForm';
import { Box } from '@mui/system';
import { Cost } from './statblock/ComplexParts';

export function sortByPage(s1, s2, reverse=false) {
    if (s1.source.page < s2.source.page) {
        return reverse ? -1 : 1
    } else if (s1.source.page > s2.source.page) {
        return reverse ? 1 : -1
    }
    return 0
}

export function sortByAlphabet(s1, s2, reverse=false) {
    return s1.name.localeCompare(s2.name) * reverse ? -1 : 1
}

export default function StatblockList( { 
    statblocks, sources, disabled, onClick, selected, 
    setStatblocks, defaultQuery, showSources=false, showErrors=true, perPage=-1,
    dense=false
  }) {

    const [page, setPage] = useState(1);
    const [sbs, setSbs] = useState(statblocks)
    const boxRef = useRef()


    const onSetPage = (event, value) => {
      setPage(value)
      boxRef.current.scrollTo(0, 0)
  }

    useEffect(() => {
      setPage(1)
    },[statblocks])

    useEffect(() => {
      console.log(perPage, )
      if(perPage > 0) {
        setSbs(statblocks?.slice((page-1)*perPage, Math.min(statblocks?.length, page*perPage)))
      } else {
        setSbs(statblocks)
      }
      
    }, [statblocks, page])

    const is_error = showErrors && statblocks?.map(sb => sb.modified_data.errors && Object.keys(sb.modified_data.errors).length > 0)

    console.log("sbs", sbs?.length, statblocks?.length)

    return (
      <Box sx={{height:"100%", alignContent:"center", textAlign:"center", aligItems:"center", width:"100%"}} ref={boxRef}>
      <List sx={{p:0, m:0}}
            subheader={<li />}
      >
        <ListSubheader key={`sb-item-search`} >
          <Box sx={{pt:"10px", pb:"10px", pr:1, pl:1}}>
          <SearchForm 
            defaultQuery={defaultQuery} 
            setResults={setStatblocks}
            sources={sources}
            disabled={disabled}
          />
          </Box>
        </ListSubheader>
        <Divider />

        {sbs?.map((sb_record,i) => {
          const sb = sb_record.modified_data
          let sb_source_text = null
          if (showSources) {
            const sb_source_candidates = sources.filter(s => s.id === sb_record.source)
            if (sb_source_candidates.length > 0) {
              sb_source_text = sb_source_candidates[0].title
            }
          }
          return (<>
            <ListItemButton 
              onClick={() => onClick(sb_record.id)} 
              selected={selected === i} 
              key={`sb-item-button-${sb.name}-${i}`} 
              sx={{pt:dense ? 0 : 1, pb:dense ? 0: 1, backgroundColor:is_error[i] ? "secondary.transparent" : null, m:0, 
                  "&.Mui-selected": {
                backgroundColor:!is_error[i] ? "primary.transparent" : "secondary.transparent"
              }}}
              >
                <ListItem key={`sb-item-${sb.name}-${i}`} sx={{pt:dense ? 0.2: 1, pb:dense ? 0.2:1}}>
                  <ListItemText 
                   primary={sb.name}
                   primaryTypographyProps={{variant:"statblock"}}
                   secondary={sb_source_text}
                  />
                </ListItem>
          </ListItemButton>
          <Divider sx={{backgroundColor: (is_error[i] || is_error[Math.min(i+1,is_error.length)]) ? "secondary.main" : null, opacity:0.5}}  />
            </>
              )})}
      </List>
      {perPage >= 0 &&
          <Pagination 
            count={Math.ceil(statblocks? statblocks.length /perPage : 1)} 
            page={page} 
            sx={{position:"relative", ml:"27%", mr:"27%"}}
            onChange={onSetPage}
            size="large"
            variant="text"
            shape="rounded"
          />
      }
      </Box>
    );
  }
  