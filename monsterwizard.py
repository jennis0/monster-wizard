
from data_loaders.pdf_loader import PDFLoader
from outputs.pluto_writer import PlutoWriter
from outputs.default_writer import DefaultWriter

from utils.config import get_config, get_argparser
from utils.logger import get_logger

from data_loaders.textract_image_loader import TextractImageLoader
from data_loaders.pdf_loader import PDFLoader

from extractor.extractor import StatblockExtractor
from extractor.creature_printer import pretty_format_creature



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
se.register_output_writer(PlutoWriter, append=not args.overwrite)
if args.output_format:
    se.select_writer(args.output_format)
else:
    se.select_writer(DefaultWriter.get_name())

### Run over provided targets 
parsed_statblocks = []
logger.info("Loading creatures from {}".format(args.target))

if args.pages:
    pages = [int(p) for p in args.pages.split(",")]
else:
    pages = None

results = se.parse(args.target, args.output, pages=pages)
if not results:
    exit()
parsed_statblocks, statblocks = results

num_pages = len(parsed_statblocks.keys())
logger.info("Found {} page{} of statblocks".format(num_pages, 's' if num_pages > 1 else ''))

if num_pages < 5:
    print("\n")
    for page in parsed_statblocks:
        print("Page {}:".format(page))
        for creature in parsed_statblocks[page]:
            print()
            print(pretty_format_creature(creature))
            print()


        

    