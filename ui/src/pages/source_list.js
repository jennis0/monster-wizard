import React from 'react'
import { Grid, ImageListItem, ImageListItemBar, IconButton, Container, Paper, Box, Typography } from "@mui/material"
import InfoIcon from '@mui/icons-material/Info';

import { useQuery, db, deleteSource } from '../libs/db';
import { useLiveQuery } from 'dexie-react-hooks';
import { useNavigate } from 'react-router-dom';
import { Delete } from '@mui/icons-material';
import B64Image from '../components/B64Image';
import CenteredContent from '../components/CenteredContent';
import { StyledCheckbox, StyledTextField } from '../components/FormFields';


function SourceListHeader( {setSources} ) {
  return (
    <Grid container spacing={1}>
      <Grid item xs={12} md={6}>
        <StyledTextField label="Search" value=""/>
      </Grid> 
      <Grid item xs={6} md={3}>
        <StyledCheckbox label="Group by author" long/>
      </Grid>     
    </Grid>
  )
}


function SourceListBody() {
  const navigate = useNavigate()
  const images = useLiveQuery( () => db.images.where("page").equals(0).toArray() )
  const sources = useLiveQuery( () => db.sources.toArray() )

  const onClick = (id) => () => {
    navigate(`/sources/${id}`)
  }

  const onDelete = (id) => () => {
    deleteSource(id)
  }

  return (
    <Grid container spacing={2} sx={{p:2}}>
      {sources?.map((source) => {
        return (
          <Grid item xs={12} sm={6} md={6} lg={4} xl={3} >
            <Paper square elevation={0} sx={{textAlign:"center"}}>
              <ImageListItem key={source.id} cols={1} onClick={onClick(source.id)}
                sx={{ width:"290px", alignItems:"center", p:0, filter:"grayscale(15%)", "&:hover": {
                  filter:"grayscale(0%) contrast(125%)"},
                  }
                }
              >
                {images && images.length && source.frontpage > 0 ? 
                  <B64Image 
                    image_data={images.filter(i => i.source === source.id)[0]?.data}
                    alt={source.frontpage}
                    width="100%"
                    height="400px"
                    style={{alignItems:"center", overflowY:"clip"}}
                  /> : <></>}
                <ImageListItemBar
                  title={(<Typography variant="nav" sx={{fontSize:20}}>{source.title}</Typography>)}
                  subtitle={(<Typography variant="nav"><i>{source.author}</i></Typography>)}
                  actionIcon={
                    <IconButton
                      sx={{ color: 'rgba(255, 255, 255, 0.54)' }}
                      aria-label={`info about ${source.title}`}
                      onClick={e => {onDelete(source.id)(); e.stopPropagation(); e.preventDefault()}}
                    >
                      <Delete />
                    </IconButton>
                  }
                  sx={{backgroundColor:"primary.dark", height:70, opacity:0.8}}
                />
              </ImageListItem>
            </Paper>
          </Grid>
        )
      })}      
    </Grid>
  )
}

export default function SourceListPage () {




  const mw = 310 * 4

  return (
      <CenteredContent
        title="Sources"
        subheader={<SourceListHeader />}
        body={<SourceListBody />}
      />
  )
}