import React, { useState, useRef, useCallback } from 'react';

import { Document, Page } from 'react-pdf/dist/esm/entry.webpack5';

import {ButtonGroup, Button, Stack} from "@mui/material";

function highlightStatblocks(text, box, pageBox, page, statblocks) {

  if (!statblocks) {
    return text;
  }

  const x = box[0] / pageBox[2];
  const y = 1 - box[1] / pageBox[3];
  const x2 = x + box[2] / pageBox[2];
  const y2 = y + box[3] / pageBox[2]; 

  for (let i = 0; i < statblocks.length; i+=1) {
    if (statblocks[i][4] !== page) {
      continue;
    }
    const bound = statblocks[i][1];
    if (x >= bound.left && y <= (bound.top+bound.height) && x2 <= (bound.left+bound.width) && y2 >= bound.top) {
      return <mark>{text}</mark>
    }
  }
  return text;
}

function PDFDisplay({pdfContent, page, setPage, processedData=null, scale=1.3, sendData=null}) {
  const [numPages, setNumPages] = useState(null);
  const [mouseHover, setMouseHover] = useState(false)
  const canvasRef = useRef(null)
  const [processed, setProcessed] = useState(false)

  const textRenderer = useCallback(
    (textItem) => { 
      return highlightStatblocks(textItem.str, [textItem.transform[4], textItem.transform[5], textItem.width, textItem.height], textItem.page._pageInfo.view, textItem.page._pageIndex, processedData?.statblock_text);
    },
    [processedData]
  );


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
    <div onMouseEnter={() => setMouseHover(true)} onMouseLeave={() => setMouseHover(false)} style={{padding:0, margin:0}}>
    <Stack alignItems="center" >
          <Document file={pdfContent} onLoadSuccess={onDocumentLoadSuccess} onLoadError={console.error}>
            <Page pageNumber={page} renderAnnotationLayer={false} customTextRenderer={textRenderer} scale={scale} canvasRef={canvasRef}/>
          </Document>
          {mouseHover ? 
          <ButtonGroup variant="outlined" sx={{margin:1, marginTop:"-5%", alignItems:"center", zIndex:100, display:"block", backgroundColor: "white"}}>
            <Button onClick={() => setPage(1)} disabled={page === 1}>First</Button>
            <Button onClick={onPageBack} disabled={page === 1}>Back</Button>
            <Button>{page}/{numPages}</Button>
            <Button onClick={onPageForward} disabled={page >= numPages - 1}>Forward</Button>
            <Button onClick={() => setPage(numPages - 1)} disabled={page >= numPages - 1}>Last</Button>
          </ButtonGroup> : <></>}
          </Stack>
      </div>
  );
}

export default PDFDisplay;
