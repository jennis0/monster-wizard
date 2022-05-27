export default function B64Image ( {image_data, alt=null, width=240, ...props} ) {
    return (
        <img
            src={"data:image/webp;base64," + image_data}
            alt={alt}
            width="100%"
            maxHeight="100%"
            loading="lazy"
            style={{backgroundColor: "whitet", body: { 
                    backgroundColor: "white"
                }
              }}
            {...props}
        />
    )
}