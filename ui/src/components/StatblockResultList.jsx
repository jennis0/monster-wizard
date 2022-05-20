import React, {useState} from 'react';
import { Divider, List, ListItem, ListItemText, ListItemButton, Stack, Box } from "@mui/material";
import { ExpandMore } from '@mui/icons-material';
import Statblock from './EditableStatblock';

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

export default function StatblockList( { title, sources, statblocks, selected, filter, sort }) {

    const index = statblocks ? statblocks.filter(filter ? filter : () => true) : [];
    const [open, setOpen] = useState(null);
    const sbs = [...index];
    // if(sort) {
    //     sbs.sort(sort)
    // }

    const onClick = (i) => () => {
      setOpen(open === i ? null : i)
    }

    return (
      <List sx={{p:0, m:0, width:"50%"}}>
        {sbs.map((sb,i) => (<>
            <ListItemButton
              onClick={onClick(i)} 
              selected={selected === i} 
              key={`sb-item-button-${sb.name}-${i}`}>
                                <Stack>

                <ListItem key={`sb-item-${sb.data.name}-${i}`}>
                  <ExpandMore />
                  <ListItemText primary={sb.data.name} secondary={sources?.filter(s => s.id === sb.source)[0].title}/>
                </ListItem>
                {open === i ? 
                  <Statblock statblock={sb.data}/> : <></>
                  }
                  </Stack>
          </ListItemButton>
          <Divider />
            </>
              ))}
      </List>
    );
  }
  