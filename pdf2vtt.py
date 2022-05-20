import os

from data_loaders.pdf_loader import PDFLoader
from outputs.pluto_writer import PlutoWriter
from outputs.default_writer import DefaultWriter
from outputs.print_writer import PrintWriter
from outputs.fvtt_writer import FVTTWriter

from utils.config import get_config, get_argparser
from utils.logger import get_logger

from data_loaders.textract_image_loader import TextractImageLoader
from data_loaders.pdf_loader import PDFLoader

from extractor.extractor import StatblockExtractor
from outputs.creature_printer import pretty_format_creature



# Get arguments
parser = get_argparser()
args = parser.parse_args()

# Get config file
config = get_config(args)

if not config.has_section("source"):
    config.add_section("source")
if args.authors:
    authors = []
    for a in args.authors:
        authors += [v.strip() for v in a.split(",")]
    config.set("source", "authors", ",".join(authors))
if args.url:
    config.set("source", "url", args.url)
if args.source:
    config.set("source", "title", args.source)


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

### Run over provided targets 
parsed_statblocks = []
logger.info("Loading creatures from {}".format(args.target))

if args.pages:
    pages = [int(p) for p in args.pages.split(",")]
else:
    pages = None

results = se.parse(args.target, pages=pages)
if not results:
    exit()

p_func = print

for source_name in parsed_statblocks:
    source, creatures, statblocks, errors = parsed_statblocks[source_name]
    p_func("Found {} statblocks in {}".format(len(creatures), source.name))

    if output:
        if args.output:
            outfile = args.output
        else:
            outfile = "{}.{}".format(os.path.basename(source.name).split('.')[0], se.writer.get_filetype())

        se.write_to_file(outfile, source, {0:creatures})

    if args.print:
        for creature in ps:
            p_func("\n" + pretty_format_creature(creature) + "\n")


        

    