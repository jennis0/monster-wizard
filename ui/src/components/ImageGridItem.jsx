

import React, { useEffect, useRef, useState } from 'react'
import { Grid, ImageListItem, ImageListItemBar, IconButton, Paper, Typography } from "@mui/material"

import { Delete, Menu } from '@mui/icons-material';
import B64Image from './B64Image';


import _ from 'lodash'
import { Box } from '@mui/system';
import ConfirmDelete from './ConfirmDelete';

function ImageActionButton({onDelete, onEdit}) {
    if (!onDelete && !onEdit) {
        return (<></>)
    }
    
    if (onDelete && !onEdit) {
        return (
            <IconButton
            sx={{ color: 'rgba(255, 255, 255, 0.54)'}}
            aria-label={`Delete}`}
            onClick={e => {e.stopPropagation(); e.preventDefault(); onDelete(); }}
          >
            <Delete />
          </IconButton>
        )
    }

    if (!onDelete && onEdit) {
        return (
            <IconButton
            sx={{ color: 'rgba(255, 255, 255, 0.54)' }}
            aria-label={`Edit`}
            onClick={e => {e.stopPropagation(); e.preventDefault(); onEdit(); }}
          >
            <Delete />
          </IconButton>
        )
    }

    return (
        <IconButton
        sx={{ color: 'rgba(255, 255, 255, 0.54)' }}
        aria-label={`menu`}
        >
        <Menu />
        </IconButton>
    )
}

export default function ImageGridItem({image, text, subText, alt, onClick, width="200px", height="100%", onDelete=null, onEdit=null}) {
    const ref = useRef()
    const [deleteOpen, setDeleteOpen] = useState()
  
  return (
    <Grid item xs={12} sm={6} md={6} lg={4} xl={3} ref={ref}>
    {onDelete && <ConfirmDelete open={deleteOpen} setOpen={setDeleteOpen} onDelete={onDelete} title={text} />}
    <Paper square elevation={0} sx={{width:width, height:height, }}>
      <ImageListItem key={text} cols={1} onClick={onClick}
        sx={{minWidth:width, minHeight:height, display:"block",
          p:0, filter:"grayscale(15%)", "&:hover": {
          filter:"grayscale(0%) contrast(125%)"},
          }
        }
      >
        {image ? 
          <B64Image 
            image_data={image?.data}
            alt={alt}
            width={width}
            style={{alignItems:"center", overflowY:"clip"}}
          /> :
          <img src="./icons/logo-a4.webp" width={width} height={height}/>
        }
        <ImageListItemBar
          title={(<Typography variant="nav" sx={{fontSize:18}}>{text}</Typography>)}
          subtitle={(subText ? <Typography variant="nav"><i>{subText}</i></Typography> : null)}
          actionIcon={<ImageActionButton onDelete={onDelete} onEdit={onEdit}/>}
          sx={{backgroundColor:"primary.dark", opacity:0.75, padding:0}}
        />
      </ImageListItem>
    </Paper>
  </Grid>
  )
}