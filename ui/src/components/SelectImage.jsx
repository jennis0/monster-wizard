import { Button, Grid, Box, Paper} from "@mui/material";
import { useLiveQuery } from "dexie-react-hooks";
import { useEffect, useState, useRef } from "react";
import { db } from "../libs/db";
import B64Image from "./B64Image";
import { StyledDropdown, StyledMultiSelect } from "./FormFields";
import ImageGridItem from "./ImageGridItem";


export function SelectImage( {startingImage, sourceIds} ) {
    return (
        <Grid container spacing={1}>
            <Grid item xs={12}>
                <Button>
                    Upload
                </Button>
            </Grid>
            <Grid item xs={12}>
                <Button>
                    From URL
                </Button>
            </Grid>
            <Grid item xs={12}>
                <Button>
                    Foundry Image
                </Button>
            </Grid>
        </Grid>
    )
}

export function SelectImageFromSource( {selectedImage, sourceIds, setSelectedImage }) {

    const [sourcesToPresent, setSourcesToPresent] = useState([])
    const [sourceIdsToPresent, setSourceIdsToPresent] = useState([])

    const sources = useLiveQuery(() => db.sources.toArray())

    useEffect(() => {
        if (sources) {
            setSourceIdsToPresent(sourceIds)
            setSourcesToPresent(sourceIds.map(i => sources?.filter(s => s.id === i)[0]).map(s => s.title))
        }
    }, [sourceIds, sources])

    const updateSelected = (sTP) => {
        setSourcesToPresent(sTP)
        setSourceIdsToPresent(sTP.map(s => sources.filter(ss => ss.title === s)[0]).map(ss => ss.id))
    }

    console.log(selectedImage, sourceIds)
    const images = useLiveQuery(() => db.images.where("source").anyOf(sourceIdsToPresent).toArray(), [sourceIdsToPresent])

    return (
        <Box sx={{width:"100%", maxHeight:"800px"}}>

        <Grid sx={12} container spacing={2}>
            <Grid item xs={12} lg={8}>
                <StyledMultiSelect label="Sources" options={sources? sources.map(s => s.title) : []} selected={sourcesToPresent}
                    setSelected={updateSelected}
                />
                  <Box sx={{display:"flex", overflowY:"auto", width:"100%", height:"700px"}}>
                    <Grid container spacing={1}>
                    {images?.map((image, i) => {
                        return (
                                <ImageGridItem image={image} text={`Page ${image?.page}`} 
                                subText={sources?.filter(s => s.id === image.source)[0].title}
                                    width="100%"
                                    alt={`Image ${i}, page ${image?.page}`} 
                                    onClick={() => {setSelectedImage(image)}}
                                />
                            )
                    })}
                    </Grid>
                </Box>
            </Grid>
            <Grid item xs={0} lg={4}>
                <Box sx={{height:"750px"}}>
                    <B64Image image_data={selectedImage?.data}/>
                </Box>
            </Grid>
        </Grid>
        </Box>
    )
}