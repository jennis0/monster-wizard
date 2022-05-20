from enum import Enum, auto
import json
from fastapi import FastAPI, Request, UploadFile, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid

from data_loaders.pdf_loader import PDFLoader
from outputs.default_writer import DefaultWriter
from outputs.print_writer import PrintWriter
from outputs.fvtt_writer import FVTTWriter

from utils.config import get_config, get_argparser
from utils.logger import get_logger

from data_loaders.textract_image_loader import TextractImageLoader
from data_loaders.pdf_loader import PDFLoader

from extractor.extractor import StatblockExtractor

def create_configured_extractor(args):
    # Get config file
    config = get_config(args)

    # Setup logger
    logger = get_logger(args.debug, args.logs)

    ### Create Extractor
    se = StatblockExtractor(config, logger)

    ### Register Input formats
    se.register_data_loader(TextractImageLoader)
    se.register_data_loader(PDFLoader)

    ### Register Output formats and select one
    se.register_output_writer(DefaultWriter, append=not args.overwrite)
    se.register_output_writer(PrintWriter, append=not args.overwrite)
    se.register_output_writer(FVTTWriter, append=not args.overwrite)
    output = True
    if args.format:
        if args.format == 'none':
            output = False
        else:
            se.select_writer(args.format)
    else:
        se.select_writer(FVTTWriter.get_name())

    return se     



app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8000/process/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = get_argparser()
args = parser.parse_args()
args.logs="logs\logs.txt"
extractor = create_configured_extractor(args)

CURRENT_JOBS = {}

class JobState(Enum):
    file_upload = auto()
    text_extraction = auto()
    parsing = auto()
    finished = auto()
    error = auto()

@app.get("/")
async def read_root():
    return {"Hello":"World"}

@app.post("/process/")
async def parse_file(file: UploadFile, request: Request, background_tasks: BackgroundTasks):

    job_id = str(uuid.uuid4())
    CURRENT_JOBS[job_id] = {"id":job_id, "state":JobState.file_upload, "file":file.file, "filename":file.filename, "text":None, "statblocks":None, "source":None, "progress":[-1,-1], "errors":[]}

    background_tasks.add_task(handle_parse_file, job_id)

    return {"id":job_id, "state":JobState.file_upload.name}

@app.get("/process/")
async def return_request(id:str):
    if id not in CURRENT_JOBS:
        raise HTTPException(404, "Job id not found")

    state = CURRENT_JOBS[id]
    if state["state"] == JobState.finished:
        result = {"id":id, "state":JobState.finished.name, "statblocks":state["statblocks"], 
                    "text":state["text"], "errors":state["errors"], 
                    "frontpage":state["source"].page_images[0], 
                    "images":state["source"].images, "version":1}
        return result

    return {"id":id, "state":state["state"].name, "progress":state["progress"], "errors":[]}


def handle_parse_file(id):
    try:
        state = CURRENT_JOBS[id]
        extractor.select_writer(DefaultWriter.get_name())

        state["state"] = JobState.text_extraction

        statblock_text,source = extractor.file_to_statblocks(state["file"], state["filename"], "pdf")

        if statblock_text == None:
            state["state"] = JobState.error
            return
        state["text"] = [st.to_tuple() for st in statblock_text]
        state["source"] = source
        state["state"] = JobState.parsing

        statblocks,errors = extractor.statblocks_to_creatures(source, statblock_text, state)
        state["errors"] += errors
        if statblocks == None:
            state["state"] = JobState.error
            return

        state["statblocks"] = [s.to_json() for s in statblocks]
        state["state"] = JobState.finished
    except Exception as e:
        state["state"] = JobState.error
        state["errors"].append(["overall",e])
        print(e)