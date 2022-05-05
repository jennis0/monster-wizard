import React from 'react';

import { Paper, Grid } from "@mui/material"

import UploadPage from './pages/old_upload';

import { Routes, Route } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';

import { LocalContext } from './libs/store';

function App() {

  return (
    <CssBaseline>
          <Paper sx={{height:"100vh"}} elevation={0}>
            <Routes>
              <Route path="/*" element={<UploadPage />}/>
            </Routes>
          </Paper>
      </CssBaseline>
  );
}

export default App;
