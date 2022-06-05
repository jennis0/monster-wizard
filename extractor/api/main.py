from typing import Union, List, Any
from fastapi import FastAPI, Response, UploadFile, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import uuid
import json

from ..data_loaders.textract_image_loader import TextractImageLoader
from ..data_loaders.pdf_loader import PDFLoader
from ..core.constants import ACTION_TYPES
from ..core.creature import Creature
from ..core.extractor import StatblockExtractor
from ..outputs.default_writer import DefaultWriter
from ..outputs.print_writer import PrintWriter
from ..outputs.fvtt_writer import FVTTWriter

from ..utils.config import get_config, get_api_argparser
from ..utils.datatypes import Bound, Line, Section, Source
from ..utils.logger import get_logger


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

@app.post("/process/")
async def parse_file(
    background_tasks: BackgroundTasks,
    files:List[UploadFile], 
    uuid: str = Form(""),
    extract_images: bool = Form(True),
    source: Any = Form(None),
    pages: List[Any] = Form([])
):
    pages = [json.loads(p) for p in pages]
    source = json.loads(source)

    if not pages:
        pages = [None for f in files]
    for i in range(len(pages)):
        if pages[i] and len(pages[i]) == 0:
            pages[i] = None

    request_id = uuid
    CURRENT_JOBS[request_id] = {
            "id":request_id, 
            "state":StatblockExtractor.JobState.file_upload, 
            "metadata": {"extract_images":extract_images},
            "files": [f.file for f in files],
            "filenames":[f.filename for f in files],
            "meta":source,
            "sources":{},
            "pages":pages, 
            "file_progress":[0, len(files)],
            "progress":[0,1], 
            "errors":{f.filename:[] for f in files}
        }

    background_tasks.add_task(handle_parse_files, request_id)
    return response(**CURRENT_JOBS[request_id])

def response(id, state, progress, file_progress, errors={}, sources={}, version=1, **kwargs):
    print(errors[list(errors.keys())[0]])
    return {
        "request_id":id, 
        "status":state.name,
        "progress":progress,
        "file_progress":file_progress,
        "errors":errors,
        "sources": [sources[s].serialise() for s in sources],
        "version":version
    }


@app.get("/process/")
async def return_request(id:str):

    if id not in CURRENT_JOBS:
        return JSONResponse(response(id=id, 
                            state=StatblockExtractor.JobState.error, 
                            progress=[1,1],
                            file_progress=[0,0],
                            errors={"api":"Request ID not found"}
                        ), 404)

    state = CURRENT_JOBS[id]

    if state["state"] == StatblockExtractor.JobState.error:
        return JSONResponse(response(**state), 500)

    return response(**state)


def handle_parse_files(id):
    file_count = 0
    state = CURRENT_JOBS[id]

    for file,filename, pages in zip(state["files"], state["filenames"], state["pages"]):
        state["file_progress"] = [file_count+1, len(state["files"])]
        file_count += 1
        try:
            state = CURRENT_JOBS[id]
            extractor.select_writer(DefaultWriter.get_name())

            state["state"] = StatblockExtractor.JobState.text_extraction
            source, errors = extractor.parse(file, filename, "pdf", state=state, 
                        pages=pages, extract_images=state["metadata"]["extract_images"])

            state["sources"][filename] = source

            if source and source.statblocks == None:
                state["state"] = StatblockExtractor.JobState.error
                state["errors"][filename].append("Did not find any statblocks")
                return

        except:
            state["state"] = StatblockExtractor.JobState.error
            state["errors"][filename].append("Unexpected failure in API")

    if file_count > 1:
        merged_source = Source.merge([state["sources"][s] for s in state["sources"]])
        if state["meta"]["title"]:
            merged_source.name = state["meta"]["title"]
        if state["meta"]["author"]:
            merged_source.name = state["meta"]["author"]
        state["sources"] = {merged_source.name: merged_source}

    state["state"] = StatblockExtractor.JobState.finished

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
    error = None
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
            print(cr.data[request.action_type])
    except Exception as e:
        error = [e]
        print(e)

    return {"result":result, "error":error}

class ConvertRequest(BaseModel):
    type:str
    title: str
    statblocks: Any

@app.post("/convert/")
def convert(request: ConvertRequest):
    if (request.type == "fvtt"):
        writer = FVTTWriter(extractor.config, extractor.logger)

        source = Source(
            request.title,
            request.title,
            len(request.statblocks),
            [],[],[],
            request.statblocks,
            [],[],[]
            )
        result = writer.writes(source, request.statblocks)

        return Response(content=json.dumps(result), status_code=200, headers={
            'Content-Type': 'application/octet-stream; charset=utf-8',
            'Content-Disposition': 'attachment; filename="filename.jpg"; filename*="filename.jpg"',
        })
