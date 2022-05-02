from fastapi import FastAPI, UploadFile
import json

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
parser = get_argparser()
args = parser.parse_args()
args.logs="logs\logs.txt"
extractor = create_configured_extractor(args)



@app.get("/")
async def read_root():
    return {"Hello":"World"}

@app.post("/process_file/")
async def parse_file(file: UploadFile):
    extractor.select_writer(DefaultWriter.get_name())

    statblock_text,source = extractor.file_to_statblocks(file.file, file.filename, "pdf")
    statblocks = extractor.statblocks_to_creatures(source, statblock_text)
    json_statblocks = extractor.writer.write_to_json(source, statblocks)

    return {"file": file.filename, "statblock_text":[s.to_tuple() for s in statblock_text], "statblocks": json_statblocks}