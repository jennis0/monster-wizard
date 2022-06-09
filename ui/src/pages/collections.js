import { Add } from "@mui/icons-material";
import { Button, Dialog, DialogTitle, Grid, Typography } from "@mui/material";
import { Box } from "@mui/system";
import { useLiveQuery } from "dexie-react-hooks";
import { useEffect, useState } from "react";
import CenteredContent from "../components/CenteredContent";
import CreateCollection from "../components/CreateCollection";
import SourceItem from "../components/SourceItem";
import { addCollection, db, deleteCollection } from "../libs/db";

function CollectionBody({collections}) {
    console.log(collections)

    const onDelete = (id) => () => {
        deleteCollection(id)
      }

    return (
        <Box sx={{p:2}}>
        <Grid container spacing={2}>
            {collections?.map((c,i) => {
                            console.log(c)
                            return (
                                <SourceItem key={`collection-item-${i}`} source={c} onDelete={onDelete}
                                    onClick={() => {}}
                                />
                            )
                    })}
        </Grid>
        </Box>
    )
}

function CollectionHeader( {setCollections} ) {
    const collections = useLiveQuery(() => db.collections.toArray())

    useEffect(() => {
        setCollections(collections)
    }, [collections])
}


function CreateCollectionButton() {
    const [dialogOpen, setDialogOpen] = useState(false)
    return (<>
  
        <Dialog open={dialogOpen} PaperProps={{square:true, sx:{p:2}}}>
          <CreateCollection onClose={() => setDialogOpen(false)} onCreate={() => setDialogOpen(false)} />
        </Dialog>
        <Button startIcon={<Add />} onClick={() => setDialogOpen(true)} 
          sx={{color:"primary.contrastText"}} variant="contained"
        >
          New Collection
        </Button>
        </>
    )
  }
  


export default function CollectionPage() {
    const [collections, setCollections] = useState([])

    return (
        <CenteredContent
            title="Collections"
            body={<CollectionBody collections={collections}/>}
            subheader={<CollectionHeader setCollections={setCollections}/>}
            headerbutton={<CreateCollectionButton />}
        />
    )
}