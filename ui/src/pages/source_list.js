import React from 'react'
import { ImageList, ListSubheader, ImageListItem, ImageListItemBar, IconButton, Container, Paper, Box, Typography } from "@mui/material"
import InfoIcon from '@mui/icons-material/Info';

import { useQuery, db, deleteSource } from '../libs/db';
import { useLiveQuery } from 'dexie-react-hooks';
import { useNavigate } from 'react-router-dom';
import { Delete } from '@mui/icons-material';
import B64Image from '../components/B64Image';

{/* <img
src={`https://www.wargamer.com/wp-content/uploads/2021/01/dnd-5e-class-guide-main-image-adventuring-party-closeup.jpg?w=248&fit=crop&auto=format`}
srcSet={`https://www.wargamer.com/wp-content/uploads/2021/01/dnd-5e-class-guide-main-image-adventuring-party-closeup.jpg?w=248&fit=crop&auto=format&dpr=2 2x`}
alt={source.title}
loading="lazy"
onMouseEnter={() => console.log("mouse")}
/> */}


export default function SourceListPage () {
  const navigate = useNavigate()
  const images = useLiveQuery( () => db.images.where("page").equals(0).toArray() )
  const sources = useLiveQuery( () => db.sources.toArray() )

  console.log(sources)
  console.log(db.sources)

  const onClick = (id) => () => {
    navigate(`/sources/${id}`)
  }

  const onDelete = (id) => () => {
    deleteSource(id)
  }

  console.log("ims", images?.length, sources?.map(s => [s.id, s.frontpage]))

  return (
      <Box>
      <Paper square sx={{width:"100%", height:"5vh", display:"flex", alignItems:"center"}}>
          <Typography variant="h6" sx={{m:0, p:1}}>Sources</Typography>
      </Paper>
      <ImageList sx={{ width: "50%", height: "100%", p:1}}>
      {sources?.map((source) => (
        <ImageListItem key={source.id} cols={1} onClick={onClick(source.id)}
        sx={{ filter:"grayscale(15%)", "&:hover": {
          filter:"grayscale(0%) contrast(125%)",
        }}}
        >

          {images && images.length && source.frontpage > 0 ? 
            <B64Image 
              image_data={images.filter(i => i.source === source.id)[0].data}
              alt={source.frontpage}
              width={240}
            /> : <></>}
          <ImageListItemBar
            title={source.title}
            subtitle={source.author}
            actionIcon={
              <IconButton
                sx={{ color: 'rgba(255, 255, 255, 0.54)' }}
                aria-label={`info about ${source.title}`}
                onClick={e => {onDelete(source.id)(); e.stopPropagation(); e.preventDefault()}}
              >
                <Delete />
              </IconButton>
            }
          />
        </ImageListItem>
      ))}
    </ImageList>
    </Box>
  )
}