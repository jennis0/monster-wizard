
from outputs.default_writer import DefaultWriter
from extractor import StatblockExtractor
from utils.config import get_config, get_argparser
from utils.logger import get_logger

from data_loaders.textract_image_loader import TextractImageLoader

from fifthedition.creature_printer import pretty_format_creature
from fifthedition.creature_parser import CreatureParser



# Get arguments
parser = get_argparser()
args = parser.parse_args()

# Get config file
config = get_config(args.config)

if not config.has_section("source"):
    config.add_section("source")
if args.author:
    config.set("source", "author", args.author)
if args.url:
    config.set("source", "url", args.url)
if args.source:
    config.set("source", "title", args.source)


# Setup logger
logger = get_logger(args.debug, args.logs)

### Load 
se = StatblockExtractor(config, logger)
se.register_data_loader(TextractImageLoader)
se.register_output_writer(DefaultWriter, append=True)
se.select_writer(DefaultWriter.get_name())
cp = CreatureParser(config, logger)

### Output writer

### Load 
parsed_statblocks = []
for target in args.targets:
    logger.info("Loading creatures from {}".format(target))
    
    results = se.parse(target, args.output)
    if not results:
        exit()
    parsed_statblocks, statblocks = results

    num_pages = len(statblocks.keys())
    logger.info("Found {} page{} of statblocks".format(num_pages, 's' if num_pages > 1 else ''))
    
    for page in parsed_statblocks:
        print("Page {}:".format(page))
        for creature in parsed_statblocks[page]:
            print()
            print(pretty_format_creature(creature))
            print()


        

    