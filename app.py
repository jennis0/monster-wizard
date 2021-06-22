
from extractor import StatblockExtractor
from utils.config import get_config, get_argparser
from utils.logger import get_logger

from data_loaders.textract_image_loader import TextractImageLoader



# Get arguments
parser = get_argparser()
args = parser.parse_args()

# Get config file
config = get_config(args.config)

# Setup logger
logger = get_logger(args.debug, args.logs)

### Load 
se = StatblockExtractor(config, logger)
se.register_data_loader(TextractImageLoader)

### Load 
parsed_statblocks = []
for target in args.targets:
    print("i")
    se.load_data(target)
    print(se.parse())


        

    