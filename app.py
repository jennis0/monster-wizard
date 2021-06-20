
from extractor import StatblockExtractor
from config import get_config
import argparse

import logging
import sys

from data_loaders.textract_image_loader import TextractImageLoader

def create_argparse() -> argparse.ArgumentParser:
    '''Creates command line argument parser to control the app'''

    parser = argparse.ArgumentParser(
        description="Extract 5e statblocks from images and PDFs"
    )
    parser.add_argument("targets", type=str, nargs='+', help="Images or PDFs to search for monster statblocks")
    parser.add_argument("--source", "-s", type=str, help="A source label for the statblocks processed")
    parser.add_argument("--output", "-o", type=str, help="Output JSON file containing statblocks")
    parser.add_argument("--cache", "-C", type=str, default=".cache", help="Local cache to store API responses")
    parser.add_argument("--config", "-c", type=str, default="default.conf", help="Configuration file for controlling parser")
    parser.add_argument("--logs", "-l", type=str, default=None, help="Optional output log file")
    parser.add_argument("--debug", action='store_true', help="Print debug logging")
    return parser

# Get arguments
parser = create_argparse()
args = parser.parse_args()

# Get config file
config = get_config(args.config)

# Setup logger
log_formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')
log_level = logging.DEBUG if args.debug else logging.INFO

logger = logging.getLogger('sbp')
logger.setLevel(log_level)
logger.addHandler(logging.StreamHandler(sys.stdout))
if args.logs:
    logger.addHandler(logging.FileHandler(args.logs))
for handler in logger.handlers:
    handler.setFormatter(log_formatter)

### Load 
parsed_statblocks = []
for target in args.targets:
    if target.endswith(".png"):
        #Handle sending image to Textract
        loader = TextractImageLoader(config, logger)
        lines = loader.image_to_lines(target)

    