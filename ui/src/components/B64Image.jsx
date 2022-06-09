import { Box } from "@mui/material"

export default function B64Image ( {image_data, alt=null, width="100%", height="100%", ...props} ) {
    return (
        <Box sx={{width:width, height:height, display:"flex",
        justifyItems:"center", alignItems:"center", textAlign:"center", justifyContent:"center",
        alignContent:"center"}}>
            <img
                src={"data:image/webp;base64," + image_data}
                alt={alt}
                width={width}
                height={height}
                loading="lazy"
                style={{objectFit: "contain"}}
                {...props}
            />
        </Box>
    )
}