import logging
import os
from pathlib import Path

def get_logger(debug: bool, log_path: str=None) -> logging.Logger:
    '''Helper function to create a standardised logger'''

    log_formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s %(name)-16s %(message)s')
    log_level = logging.DEBUG if debug else logging.INFO

    logger = logging.getLogger('sbp')
    logger.setLevel(log_level)

    ## Ensure we don't double handlers in a notebook environment
    for hdl in logger.handlers:
        logger.removeHandler(hdl)
        
    if log_path:
        os.makedirs(Path(log_path).parent.absolute(), exist_ok=True)
        logger.addHandler(logging.FileHandler(log_path, encoding='utf-8'))

    for handler in logger.handlers:
        handler.setFormatter(log_formatter)

    return logger