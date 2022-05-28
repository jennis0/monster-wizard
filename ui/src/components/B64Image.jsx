export default function B64Image ( {image_data, alt=null, width="100%", height="100%", ...props} ) {
    return (
        <img
            src={"data:image/webp;base64," + image_data}
            alt={alt}
            width={width}
            height={height}
            loading="lazy"
            style={{backgroundColor: "whitet", objectFit: "cover", objectPosition:"left top", body: { 
                    backgroundColor: "white", 
                }
              }}
            {...props}
        />
    )
}