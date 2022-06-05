import React, {useState, useEffect} from 'react';
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

import { useLocation, useNavigate } from 'react-router-dom';
import { useLiveQuery } from 'dexie-react-hooks';
import { db } from '../libs/db';
import { IconButton, LinearProgress, Stack, Typography } from '@mui/material';
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

export function NavDrawer(props) {
  const { window, pages } = props;
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const navigate = useNavigate()
  const location = useLocation()

  const uploads = useLiveQuery(() => db.uploads.toArray())

  const path = location.pathname.split("/")[1];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (<>
      <Box sx={{height:50, width:"100%"}}></Box>
      <Toolbar sx={{width:"100%"}}>
      </Toolbar>
      <List sx={{width:"100%", m:0, p:0}}>
        {pages.map(p => (
          <ListItem key={p.path} disablePadding={true} sx={{backgroundColor: path === p.path ? "primary.light" : null}}>
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
      
      <Box sx={{position:"absolute", bottom:"0", left:0, width:"100%"}}>
      {uploads && <ImportProgressViewer uploads={uploads}/>}
      </Box>
      </>
  );

  const container = window !== undefined ? () => window().document.body : undefined;

  return (
        <Drawer
          variant="permanent"
          PaperProps={{variant:"elevation", elevation:2}}
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              backgroundColor:"primary.main", 
              color:"background.default",
              width: drawerWidth,
              p:0, m:0
            },
          }}
          open
        >
          {drawer}
        </Drawer>
  );
}

NavDrawer.propTypes = {
  /**
   * Injected by the documentation to work in an iframe.
   * You won't need it on your project.
   */
  window: PropTypes.func,
};