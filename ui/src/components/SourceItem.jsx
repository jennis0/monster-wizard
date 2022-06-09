

import React, { useEffect, useRef, useState } from 'react'
import { Grid, ImageListItem, ImageListItemBar, IconButton, Paper, Typography } from "@mui/material"

import { Delete } from '@mui/icons-material';
import B64Image from './B64Image';


import _ from 'lodash'
import { Box } from '@mui/system';
import ConfirmDelete from './ConfirmDelete';

export default function SourceItem({source, onClick, onDelete, images}) {
    const ref = useRef()
    const [height, setHeight] = useState()
    const [deleteOpen, setDeleteOpen] = useState()
  
    useEffect(() => {
      setHeight(1.294 * ref.current.clientWidth)
    }, [ref])
  
  return (
    <Grid item xs={12} sm={6} md={6} lg={4} xl={3} ref={ref}>
    <ConfirmDelete open={deleteOpen} setOpen={setDeleteOpen} onDelete={onDelete(source.id)} title={source.title} />
    <Paper square elevation={0}>
      <ImageListItem key={source.id} cols={1} onClick={onClick(source.id)}
        sx={{ maxWidth:"100%", alignItems:"center", p:0, filter:"grayscale(15%)", "&:hover": {
          filter:"grayscale(0%) contrast(125%)"},
          }
        }
      >
        {images && images.length && source.frontpage > 0 ? 
          <B64Image 
            image_data={images.filter(i => i.source === source.id)[0]?.data}
            alt={source.frontpage}
            width="100%"
            height={height}
            style={{alignItems:"center", overflowY:"clip"}}
          /> :
          <img src="./icons/logo-a4.webp" height={height} />
        }
        
        <ImageListItemBar
          title={(<Typography variant="nav" sx={{fontSize:20}}>{source.title}</Typography>)}
          subtitle={(<Typography variant="nav"><i>{source.author ? source.author : ""}</i></Typography>)}
          actionIcon={
            <>
            <IconButton
              sx={{ color: 'rgba(255, 255, 255, 0.54)' }}
              aria-label={`info about ${source.title}`}
              onClick={e => {e.stopPropagation(); e.preventDefault(); setDeleteOpen(true); }}
            >
              <Delete />
            </IconButton>
            </>
          }
          sx={{backgroundColor:"primary.dark", height:70, opacity:0.8}}
        />
      </ImageListItem>
    </Paper>
  </Grid>
  )
}