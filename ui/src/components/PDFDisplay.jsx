import React, { useState, useRef, useCallback, useEffect } from 'react';

import { Document, Page } from 'react-pdf/dist/esm/entry.webpack5';

import {ButtonGroup, Button, Stack} from "@mui/material";
import { ArrowLeft, ArrowRight, FirstPage, LastPage } from '@mui/icons-material';

function PDFDisplay({pdfContent, startPage=1, processedData=null, scale=1.3, sendData=null}) {
  const [numPages, setNumPages] = useState(null);
  const [mouseHover, setMouseHover] = useState(false)
  const [page, setPage] = useState(startPage)
  const canvasRef = useRef(null)

  useEffect(() => {
    setPage(startPage)
  },[pdfContent])

  function onDocumentLoadSuccess(pdfResult) {
    console.log("pdfinfo", pdfResult)
    const data = {"numPages":pdfResult._pdfInfo.numPages}
    pdfResult.getMetadata().then(r => {
      if (r.info.Title) {
        data.title = r.info.Title
      }
      if (r.info.Author) {
        data.author = r.info.Author
      }
      setNumPages(data.numPages)
      sendData(data)
    })
  }

  function onPageForward() {
    setPage(page => Math.min(page + 1, numPages - 1));
  }

  function onPageBack() {
    setPage(page => Math.max(page - 1, 1));
  }


  return (
    <>{pdfContent ? 
    <div onMouseEnter={() => setMouseHover(true)} onMouseLeave={() => setMouseHover(false)} style={{padding:0, margin:0}}>
    <Stack alignItems="center" >
          <Document file={pdfContent} onLoadSuccess={onDocumentLoadSuccess} onLoadError={console.error}>
            <Page pageNumber={page} renderAnnotationLayer={false} scale={scale} canvasRef={canvasRef}/>
          </Document>
          {mouseHover ? 
          <ButtonGroup variant="outlined" sx={{margin:1, height:"100%", marginTop:"-40px", marginBottom:"auto", alignItems:"center", zIndex:100, display:"block", backgroundColor: "white"}}>
            <Button sx={{height:40}} onClick={() => setPage(1)} disabled={page === 1}><FirstPage /></Button>
            <Button sx={{height:40}} onClick={onPageBack} disabled={page === 1}><ArrowLeft /></Button>
            <Button sx={{height:40}}>{page}/{numPages}</Button>
            <Button sx={{height:40}} onClick={onPageForward} disabled={page >= numPages - 1}><ArrowRight /></Button>
            <Button sx={{height:40}} onClick={() => setPage(numPages - 1)} disabled={page >= numPages - 1}><LastPage /></Button>
          </ButtonGroup> : <></>}
          </Stack>
      </div>
       : <></>}</>
  );
}

export default PDFDisplay;
