from typing import Union
from fastapi import FastAPI, Request, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
from datetime import datetime

from data_loaders.pdf_loader import PDFLoader
from extractor.constants import ACTION_TYPES
from extractor.creature import Creature
from outputs.default_writer import DefaultWriter
from outputs.print_writer import PrintWriter
from outputs.fvtt_writer import FVTTWriter

from utils.config import get_config, get_api_argparser
from utils.datatypes import Bound, Line, Section
from utils.logger import get_logger

from data_loaders.textract_image_loader import TextractImageLoader
from data_loaders.pdf_loader import PDFLoader

from extractor.extractor import StatblockExtractor

def create_configured_extractor(args):
    # Get config file
    config = get_config(args, cli=False)

    # Setup logger
    logger = get_logger(args.debug, args.logs)

    ### Create Extractor
    se = StatblockExtractor(config, logger)

    ### Register Input formats
    se.register_data_loader(TextractImageLoader)
    se.register_data_loader(PDFLoader)

    ### Register Output formats and select one
    se.register_output_writer(DefaultWriter, append=False)
    se.register_output_writer(PrintWriter, append=False)
    se.register_output_writer(FVTTWriter, append=False)

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

parser = get_api_argparser()
cli = ["--logs", f"logs\logs-{datetime.now().strftime('%y%m%d_%H%M%S')}.txt", "--debug"]
args = parser.parse_args(cli)
extractor = create_configured_extractor(args)

CURRENT_JOBS = {}

@app.get("/")
async def read_root():
    return {"Hello":"World"}

@app.post("/process/")
async def parse_file(file: UploadFile, request: Request, background_tasks: BackgroundTasks):

    job_id = str(uuid.uuid4())
    CURRENT_JOBS[job_id] = {
            "id":job_id, 
            "state":StatblockExtractor.JobState.file_upload, 
            "file":file.file, "filename":file.filename,
            "source":None, 
            "progress":[-1,1], 
            "errors":[]
        }

    background_tasks.add_task(handle_parse_file, job_id)

    return response(**CURRENT_JOBS[job_id])

def response(id, state, progress=[-1,1], errors=[], source={}, version=1, **kwargs):
    return {
        "id":id, 
        "state":state.name,
        "progress":progress,
        "errors":errors,
        "source": source.serialise() if source else {},
        "version":version
    }


@app.get("/process/")
async def return_request(id:str):

    if id not in CURRENT_JOBS:
        return JSONResponse(response(id=id, state=StatblockExtractor.JobState.error, errors=["Id not found"]), 404)

    state = CURRENT_JOBS[id]

    if state["state"] == StatblockExtractor.JobState.error:
        return JSONResponse(response(**state), 500)

    return response(**state)


def handle_parse_file(id):
    try:
        state = CURRENT_JOBS[id]
        extractor.select_writer(DefaultWriter.get_name())

        state["state"] = StatblockExtractor.JobState.text_extraction
        source, errors = extractor.parse(state["file"], state["filename"], "pdf", state=state)

        state["source"] = source
        state["errors"] = errors

        if source and source.statblocks == None:
            state["state"] = StatblockExtractor.JobState.error
            state["errors"].append("Did not find any statblocks")
            return

    except Exception as e:
        state["state"] = StatblockExtractor.JobState.error
        state["errors"].append(["Unexpected failure in API"])
        exit(1)

class ParseRequest(BaseModel):
    type: str
    title: str
    text: str
    action_type: Union[str, None] = None

@app.post("/parse/")
def parse_text(request: ParseRequest):
    cr = Creature(extractor.config, extractor.logger.getChild("parse_request"))
    cr.set_name("tmp")
    lines = [Line(text=request.title + ". " + request.text, bound=Bound(0,0,1,1), page=0, attributes=[], id="1")]
    print(lines)
    try:
        s = Section(lines=lines)
        print(s)
        if request.type == "feature":
            print(s)
            cr.add_feature(s)
            result = cr.data["features"][0]
            print(result)
        else:
            if request.action_type not in ACTION_TYPES._member_map_:
                return JSONResponse({"result":None, "error":"Unknown action type"}, 500)
            cr.add_action(s, action_type=ACTION_TYPES._member_map_[request.action_type])
            result = cr.data[request.action_type][0]
    except:
        print(e)

    return {"result":result, "error":None}
