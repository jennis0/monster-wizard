import { AddPhotoAlternate, Image } from "@mui/icons-material"
import { ImageList, ImageListItem, ImageListItemBar, Box, Container, Button, Dialog } from "@mui/material"
import { useState } from "react"
import B64Image from "../B64Image"
import { SelectImage, SelectImageFromSource } from "../SelectImage"


function SelectImageDialog( {startingImage, open, setOpen, setImage} ) {
    return (
        <Dialog open={open} PaperProps={{square:true, sx:{p:2, width:"1200px", maxHeight:"800px"}}}
            maxWidth={{sm:12, lg:6}} onClose={() => setOpen(false)}
        >
            <SelectImageFromSource selectedImage={startingImage} 
                sourceIds={startingImage && startingImage.source ? [startingImage.source] : []} 
                setSelectedImage={setImage}
            />
        </Dialog>
    )
}

export default function ImageViewer( { image, imageOptions, allowEdit=false, defaultEdit=false, setImage=null } ) {
    const [dialogOpen, setDialogOpen] = useState(false)
    const [fromSource, setFromSource] = useState(true)

    
    return (
        <Box width="100%" sx={{p:1}}>
        <Container width="80%" sx={{display:"flex", justifyContent:"center"}}>
            {image && <B64Image
                image_data={image.data}
                alt={`Image ${image.page}-main`}
                width="80%"
            />}
        </Container>
        <Button startIcon={<Image />} onClick={() => setDialogOpen(true)}>
            Select Image From Source
        </Button>
        <Button startIcon={<AddPhotoAlternate />}>
            Select New Image
        </Button>

        <SelectImageDialog startingImage={image} fromSource={fromSource} 
            open={dialogOpen} setOpen={setDialogOpen} 
            setImage={setImage}
        />
        </Box>
    )
}