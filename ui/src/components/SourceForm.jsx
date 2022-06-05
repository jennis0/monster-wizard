import { useState, useEffect } from 'react'

import { Grid, Typography, Stack, Box, Button, Paper, Divider, Tabs, Tooltip } from '@mui/material'
import { Done,  Delete } from '@mui/icons-material'

import { StyledCheckbox, StyledTextField } from './FormFields'
import PDFViewer from './viewers/PDFViewer'

import {load_pdf} from '../libs/pdf'

import Tab from '@mui/material/Tab';
import TabContext from '@mui/lab/TabContext';
import TabList from '@mui/lab/TabList';
import TabPanel from '@mui/lab/TabPanel';
import { uploadRequest } from '../libs/upload'

function SourceRequestTabs( { requests, setRequests, disabled }) {
  const [value, setValue] = useState("0");

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const setRequest = (i) => (val) => {
    const newReqs = [...requests]
    newReqs[i] = val
    setRequests(newReqs)
  }

  const removeRequest = (i) => () => {
    const newReqs = [...requests]
    newReqs.splice(i, 1)
    setRequests(newReqs)
  }

  return (
    <Box sx={{ width: '100%', typography: 'smallNav' }}>
      <TabContext value={String(value)}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <TabList onChange={handleChange} 
            aria-label="File Import Requests"
            variant="scrollable"
            scrollButtons="auto"
          >
              {requests?.map((r,i) => {
                  return (
                    <Tab label={r.source.title} value={String(i)} key={`tab-label-${i}`}/>
                )
              })}
          </TabList>
        </Box>
        {requests?.map((r, i) => {
            return (
            <TabPanel value={String(i)} key={`tab-${i}`}>
                <SourceRequestDisplay disabled={disabled} request={r} setRequest={setRequest(i)} removeRequest={removeRequest(i)} />
            </TabPanel>)
        })}
      </TabContext>
    </Box>
  );
}


const FORMATS = {
    "pdf":{accept:".pdf"},
    "fvtt":{accept:".json"}
}

function ImageButton ( {icon, children, onAddFile, width="100%", height=150, format, disabled}) {
    const format_data = FORMATS[format]
    const id = `raised-button-file-${format}`
    return (
        <Paper elevation={0} sx={{borderRadius:0, height:height, width:width, m:0, p:0}}>
            <input
                accept={format_data?.accept}
                style={{ display: 'none' }}
                id={id}
                type="file"
                multiple
                disabled={disabled}
                onChange={onAddFile}
            />
            <label htmlFor={id} sx={{m:0, p:0}}>
            <Button 
                component="span"
                disabled={disabled}
                sx={{borderRadius:0, width:width, m:0, height:"100%", p:2, alignItems:"center", textAlign:"center"}}
            >
                <Stack spacing={1.5} sx={{alignItems:"center", justifyContent:"center", m:0, p:0}}>
                    {icon}
                    {children}
                </Stack>
            </Button>
            </label>
        </Paper>
    )
}

function SourceRequestDisplay ({request, setRequest, removeRequest, disabled=false}) {

    const [pdfMetadata, setPDFMetadata] = useState({numPages:null})


    const setRequestField = (field) => (e) => {
        const req = {...request}
        req.source[field] = e.target.value
        setRequest(req)
    }

    useEffect(() => {
        const handlePDFLoad = (result) => {
            setRequest({...request, file:result})
        }

        if (request.source.filename && !request.file) {
            load_pdf(request.source.filename, handlePDFLoad)
        }
    }, [request])

    return (
    <Grid container spacing={1}>
        <Grid item container xs={12} xl={6} spacing={1} alignItems="center">
            <Grid item xs={8}>
                <Typography variant="nav" fontSize={24} sx={{p:1}}>PDF File</Typography>
            </Grid>
            <Grid item xs={4}>
                <Button endIcon={<Delete />} sx={{width:"100%"}} onClick={removeRequest}>Remove</Button>
            </Grid>
            <Grid item xs={12}>
                <StyledTextField 
                    tooltip="Title for this document."
                    disabled={disabled} label="Title" onChange={setRequestField("title")} value={request.source.title}/>
            </Grid>
            <Grid item xs={12}>
                <StyledTextField 
                    tooltip="Comma-separated list of authors."
                    disabled={disabled} label="Author(s)" onChange={setRequestField("author")} value={request.source.author}/>
            </Grid>
            <Grid item xs={12}>
                <StyledTextField 
                    tooltip="The pages to import, can be comma-separated list or ranges."
                    disabled={disabled} label="Pages" value={pdfMetadata.numPages} />
            </Grid>
            <Grid item xs={12}>
                <Box flex={1} sx={{display:"flex", height:"170px"}} />
            </Grid>
        </Grid>
        <Grid item xs={12} xl={6}>
            <SourcePDFDisplay file={request.file} setPDFMetadata={setPDFMetadata} />
        </Grid>
    </Grid>
    )
}

function SourcePDFDisplay( {file, setPDFMetadata} ) {
    return (
    <Box justifyContent="center" alignContent="center" textAlign="center" padding={2} height={450}>
        <PDFViewer pdfContent={file} startPage={1} scale={0.55} sendData={setPDFMetadata}/>
    </Box>)
}
 

function create_default_source(title, file) {
    return {
        title:title, type:"", author:"", filename:file.name, 
    }
}

function create_meta_source(title) {
    return {
        title:title, author:"", sources:{}
    }
}

function create_default_request(file) {

    let title = file.name.split(".")[0].replace("_"," ").replace("-"," ").trim()
    title = title[0] + title.substring(1)

    return {
        file:file,
        pages:[],
        source: create_default_source(title, file)
    }
}

function create_default_upload() {
    return {
            time:null, status:null, 
            file_progress:null, progress:null, errors:[], 
            store_images:true, store_raw:true, merge:false,
            requests:[], merged_source: create_meta_source("")
        }
}

function send_files(upload) {
    if (upload.merge) {
        uploadRequest(upload.requests, upload.merged_source, upload.store_images, upload.store_raw)
    } else {
        for (const request of upload.requests) {
            uploadRequest([request], request.source, upload.store_images, upload.store_raw)
        }
    }
    
}

export default function SourceForm() {

    const [currentRequests, setCurrentRequests] = useState(create_default_upload())

    const setFilename = (e) => {

        const requests = [...currentRequests.requests]
        for (const f of e.target.files) {
            const cs = create_default_request(f)
            requests.push(cs)
        }

        setCurrentRequests(r => {
            return {...r, requests:requests}
        })

        if (currentRequests.merged_source.title.length === 0) {
            updateMergedSource("title")(requests[0].source.title)
        }
    }


    const updateField = (field) => (val) => {
        setCurrentRequests(cr => {
            const newRequest = {...cr}
            newRequest[field] = val
            return newRequest
        })
        
    }

    const updateMergedSource = (field) => (val) => {
        setCurrentRequests(cr => {
            const ns = {...cr.merged_source}
            ns[field] = val
            return {...cr, merged_source:ns}
        })
    }

    return (
    <Box sx={{width:"100%", height:"100%", justifyItems:"center", alignItems:"center"}}>

    <Grid container spacing={1}>
        <Grid item xs={6} xl={6}>
            <ImageButton icon={<img src={"icons/pdf.png"} width={30}/>} onAddFile={setFilename} format="pdf" height={100}>
                <Typography variant="nav">Add PDF</Typography>
            </ImageButton>
        </Grid>
        <Grid item xs={6} xl={6}>
            <Tooltip title="Coming soon..."><span>
                <ImageButton disabled format="fvtt" icon={<img src={"icons/fvtt.png"} width={30}/>} onAddFile={setFilename}  height={100} size="large" sx={{height:292, width:"100%"}}>
                    <Typography variant="nav">Add Foundry Compendium</Typography>
                </ImageButton>
                </span>
            </Tooltip>
        </Grid>
    </Grid>
        
    <Divider sx={{width:"100%", m:0, p:0, mb:1, mt:1}} />
  
    {currentRequests.requests.length > 0 ? 
    <>
        <SourceRequestTabs disabled={currentRequests.merge} requests={currentRequests.requests} setRequests={updateField("requests")} />
        <Divider sx={{width:"100%", m:0, p:0, mb:1, mt:1}} />
    </> : <></>}


    {currentRequests.merge ? 
    <>
        <Grid container padding={2} spacing={1}>
            <Grid item xs={12}>
                <Tooltip title="Details to be used by the final merged source">
                    <Typography variant="nav" fontSize={24}>Source Details</Typography>
                </Tooltip>
            </Grid>
            <Grid item xs={12} xl={6}>
                <StyledTextField label="Source Title" 
                    tooltip="Title for source" 
                    value={currentRequests.merged_source.title}
                    onChange={(e) => updateMergedSource("title")(e.target.value)}
                />
            </Grid>
            <Grid item xs={12} xl={6}>
                <StyledTextField label="Source Author(s)" 
                    value={currentRequests.merged_source.author}
                    tooltip="Comma-separated list of authors"
                    onChange={(e) => updateMergedSource("author")(e.target.value)}
                />
            </Grid>
        </Grid>
        <Divider sx={{width:"100%", m:0, p:0, mb:1, mt:1}} />
    </>
     : <></>}


    <Grid container spacing={2} padding={2}>
        <Grid item xs={12}>
            <Tooltip title="Configuration settings for the import process">
                <Typography variant="nav" fontSize={24}>Import Settings</Typography>
            </Tooltip>
        </Grid>
        <Grid item xs={12} lg={6} xl={4}>
            <StyledCheckbox checked={currentRequests.store_raw} 
                tooltip="Store the original PDF alongside the extracted statblocks. This can use a large amount of space."
                label="Store PDFs" onCheckChange={(e) => updateField("store_raw")(e.target.checked)} long />
        </Grid>
        <Grid item xs={12} lg={6} xl={4}>
            <StyledCheckbox checked={currentRequests.store_images} 
                tooltip="Extract images from PDF files and attempt to attach them to statblocks. This can use a large amount of space."
                label="Extract Images" onCheckChange={(e) => updateField("store_images")(e.target.checked)} long/>
        </Grid>
        <Grid item xs={12} lg={6} xl={4}>
            <StyledCheckbox checked={currentRequests.merge} 
                tooltip="Merge all documents into a single source" 
                label="Merge to Single Source" onCheckChange={(e) => updateField("merge")(e.target.checked)} long />
        </Grid>
    </Grid>


    <Divider sx={{width:"100%", m:0, p:0, mb:1, mt:1}} />

    <Box padding={2}>
            <Box display="flex" justifyContent="flex-end" sx={{width:"100%"}}>
                <Tooltip title="Import selected files">
                    <span>
                    <Button startIcon={<Done />} 
                        variant="contained"
                        elevation={0}
                        onClick={() => send_files(currentRequests)}
                        disabled={currentRequests.requests.length === 0}
                        sx={{borderRadius:0, width:"150px"}}
                    >
                        Import
                    </Button>
                    </span>
                </Tooltip>
            </Box>
    </Box>

    </Box>)
}