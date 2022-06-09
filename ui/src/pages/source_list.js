import React, { useEffect, useRef, useState } from 'react'
import { Grid, ImageListItem, ImageListItemBar, IconButton, Container, Paper, Box, Typography, Divider, Dialog, Button } from "@mui/material"
import InfoIcon from '@mui/icons-material/Info';

import { useQuery, db, deleteSource } from '../libs/db';
import { useLiveQuery } from 'dexie-react-hooks';
import { useNavigate } from 'react-router-dom';
import { Add, Delete } from '@mui/icons-material';
import B64Image from '../components/B64Image';
import CenteredContent from '../components/CenteredContent';
import { StyledCheckbox, StyledTextField } from '../components/FormFields';

import _ from 'lodash'
import SourceItem from '../components/SourceItem';
import CreateSource from '../components/CreateSource';
import ImageGridItem from '../components/ImageGridItem';


function SourceListHeader( {setSources} ) {
  const [searchTerm, setSearchTerm] = useState("")
  const [group, setGroup] = useState(true)

  const sources = useLiveQuery( () => db.sources.filter(s => s.title.toLowerCase().indexOf(searchTerm) >= 0).toArray(), [searchTerm])
  
  console.log(searchTerm)

  useEffect(() => {
    sources?.sort((s1, s2) => s1.title > s2.title)
    if (group) {
      setSources(_.groupBy(sources, (s=>s.author)))
    } else {
      setSources({"":sources})
    }
  },[sources, group])

  return (
    <Grid container spacing={1}>
      <Grid item xs={12} md={6}>
        <StyledTextField label="Search" value="" onChange={(e) => setSearchTerm(e.target.value)}/>
      </Grid> 
      <Grid item width="auto">
        <StyledCheckbox checked={group} label="Group by author" long onCheckChange={() => setGroup(!group)}/>
      </Grid>     
    </Grid>
  )
}

function SourceListBody( {sources} ) {
  const navigate = useNavigate()
  const images = useLiveQuery( () => db.images.where("page").equals(0).toArray() )

  const onClick = (id) => () => {
    navigate(`/sources/${id}`)
  }

  const onDelete = (id) => () => {
    deleteSource(id)
  }

  const authors = sources ? Object.keys(sources) : []
  authors.sort()

  return (
    <Grid container spacing={2} sx={{p:2}}>

      {authors?.map((s) => {
        const author_sources = sources[s]
        return (<>
          {s !== "" && <>
          <Grid item xs={12}>
            <Typography variant="nav" fontSize={24} color="primary">{s}</Typography>
            <Divider sx={{mb:0, pb:0, mt:0.}}/>
          </Grid>
          </>}
          {author_sources.map((source,i) => 
          { 
              let image = images.filter(i => i.id === source.frontpage);
              if (image.length === 1) {
                image = image[0]
              } else {
                image = null
              }
            return (
              <ImageGridItem key={`source-item-${s}-${i}`} image={image} onClick={onClick(source.id)}
                height="100%" width="100%" text={source.title} subText={source.author}
                onDelete={onDelete(source.id)} 
              />
            )
          }
           )} </>)
      })}     
    </Grid>
  )
}

function CreateSourceButton() {
  const [dialogOpen, setDialogOpen] = useState(false)
  return (<>

      <Dialog open={dialogOpen} PaperProps={{square:true, sx:{p:2}}}>
        <CreateSource onClose={() => setDialogOpen(false)} onCreate={() => setDialogOpen(false)} />
      </Dialog>
      <Button startIcon={<Add />} onClick={() => setDialogOpen(true)} 
        sx={{color:"primary.contrastText"}} variant="contained"
      >
        New Source
      </Button>
      </>
  )
}

export default function SourceListPage () {

  const [sources, setSources] = useState(null)

  return (
      <CenteredContent
        title="Sources"
        subheader={<SourceListHeader setSources={setSources} />}
        body={<SourceListBody sources={sources}/>}
        headerbutton={<CreateSourceButton />}
      />
  )
}