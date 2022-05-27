import * as React from 'react';
import PropTypes from 'prop-types';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import {  Paper, Typography } from '@mui/material';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import MailIcon from '@mui/icons-material/Mail';
import Toolbar from '@mui/material/Toolbar';

import { useLocation, useNavigate } from 'react-router-dom';


const drawerWidth = 240;

export function NavDrawer(props) {
  const { window, pages } = props;
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const navigate = useNavigate()
  const location = useLocation()

  const path = location.pathname.split("/")[1];
  console.log(path)

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (<>
      <Box sx={{height:50}}></Box>
      <Toolbar>
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
      <Box sx={{position:"absolute", top:"95%"}}>
        <img src="/icons/homebrew_banner.webp" width={250}/>
      </Box>
      </>
  );

  const container = window !== undefined ? () => window().document.body : undefined;

  return (
        <Drawer
          variant="permanent"
          PaperProps={{variant:"elevation", elevation:2, boxSizing: 'border-box' }}
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