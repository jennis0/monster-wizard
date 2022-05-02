import React, { useState, useRef, useEffect, useCallback } from 'react';

import { Document, Page } from 'react-pdf/dist/esm/entry.webpack5';

import {ButtonGroup, Button} from "@mui/material";
import { Paper } from "@mui/material"
import ArrowBack from '@mui/icons-material/ArrowBackIosNew';
import ArrowForward from '@mui/icons-material/ArrowForwardIos';


import UploadButton from './UploadButton';

function highlightStatblocks(text, box, pageBox, page, statblocks) {

  if (statblocks == null) {
    return text;
  }

  const x = box[0] / pageBox[2];
  const y = 1 - box[1] / pageBox[3];
  const x2 = x + box[2] / pageBox[2];
  const y2 = y + box[3] / pageBox[2]; 

  for (let i = 0; i < statblocks.length; i+=1) {
    if (statblocks[i][4] != page) {
      continue;
    }
    const bound = statblocks[i][1];
    if (x >= bound.left && y <= (bound.top+bound.height) && x2 <= (bound.left+bound.width) && y2 >= bound.top) {
      return <mark>{text}</mark>
    }
  }
  return text;
}

function PDFDisplay({ pdfContent, processedData, style, page, setPage }) {
  const [numPages, setNumPages] = useState(null);
  const windowRef = useRef(null);

  const textRenderer = useCallback(
    (textItem) => { 
      return highlightStatblocks(textItem.str, [textItem.transform[4], textItem.transform[5], textItem.width, textItem.height], textItem.page._pageInfo.view, textItem.page._pageIndex, processedData?.statblock_text);
    },
    [processedData]
  );


  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
  }

  function onPageForward() {
    setPage(page => Math.min(page + 1, numPages - 1));
  }

  function onPageBack() {
    setPage(page => Math.max(page - 1, 1));
  }

  return (
    <div style={{
        display:"flex", verticalAlign:"top", alignItems: "center", justifyContent:"center", flexDirection:"column", ...style, 
    }} ref={windowRef}>
          <Document file={pdfContent} onLoadSuccess={onDocumentLoadSuccess} onLoadError={console.error}>
            <Page pageNumber={page} renderAnnotationLayer={false} customTextRenderer={textRenderer}/>
          </Document>
          <ButtonGroup variant="outlined" sx={{margin:1, alignItems:"center"}}>
            <Button onClick={() => setPage(1)} disabled={page == 1}>First</Button>
            <Button onClick={onPageBack} disabled={page == 1}>Back</Button>
            <Button>{page}/{numPages}</Button>
            <Button onClick={onPageForward} disabled={page >= numPages - 1}>Forward</Button>
            <Button onClick={() => setPage(numPages - 1)} disabled={page >= numPages - 1}>Last</Button>
          </ButtonGroup>
      </div>
  );
}

export default PDFDisplay;
