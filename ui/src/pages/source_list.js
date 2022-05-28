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
      <ImageList sx={{ width: "100%", height: "100%", p:17, pl:25, pr:25}} rowHeight={400} gap={16} cols={6}>
      {sources?.map((source) => (
        <Paper>
        <ImageListItem key={source.id} cols={1} onClick={onClick(source.id)}
        sx={{ filter:"grayscale(15%)", "&:hover": {
          filter:"grayscale(0%) contrast(125%)"},
          }
        }
        >

          {images && images.length && source.frontpage > 0 ? 
            <B64Image 
              image_data={images.filter(i => i.source === source.id)[0].data}
              alt={source.frontpage}
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
      ))}
    </ImageList>
    </Box>
  )
}