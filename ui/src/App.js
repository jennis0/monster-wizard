import React from 'react';

import { Paper, Box } from "@mui/material"

import UploadPage from './pages/add_source';
import SourceListPage from './pages/source_list';
import SourcePage from './pages/source'

import { Routes, Route } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';

import { NavDrawer } from './components/Navbar'
import { Upload, Search, Book, Collections, Info } from '@mui/icons-material';
import SearchPage from './pages/search';
import { Settings } from '@mui/icons-material';

const ROUTES = [
  {label:"Import", path:"import", element:<UploadPage />, icon:<Upload />},
  {label:"Sources", path:"sources", element:<SourceListPage />, icon:<Book />},
  {label:"Collections", path:"collections", element:<SourceListPage />, icon:<Collections />},
  {label:"Search", path:"search", element:<SearchPage />, icon:<Search />},
  {label:"Settings", path:"settings", element:null, icon:<Settings />},
  {label:"About", path:"about", element:null, icon:<Info />}
]

function App() {

  return (
    <CssBaseline>
          <Paper sx={{height:"100vh"}} elevation={0}>
            <NavDrawer pages={ROUTES}/>
            <Box sx={{marginLeft:"240px", p:0, overflowY:"hidden"}}>
              <Routes>
              <Route path={"/sources/:id"} element={<SourcePage />}/>
                {ROUTES.map(r => 
                  <Route path={`/${r.path}`} element={r.element}/>
                  )}
              </Routes>
            </Box>
          </Paper>
      </CssBaseline>
  );
}

export default App;
