import { ImageList, ImageListItem, ImageListItemBar, Box, Container } from "@mui/material"
import B64Image from "../B64Image"


export default function ImageViewer( { image, imageOptions, allowEdit=false, defaultEdit=false } ) {
    return (
        <Box width="100%">
        <Container width="100%" alignItems="center">
            {image && <B64Image
                image_data={image.data}
                alt={`Image ${image.page}-main`}
                width="90%"
            />}
        </Container>
        
            <ImageList sx={{ width: 500, height: 450 }} cols={3} rowHeight={164}>
            {imageOptions && imageOptions.map((image,i) => (
                    <ImageListItem key={`image-${image.page}-${i}`}>
                    <B64Image
                        image_data={image.data}
                        alt={`Image ${image.page}-${image.id}`}
                        width={240}
                    />
                    <ImageListItemBar
                        title={`Page ${image.page}`}
                    />
                    </ImageListItem>
            ))
            }
            </ImageList>
        </Box>
    )
}