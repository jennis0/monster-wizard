import React, {useEffect, useRef, useState} from 'react';
import { Divider, List, ListItem, ListItemText, ListItemButton, Stack, Box, Pagination } from "@mui/material";
import { ExpandMore } from '@mui/icons-material';
import Statblock from './statblock/EditableStatblock';
import { ExpandLess } from '@mui/icons-material';

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
    const boxRef = useRef()
    const [page, setPage] = useState(1);
    const [open, setOpen] = useState(null);
    const sbs = [...index];
    // if(sort) {
    //     sbs.sort(sort)
    // }

    useEffect(() => {
      setPage(1)
    }, [index])

    const onClick = (i) => () => {
      setOpen(open === i ? null : i)
    }

    const onSetPage = (event, value) => {
        setPage(value)
        boxRef.current.scrollTo(0, 0)
    }

    const perPage = 20;

    return (<Box sx={{width:"100%", height:"80vh", overflow:"auto"}} ref={boxRef}>
      <List sx={{p:0, m:0, width:"100%"}}>
        {sbs.slice((page-1)*perPage, Math.min(sbs.length, page*perPage)).map((sb,i) => (<>
            <ListItemButton sx={{height:80}}
              onClick={onClick(i)} 
              selected={open === i} 
              key={`sb-item-button-${sb.name}-${i}`}
            >
            <Stack>

                <ListItem key={`sb-item-${sb.modified_data.name}-${i}`}>
                  {open === i ? <ExpandLess sx={{mr:3}} /> : <ExpandMore sx={{mr:3}}/>}
                  <ListItemText primary={(<b>{sb.modified_data.name}</b>)} secondary={sources?.filter(s => s.id === sb.source)[0].title}/>
                </ListItem>
                  </Stack>
          </ListItemButton>
          {open === i ? <>
                  <Divider variant="middle" sx={{mb:0, mt:1.5}}/>
                  <Box sx={{m:2, p:2, backgroundColor:"#f5f5f5"}}>
                  <Statblock statblock={sb.modified_data} sx={{p:1}} editable={false}/> 
                  </Box>
                  </>: <></>
                  }
          <Divider />
            </>
              ))}
      </List>
      <Pagination 
        count={Math.ceil(index.length /perPage)} 
        page={page} 
        sx={{mt:2, position:"relative", left:0, marginLeft:"auto", marginRight:"auto", width:"450px", marginTop:4, marginBottom:4}} 
        onChange={onSetPage}
        size="large"
        variant="text"
        shape="rounded"
        />
      </Box>

    );
  }
  