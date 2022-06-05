import React from 'react';
import { Divider, List, ListItem, ListItemText, ListItemButton, ListSubheader } from "@mui/material";
import SearchForm from './SearchForm';
import { Box } from '@mui/system';

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

export default function StatblockList( { statblocks, sources, disabled, onClick, selected, filter, setStatblocks, defaultQuery }) {

    const index = statblocks ? statblocks.filter(filter ? filter : () => true) : [];
    const sbs = [...index];
    // if(sort) {
    //     sbs.sort(sort)
    // }

    const is_error = statblocks?.map(sb => Object.keys(sb.errors).length > 0)

    console.log("sb list")

    return (
      <Box sx={{height:"100%"}}>
      <List sx={{p:0, m:0, height:"100%"}}
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

        {sbs.map((sb,i) => (<>
            <ListItemButton onClick={() => onClick(i)} selected={selected === i} key={`sb-item-button-${sb.name}-${i}`} 
              sx={{backgroundColor:is_error[i] ? "secondary.transparent" : null, m:0, 
                  "&.Mui-selected": {
                backgroundColor:!is_error[i] ? "primary.transparent" : "secondary.transparent"
              }}}>
                <ListItem key={`sb-item-${sb.name}-${i}`} sx={{"&.Mui-selected": {
                backgroundColor:"black"
              }}}>
                  <ListItemText primary={sb.name} primaryTypographyProps={{variant:"statblock"}}/>
                </ListItem>
          </ListItemButton>
          <Divider sx={{backgroundColor: (is_error[i] || is_error[Math.min(i+1,is_error.length)]) ? "secondary.main" : null, opacity:0.5}}  />
            </>
              ))}
      </List>
      </Box>
    );
  }
  