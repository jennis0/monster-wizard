import React from 'react';

import { Paper, Box } from "@mui/material"

import UploadPage from './pages/add_source';
import SourceListPage from './pages/source_list';
import SourcePage from './pages/source'

import { Routes, Route } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';

import { NavDrawer } from './components/Navbar'
import { Upload } from '@mui/icons-material';
import { Search } from '@mui/icons-material';
import { Book } from '@mui/icons-material';
import SearchPage from './pages/search';

const ROUTES = [
  {label:"Upload", path:"upload", element:<UploadPage />, icon:<Upload />},
  {label:"Sources", path:"sources", element:<SourceListPage />, icon:<Book />},
  {label:"Search", path:"search", element:<SearchPage />, icon:<Search />},
]

function App() {

  return (
    <CssBaseline>
          <Paper sx={{height:"100vh"}} elevation={0}>
            <NavDrawer pages={ROUTES}/>
            <Box sx={{marginLeft:"240px"}}>
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
