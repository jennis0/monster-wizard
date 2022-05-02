import { Button } from "@mui/material";

export default function UploadButton( { onChange, children } ) {
    
    return (
      <>
      <input
        accept="pdf/*"
        style={{ display: 'none' }}
        id="raised-button-file"
        multiple
        type="file"
        onChange={onChange}
      />
      <label htmlFor="raised-button-file">
        <Button variant="outlined" component="span">
          {children ? children: "Upload"}
        </Button>
      </label> 
      </>
    );
  }