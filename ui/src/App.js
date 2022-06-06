import React, { useEffect } from 'react';

import { Paper, Box, Grid, Stack, useMediaQuery } from "@mui/material"

import UploadPage from './pages/upload';
import SourceListPage from './pages/source_list';
import SourcePage from './pages/source'
import CollectionPage from './pages/collections';

import { Routes, Route } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';

import { NavDrawer } from './components/Navbar'
import { Upload, Search, Book, Collections, Info, Add } from '@mui/icons-material';
import SearchPage from './pages/search';
import { Settings } from '@mui/icons-material';
import CreatePage from './pages/create';

const ROUTES = [
  {label:"Create", path:"create", element:<CreatePage />, icon:<Add />},
  {label:"Import", path:"import", element:<UploadPage />, icon:<Upload />},
  {label:"Sources", path:"sources", element:<SourceListPage />, icon:<Book />},
  {label:"Collections", path:"collections", element:<CollectionPage />, icon:<Collections />},
  {label:"Search", path:"search", element:<SearchPage />, icon:<Search />},
  // {label:"Settings", path:"settings", element:null, icon:<Settings />},
  // {label:"About", path:"about", element:null, icon:<Info />}
]

function App() {

  const persistantNav = useMediaQuery('(min-width:900px)');


  return (
    <CssBaseline>
        <Stack direction={persistantNav ? "column" : "row"}>
          <NavDrawer pages={ROUTES} persistant={persistantNav}/>
          <Box sx={{width:"100%", p:0, overflowY:"hidden", 
            paddingLeft:persistantNav ? "240px" : null, marginTop:{xs:"50px", sm:"64px", md:"0px"}
          }}>
                <Routes>
                  <Route path={"/sources/:id"} element={<SourcePage />}/>
                  {ROUTES.map(r => 
                    <Route key={`route-${r.path}`} path={`/${r.path}`} element={r.element}/>
                  )}
                </Routes>
          </Box>
        </Stack>
 
      </CssBaseline>
  );
}

export default App;
