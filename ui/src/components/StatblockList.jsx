import React from 'react';
import { Divider, List, ListItem, ListItemText, ListItemButton } from "@mui/material";

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

export default function StatblockList( { title, statblocks, onClick, selected, filter, sort }) {

    const index = statblocks ? statblocks.filter(filter ? filter : () => true) : [];
    const sbs = [...index];
    // if(sort) {
    //     sbs.sort(sort)
    // }

    const is_error = statblocks.map(sb => Object.keys(sb.errors).length > 0)

    return (
      <List sx={{p:0, m:0}}>
        {title ? <>
        <ListItem key={`sb-item-header-${title}`} sx={{topMargin:"10px", bottomMargin:"10px"}}>
            <ListItemText align="center" primaryTypographyProps={{variant:"statblock"}} primary={title} /> 
        </ListItem>
        <Divider sx={{".MuiDivider-root":{color:"pink", backgroundColor:"pink", background:"pink"}}}/></> : <></>
        }

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
          <Divider sx={{backgroundColor: (is_error[i] || is_error[Math.min(i+1,is_error.length)]) ? "secondary.main" : "primary.main", opacity:0.5}}  />
            </>
              ))}
      </List>
    );
  }
  