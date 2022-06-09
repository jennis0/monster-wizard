import React, {useState, useEffect, useReducer, useRef} from 'react';
import PropTypes from 'prop-types';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Toolbar from '@mui/material/Toolbar';
import { Menu as MenuIcon } from '@mui/icons-material';

import { useLocation, useNavigate } from 'react-router-dom';
import { useLiveQuery } from 'dexie-react-hooks';
import { db } from '../libs/db';
import { AppBar, Dialog, DialogContent, IconButton, LinearProgress, Menu, Paper, Stack, Typography } from '@mui/material';
import { ImportProgress } from './Loader';
import { ExpandLess, ExpandMore } from '@mui/icons-material';
import { get_request_status } from '../libs/upload';


const drawerWidth = 240;

function ImportProgressViewer( {uploads} ) {
  const [open, setOpen] = useState(uploads?.length > 0)
  const navigate = useNavigate()
  
  useEffect(() => {
    const timer = setTimeout(() => get_request_status(uploads), open ? 1e3 : 1e4)
    return () => clearTimeout(timer)
   })

  const goTo = (id) => (e) => {
    navigate(`/sources/${id}`)
  }

  return (
    <Box sx={{width:"100%", m:0, p:0, alignItems:"end", direction:"column"}}>
    {uploads && uploads.length > 0 ? 
    <>
    <Divider sx={{mb:0}}/>
      <Box onClick={() => setOpen(!open)} 
        sx={{w:"100%", alignItems:"center", justifyContent:"space-between", display:"flex", p:1,
        "&:hover":{backgroundColor:"primary.dark"}}}
      >
        <Typography variant="nav">Import Progress</Typography>
        {open ? <ExpandLess sx={{color:"background.default"}}/> : <ExpandMore sx={{color:"background.default"}}/>}
      </Box>
    {open ? 
    <>
    <Divider sx={{mb:0}}/>
      <List sx={{width:"100%", m:0, mt:-1, p:2, height:"400px", overflowY:"auto"}} disablePadding={true} disableGutters={true}>
        {uploads?.map(u => {
          return (<>
          {u.status === "finished" ? 
            <ListItemButton key={u.id} onClick={goTo(u.id)} sx={{m:0, p:0, pl:1, pr:1, pt:0.5, mt:-1, ml:-2, mr:-2, mb:1, "&:hover":{backgroundColor:"primary.dark"}}} >
              <ListItem sx={{m:0, p:0}} disableGutters>
              <Stack sx={{width:"100%"}} spacing={0}>
                <Box sx={{width:"100%"}}>
                <ListItemText primaryTypographyProps={{fontFamily:"Scaly Sans", fontSize:13}}
                  primary={u.source?.title}/>
                </Box>
                <Box sx={{w:"100%"}}>
                  <ImportProgress upload={u} />
                </Box>
              <Divider sx={{mt:1.5, h:5, ml:-2, mr:-2}}/>
              </Stack>
            </ListItem>
          </ListItemButton>
            :
            <ListItem key={u.id} sx={{m:0, p:0}}>
            <Stack sx={{width:"100%"}} spacing={0}>
              <Box sx={{width:"100%", mt:-1}}>
              <ListItemText primaryTypographyProps={{fontFamily:"Scaly Sans", fontSize:13}}
                primary={u.source?.title}/>
              </Box>
              <Box sx={{w:"100%"}}>
                <ImportProgress upload={u} />
              </Box>
            <Divider sx={{mt:1, mb:1, h:5, ml:-2, mr:-2 }}/>
            </Stack>
          </ListItem>
          }</>
          

        )})}
      </List></> : <></>}
      <Divider sx={{mb:0}}/>
    </>: <></>}
    </Box>
  )
}

function LinksMenu( {pages} ) {
  const location = useLocation()
  const navigate = useNavigate()
  const currentPath = location.pathname.split("/")[1]; 

  return (
    <List sx={{width:"100%", m:0, p:0}}>
    {pages?.map(p => (
      <ListItem key={p.path} disablePadding={true} sx={{backgroundColor: currentPath === p.path ? "primary.light" : null}}>
        <ListItemButton onClick={() => {navigate(`/${p.path}`)}}>
          <ListItemIcon sx={{color:'background.default'}}>
            {p.icon}
          </ListItemIcon>
          <ListItemText primaryTypographyProps={{variant:"nav"}} primary={p.label} />
        </ListItemButton>
        <Divider />

      </ListItem>

    ))}
  </List>
  )
}

function AppBarNav( {openDrawer}) { 
  return (
    <Box sx={{p:0, m:0}}>
      <AppBar sx={{p:0, m:0}}>
        <Toolbar sx={{p:0}}>
          <IconButton
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ ml:1, mr: 2 }}
            onClick={() => openDrawer(true)}
          >
            <MenuIcon sx={{color:"primary.contrastText"}}/>
          </IconButton>
        </Toolbar>
      </AppBar>
    </Box>
  );
}

function DrawerNav( {pages, variant, open, setOpen} ) {
  const uploads = useLiveQuery(() => db.uploads.toArray())

  console.log("drawer", open)

  return (
      <Drawer
        variant={variant}
        anchor="left"
        // PaperProps={{variant:"elevation", elevation:2}}
        sx={{
          display: "block",
          '& .MuiDrawer-paper': {
            backgroundColor:"primary.main", 
            color:"background.default",
            width: drawerWidth,
            p:0, m:0
          },
        }}
        open={open}
        onClose={() => setOpen(false)}
      >
        <Box sx={{width:"100%", height:"100px", p:3}}>
          {/* <Stack direction="row" alignItems="center" spacing={2}>
            <img src="/icons/logo-transparent.png" height="60px" />
            <Typography color="secondary" variant="nav" fontSize={30}>INDEX</Typography>
          </Stack> */}
        </Box>
        <LinksMenu pages={pages} />
        <Box sx={{position:"absolute", bottom:"0", left:0, width:"100%"}}>
          {uploads && <ImportProgressViewer uploads={uploads}/>}
        </Box>
      </Drawer>
  )
}


export function NavDrawer( {pages, persistant}) {
  const [drawerOpen, setDrawerOpen] = useState(false)

  // useEffect(() => {
  //   setDrawerOpen(persistant)
  // },[persistant])

  console.log(persistant, drawerOpen)

  return (<>
    {!persistant && <AppBarNav openDrawer={setDrawerOpen}/>}
    <DrawerNav 
      open={drawerOpen} setOpen={setDrawerOpen} pages={pages} 
      variant={persistant ? "permanent" : "temporary"}
    />
    </>
  );
}