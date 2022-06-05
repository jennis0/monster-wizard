import React from 'react';

import { Paper, Box } from "@mui/material"

import UploadPage from './pages/add_source_2';
import SourceListPage from './pages/source_list';
import SourcePage from './pages/source'

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
  {label:"Collections", path:"collections", element:<SourceListPage />, icon:<Collections />},
  {label:"Search", path:"search", element:<SearchPage />, icon:<Search />},
  // {label:"Settings", path:"settings", element:null, icon:<Settings />},
  // {label:"About", path:"about", element:null, icon:<Info />}
]

function App() {

  return (
    <CssBaseline>
            <NavDrawer pages={ROUTES}/>
            <Box sx={{marginLeft:"240px", p:0, overflowY:"hidden"}}>
              <Routes>
              <Route path={"/sources/:id"} element={<SourcePage />}/>
                {ROUTES.map(r => 
                  <Route key={`route-${r.path}`} path={`/${r.path}`} element={r.element}/>
                  )}
              </Routes>
            </Box>
      </CssBaseline>
  );
}

export default App;
