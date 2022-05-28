import React, { useEffect, useState } from 'react';
import { Grid, Paper, Typography, Box, Stack, Button, IconButton, Tab, Tabs, ImageList, ImageListItem, ImageListItemBar } from "@mui/material";
import SaveIcon from '@mui/icons-material/Save';
import EditIcon from '@mui/icons-material/Edit';

import Statblock from './statblock/EditableStatblock';
import StatblockList, { sortByAlphabet } from './StatblockList';
import UploadButton from './UploadButton';
import PDFDisplay from './PDFDisplay';


import { post_file } from '../libs/api';
import { addSource, addStatblock, addImage } from '../libs/db';
import { useNavigate } from 'react-router-dom';
import Loader from './Loader';
import B64Image from './B64Image';

function TabPanel(props) {
    const { children, value, index, ...other } = props;
  
    return (
      <div
        role="tabpanel"
        hidden={value !== index}
        id={`simple-tabpanel-${index}`}
        aria-labelledby={`simple-tab-${index}`}
        {...other}
      >
        {value === index && (
          <Box sx={{ p: 3 }}>
            {children}
          </Box>
        )}
      </div>
    );
  }



export default function ReviewPanel( {source, setSource} ) {
    const [selected, setSelected] = useState(0);
    const [page, setPage] = useState(1);
    const [pdfSource, setPDFSource] = useState(null);
    const [processedData, setProcessedData] = useState(null);
    const [uploadState, setUploadState] = useState({state:"file_upload", progress:[-1,-1]})
    const navigate = useNavigate()
    const [selectedTab, setSelectedTab] = useState(1)
    const [imageData, setImageData] = useState([])

    useEffect(() => {
        setSelected(0)
        setPage(1)
        setPDFSource(null)
        setProcessedData(null)
        const file = source.filename;
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
          setPDFSource(reader.result);
          var data = new FormData()
          data.append("file", source.filename);
          post_file(data, (x) => {console.log("setting statblock", x); setProcessedData(x)}, null, setUploadState);
        };
    }, [source])
  
    const selectStatblock = (index) => {
        const page = processedData?.source?.statblocks[index].source?.page
        if (page) {
            setPage(page);
        }
        setSelected(index);
    }

    const onSave = () => {
        addSource(
            source.title, 
            source.author, 
            processedData.num_pages, 
            source.filename.name, 
            Date.toString(), 
            source.version, 
            "finished", 
            processedData.source.page_images[0]
        )
        .then(
            (id) => {
                for (const sb of processedData.source.statblocks) {
                    addStatblock(id, sb)
                }
                for (const image of processedData.source.images) {
                    addImage(id, image.page, image)
                }
                console.log("finished save")
                //navigate("/sources")
        })
    }

    useEffect(() => {
        let images  = []
        if (processedData) {
            for (const image of processedData.source?.images) {
                images.push({id:image.id, page:image.page, data:image.data, bound:image.bound})
            }
        }
        setImageData(images)
        console.log(images)
    }, [processedData])

    if (!processedData && uploadState) {
        return <Loader state={uploadState} setState={(x) => {setUploadState(x); setSource(x)}}/>
    }

    return (
        <Grid container spacing={0} direction="column">
            <Grid item xs={2}>
                <Paper square variant="outlined" sx={{width:"100%", p:2, m:0, justifyContent:"space-between", display:"flex", flexDirection:"row"}}>
                    <Stack>
                    <Typography variant="h5">Review: {source.title} <IconButton><EditIcon /></IconButton></Typography>
                    <Typography variant="subtitle1">{source.filename.name}</Typography>
                    </Stack>
                    <Button onClick={onSave} startIcon={<SaveIcon />} variant="contained" disableElevation color="secondary" sx={{p:1, m:1, mr:5, pl:2, pr:2}} size="large">Save Statblocks</Button>
                </Paper>
            </Grid>
            <Grid container direction="row" spacing={0} height="95%">
            {processedData && processedData.source.statblocks ? <>
                <Grid item xs={4} md={2}>
                    <Paper square variant="outlined" sx={{p:0,m:0, overflowY:"auto", width:"100%", maxHeight:"95%"}}>
                        <StatblockList statblocks={processedData.source.statblocks} onClick={selectStatblock} title="" sort={sortByAlphabet} />
                    </Paper>
                </Grid>
                <Grid item xs={4} md={5}>
                    <Paper variant="outlined" square sx={{p:2, m:0, overflowY:"auto", height:"100%", width:"100%"}}>
                        <Statblock statblock={processedData.source.statblocks[selected]} allowEdit={true} defaultEdit={true}/>
                    </Paper>
                </Grid>
                <Grid item xs={4} md={5} >
                <Paper square variant="outlined" sx={{width:"100%", p:0, m:0, height:"93vh"}}>
                    <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                        <Tabs value={selectedTab} onChange={(e,v) => setSelectedTab(v)} aria-label="basic tabs example">
                            <Tab label="PDF Content" />
                            <Tab label="Images" />
                        </Tabs>
                    </Box>
                    <TabPanel value={selectedTab} index={0}>
                        <PDFDisplay pdfContent={pdfSource} processedData={processedData} page={page} setPage={setPage} style={{margin:5}} scale={1}/>
                    </TabPanel>
                    <TabPanel value={selectedTab} index={1}>
                    <ImageList sx={{ width: 500, height: 450 }} cols={3} rowHeight={164}>
                        {imageData.filter(i => i.id === processedData.source?.statblocks[selected]?.image?.ref).map((image,i) => (
                                <ImageListItem key={`image-${image.page}-${i}`}>
                                <B64Image
                                    image_data={image.data}
                                    alt={`Image ${image.page}-${i}`}
                                    width={240}
                                />
                                </ImageListItem>
                        ))
                        }
                        </ImageList>
                        <ImageList sx={{ width: 500, height: 450 }} cols={3} rowHeight={164}>
                        {imageData.map((image,i) => (
                                <ImageListItem key={`image-${image.page}-${i}`}>
                                <B64Image
                                    image_data={image.data}
                                    alt={`Image ${image.page}-${image.id}`}
                                    width={240}
                                />
                                <ImageListItemBar
                                    title={image.id}
                                    subtitle={image.page}
                                />
                                </ImageListItem>
                        ))
                        }
                        </ImageList>
                    </TabPanel>
                </Paper>
                </Grid></>  : <></>} 
            </Grid>
        </Grid>
    )
}