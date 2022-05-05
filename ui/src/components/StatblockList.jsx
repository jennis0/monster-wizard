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

    const index = statblocks && statblocks.creatures ? statblocks.creatures.filter(filter ? filter : () => true) : [];
    const sbs = [...index];
    // if(sort) {
    //     sbs.sort(sort)
    // }

    console.log(sbs)

    return (
      <List
        sx={{
          maxWidth:400,
          bgcolor: 'background.paper',
        }}
      >
        {title ? <>
        <ListItem key={`item-header-${statblocks.source?.title?.name}`} sx={{topMargin:"10px", bottomMargin:"10px"}}>
            <ListItemText align="center">
                {title}
            </ListItemText>
        </ListItem>
        <Divider /></> : <></>
        }

        {sbs.map((sb,i) => (<>
            <ListItemButton onClick={() => onClick(i)} selected={selected === i}>
                <ListItem key={`item-${sb.name}-${i}`}>
                  <ListItemText primary={sb.name} />
                </ListItem>
          </ListItemButton>
                          <Divider />
                          </>
              ))}
      </List>
    );
  }
  