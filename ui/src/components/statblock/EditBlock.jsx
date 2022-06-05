import { Paper,Button, Box, Grid, Divider, ButtonGroup, IconButton } from "@mui/material"

import { StyledTextField } from '../FormFields.jsx';
import PoppableField from "./PoppableField.jsx";

import * as fmt from '../../libs/creature_format.js'
import { Delete } from '@mui/icons-material';
import { Add } from '@mui/icons-material';
import { Typography } from "@mui/material";

export default function EditBlock({ title, children, onAdd, onDelete, first=false }) {
  
    return(<>
            <Grid item xs={12} key={"eb-grid-divider-1"}>
              <Divider />
            </Grid>
            <Grid item xs={10} sx={{m:0, p:0,}} key={"eb-grid-title"}>
              <Box sx={{pl:0.5, pt:0.5, m:0}}>
                <Typography sx={{p:0, m:0}} variant="nav">{title}</Typography>
              </Box>
            </Grid>
            <Grid item xs={2} alignItems="flex-end" textAlign="flex-end" sx={{m:0, p:0}} key="eb-grid-buttons">
              <ButtonGroup 
                sx={{borderRadius:0, m:0, p:0, alignItems:"flex-end"}}>
                {onAdd && <IconButton onClick={onAdd} sx={{m:0, p:1, borderRadius:0}}><Add /></IconButton>}
                {onDelete && <IconButton onClick={onDelete} disabled={first} sx={{m:0, p:1, borderRadius:0}}><Delete /></IconButton>}
              </ButtonGroup>
            </Grid>
            {children}
            <Grid item xs={12} key="eb-grid-divider-2">
                <Divider />
            </Grid>
        </>
    )
  }
  